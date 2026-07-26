from config import client
from formatters import format_travel_answer_as_markdown
from models import (
    AskAIResult,
    IntentAnalysis,
    TravelGuideAnswer
)
from prompts import (
    INTENT_SYSTEM_PROMPT,
    RETRIEVAL_SYSTEM_PROMPT
)
from vector_store import VectorStoreManager
from typing import TypeVar, Type
from pydantic import BaseModel
T = TypeVar("T", bound=BaseModel)
from console import print_travel_answer

DEBUG = False

# Sends a request to the LLM and parses the response directly
# into the specified Pydantic model using Structured Outputs.
# This helper is reused for both:
# 1. Intent analysis (understanding the user request)
# 2. Retrieval answer generation (creating the final answer
#    from the retrieved PDF context)

def generate_structured_response(
    instructions: str,
    user_input: str,
    response_model: Type[T]
) -> T:
    response = client.responses.parse(
        model = "gpt-4o-mini",
        instructions = instructions,
        input = user_input,
        text_format = response_model
    )

    parsed_result = response.output_parsed

    if parsed_result is None:
        raise ValueError(
            f"The model did not return a valid "
            f"{response_model.__name__} response."
        )

    return parsed_result

def retrieve_information(
    prompt: str,
    vector_store: VectorStoreManager
) -> TravelGuideAnswer:
    # search_requests queries are converted into embeddings and used
    # by ChromaDB to retrieve the most semantically relevant chunks.
    # The LLM is NOT involved in this step.
    search_requests =[
        {
            "query": prompt,
            "source": None,
            "top_k": 3
        },
        {
            "query": "Prague best time to visit and best weather",
            "source": "prague_tour_guide.pdf",
            "top_k": 2
        },
        {
            "query": (
                "Prague cheapest time to visit, "
                "lower flight and accommodation prices"
            ),
            "source": "prague_tour_guide.pdf",
            "top_k": 2
        },
        {
            "query": (
                "Malaga best time for beach life, "
                "sightseeing and excursions"
            ),
            "source": "malaga_tour_guide.pdf",
            "top_k": 2
        },
        {
            "query": (
                "Malaga cheapest time, fair prices, "
                "shoulder seasons and most economical period"
            ),
            "source": "malaga_tour_guide.pdf",
            "top_k": 2
        }
    ]

    retrieved_chunks = []

    for request in search_requests:
        # IMPORTANT:
        # Embeddings are used only for sematic search.
        # The LLM never receives embedding vectors.
        # ChromaDB returns the original text chunks, which are
        # then provided to the model as context
        results = vector_store.search(
            query=request["query"],
            top_k=request["top_k"],
            source=request["source"]
        )

        retrieved_chunks.extend(results)

    unique_chunks_by_id = {}

    for chunk in retrieved_chunks:
        existing = unique_chunks_by_id.get(chunk["id"])

        if existing is None or chunk["distance"] < existing["distance"]:
            unique_chunks_by_id[chunk["id"]] = chunk

    unique_chunks = sorted(
        unique_chunks_by_id.values(),
        key=lambda chunk: chunk["distance"],
    )

    # The retrieved chunks are converted back into plain text.
    # This text becomes the context that will be sent to the LLM.
    context = "\n\n".join(
        (
            f"[Source File: {chunk['source']}, "
            f"Page: {chunk['page']}]\n"
            f"{chunk['text']}"
        )
        for chunk in unique_chunks
    )


    if DEBUG:
        for index, chunk in enumerate(unique_chunks, start=1):
            print(f"\n--- Retrieved chunk {index} ---")
            print(
                f"Source: {chunk['source']}, "
                f"Page: {chunk['page']}, "
                f"Distance: {chunk['distance']:.4f}"
            )
            print(chunk["text"])

    # Step 2:
    # The model now receives:
    # - the retrieved PDF text (context)
    # - the original user question
    # - instructions describing how the final answer should be structured
    # The model never sees the embeddings !!!
    # It only reads the retrieved text chunks!
    parsed_answer = generate_structured_response(
        instructions = RETRIEVAL_SYSTEM_PROMPT,
        user_input = (
            f"Retrieved PDF context:\n\n{context}\n\n"
            f"Question:\n\n{prompt}"
        ),
        response_model = TravelGuideAnswer
    )

    return parsed_answer


def ask_ai(
    question: str,
    vector_store: VectorStoreManager
) -> AskAIResult:
    print("\n--------------------------------------------------")
    print(f'User Question: "{question}"')

    # Step 1:
    # The model analyzes the user question only.
    # It does Not have access to the PDF documents yet.
    # Its job is to extract a clean retrieval prompt
    # and determine the desired output format.

    parsed_intent = generate_structured_response(
        instructions = INTENT_SYSTEM_PROMPT,
        user_input = question,
        response_model = IntentAnalysis
    )

    extracted_prompt = parsed_intent.prompt
    requested_format = parsed_intent.format

    print(f'Extracted Prompt: "{extracted_prompt}"')
    print(f'Detected Format: "{requested_format.upper()}"')

    travel_answer = retrieve_information(
        prompt=parsed_intent.prompt,
        vector_store=vector_store
    )

    if parsed_intent.format == "text":
        print_travel_answer(travel_answer)
        markdown_answer = format_travel_answer_as_markdown(
            travel_answer
        )
    #elif parsed_intent.format == "audio":
        # formatted_answer = generate_audio_answer(
        #    travel_answer
        #)
    #elif parsed_intent.format == "image":
        #formatted_answer = generate_image_answer(
        #    travel_answer
        #)
    #else:
        #raise ValueError(
            #f"Unsupported output format: {parsed_intent.format}"
        #)

    return AskAIResult(
        intent=parsed_intent,
        answer=travel_answer
    )