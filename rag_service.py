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

def parse_structured_response(
    system_prompt: str,
    user_prompt: str,
    response_model: Type[T]
) -> T:
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        response_format=response_model,
        temperature=0
    )

    parsed_result = response.choices[0].message.parsed

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

    context = "\n\n".join(
        (
            f"[Source File: {chunk['source']}, "
            f"Page: {chunk['page']}]\n"
            f"{chunk['text']}"
        )
        for chunk in unique_chunks
    )


    for index, chunk in enumerate(unique_chunks, start=1):
        print(f"\n--- Retrieved chunk {index} ---")
        print(
            f"Source: {chunk['source']}, "
            f"Page: {chunk['page']}, "
            f"Distance: {chunk['distance']:.4f}"
        )
        print(chunk["text"])

    parsed_answer = parse_structured_response(
        system_prompt=RETRIEVAL_SYSTEM_PROMPT,
        user_prompt=(
            f"Retrieved PDF context:\n\n{context}\n\n"
            f"Question:\n\n{prompt}"
        ),
        response_model=TravelGuideAnswer
    )

    if parsed_answer is None:
        raise Exception("The model did not return a valid structured answer.")

    return parsed_answer

def ask_ai(
    question: str,
    vector_store: VectorStoreManager
) -> AskAIResult:
    print("\n--------------------------------------------------")
    print(f'User Question: "{question}"')

    parsed_intent = parse_structured_response(
        system_prompt=INTENT_SYSTEM_PROMPT,
        user_prompt=question,
        response_model=IntentAnalysis
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
        markdown_answer = format_travel_answer_as_markdown(
            travel_answer
        )

        print("\n" + markdown_answer)

    return AskAIResult(
        intent=parsed_intent,
        answer=travel_answer
    )