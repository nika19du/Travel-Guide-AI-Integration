import json
from typing import Type, TypeVar

from pydantic import BaseModel

from config import client
from models import (
    AskAIResult,
    IntentAnalysis,
    TravelGuideAnswer
)
from prompts import (
    INTENT_SYSTEM_PROMPT,
    RETRIEVAL_SYSTEM_PROMPT
)
from tools import (
    TRAVEL_GUIDE_TOOLS,
    execute_tool
)
from vector_store import VectorStoreManager

T = TypeVar("T", bound=BaseModel)

DEBUG = True
MAX_TOOL_ITERATIONS = 8


def generate_structured_response(
    instructions: str,
    user_input: str,
    response_model: Type[T]
) -> T:
    """
    Sends a request to the model and parses the response
    directly into the supplied Pydantic model.

    This is currently used for intent analysis.
    """

    response = client.responses.parse(
        model="gpt-4o-mini",
        instructions=instructions,
        input=user_input,
        text_format=response_model
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
    """
    Uses Responses API tool calling.

    The model decides:
    - whether guide search is needed;
    - which search query to use;
    - whether to filter by a destination;
    - how many chunks to retrieve;
    - whether to perform more than one search.

    The final response is parsed into TravelGuideAnswer.
    """

    instructions = (
        f"{RETRIEVAL_SYSTEM_PROMPT}\n\n"
        "You have access to indexed PDF travel guides.\n\n"
        "Available destinations:\n"
        "- Prague\n"
        "- Malaga\n\n"
        "Tool usage rules:\n"
        "1. If the question mentions Prague, call search_travel_guides "
        "with destination='Prague'.\n"
        "2. If the question mentions Malaga, call search_travel_guides "
        "with destination='Malaga'.\n"
        "3. If the user explicitly asks to compare Prague and Malaga, "
        "perform a separate search for each destination.\n"
        "4. Do not search an unrequested destination.\n"
        "5. Use list_available_guides only when you need to discover "
        "which guides are available.\n"
        "6. Base the answer only on retrieved chunks.\n"
        "7. For search_travel_guides, use top_k=5 by default "
        "and never use a value lower than 3.\n"
    )

    response = client.responses.parse(
        model = "gpt-4o-mini",
        instructions = instructions,
        input = prompt,
        tools = TRAVEL_GUIDE_TOOLS,
        text_format = TravelGuideAnswer
    )

    for iteration in range(MAX_TOOL_ITERATIONS):
        function_calls = [
            output_item
            for output_item in response.output
            if output_item.type == "function_call"
        ]

        # No tool calls means the model has produced its final answer.
        if not function_calls:
            parsed_answer = response.output_parsed

            if parsed_answer is None:
                raise ValueError(
                    "The model did not return a valid "
                    "TravelGuideAnswer."
                )

            invalid_destinations = {
                "comparison",
                "summary",
                "overall"
            }

            parsed_answer.destinations = [
                destination
                for destination in parsed_answer.destinations
                if destination.destination.strip().lower()
                not in invalid_destinations
            ]

            return parsed_answer

        tool_outputs = []

        for function_call in function_calls:
            if DEBUG:
                print(
                    f"\nTool call: {function_call.name}"
                )
                print(
                    f"Arguments: {function_call.arguments}"
                )

            tool_result = run_function_call(
                function_call=function_call,
                vector_store=vector_store
            )

            if DEBUG:
                print("Tool result:")
                print(
                    json.dumps(
                        tool_result,
                        indent=2,
                        ensure_ascii=False
                    )
                )

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": function_call.call_id,
                "output": json.dumps(
                    tool_result,
                    ensure_ascii=False
                )
            })

        # Send the locally executed tool results back to the model.
        response = client.responses.parse(
            model = "gpt-4o-mini",
            instructions = instructions,
            previous_response_id = response.id,
            input = tool_outputs,
            tools = TRAVEL_GUIDE_TOOLS,
            text_format = TravelGuideAnswer
        )

    raise RuntimeError(
        "The maximum number of tool-call iterations "
        "was exceeded."
    )


def run_function_call(
    function_call,
    vector_store: VectorStoreManager
):
    """
    Converts the JSON tool arguments into a Python dictionary
    and executes the requested local function.
    """

    try:
        arguments = json.loads(function_call.arguments)
    except json.JSONDecodeError as error:
        return {
            "success": False,
            "error": "Invalid tool arguments.",
            "details": str(error)
        }

    try:
        return execute_tool(
            vector_store=vector_store,
            tool_name=function_call.name,
            arguments=arguments
        )
    except Exception as error:
        return {
            "success": False,
            "error": (
                f"Tool '{function_call.name}' failed."
            ),
            "details": str(error)
        }


def ask_ai(
    question: str,
    vector_store: VectorStoreManager
) -> AskAIResult:
    print(
        "\n"
        "--------------------------------------------------"
    )
    print(f'User Question: "{question}"')

    if not question or not question.strip():
        raise ValueError(
            "The user question cannot be empty."
        )

    # Step 1:
    # Analyze the user's original question.
    parsed_intent = generate_structured_response(
        instructions=INTENT_SYSTEM_PROMPT,
        user_input=question.strip(),
        response_model=IntentAnalysis
    )

    extracted_prompt = parsed_intent.prompt
    requested_format = parsed_intent.format

    print(f'Extracted Prompt: "{extracted_prompt}"')
    print(
        f'Detected Format: '
        f'"{requested_format.upper()}"'
    )

    # Step 2:
    # Let the model choose and execute the retrieval tools.
    travel_answer = retrieve_information(
        prompt=extracted_prompt,
        vector_store=vector_store
    )

    return AskAIResult(
        intent=parsed_intent,
        answer=travel_answer
    )