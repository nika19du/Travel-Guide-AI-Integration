from pydantic import BaseModel, ConfigDict, Field
from vector_store import VectorStoreManager

SOURCE_MAPPING = {
    "Prague": "prague_tour_guide.pdf",
    "Malaga": "malaga_tour_guide.pdf",
}

class SearchTravelGuidesParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        description=(
            "A concise semantic search query describing "
            "the requested information."
        )
    )
    destination: str | None = Field(
        description = (
            "Destination filter, for example Prague or Malaga. "
            "Use null when no destination filter is required."
        )
    )
    top_k: int = Field(
        ge = 3,
        le = 10,
        description=(
            "Number of retrieved chunks. Use 5 by default "
            "and never fewer than 3."
        )
    )

class ListAvailableTravelGuidesParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

TRAVEL_GUIDE_TOOLS = [
    {
        "type": "function",
        "name": "search_travel_guides",
        "description": (
            "Search the indexed travel guides for information "
            "about destinations, weather, prices, attractions, "
            "transport, accommodation and recommended travel periods."
        ),
        "parameters": SearchTravelGuidesParams.model_json_schema(),
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_available_guides",
        "description": (
            "List the destinations and travel guides "
            "available in the vector database."
        ),
        "parameters": ListAvailableTravelGuidesParams.model_json_schema(),
        "strict": True,
    },
]


def search_travel_guides(
    vector_store: VectorStoreManager,
    query: str,
    destination: str | None,
    top_k = 5
):
    """
    Search the indexed travel guides using semantic search.
    Args:
        vector_store: ChromaDB vector store.
        query: User search query.
        source: Optional PDF source filter.
        top_k: Maximum number of chunks to return.
    """

    source = SOURCE_MAPPING.get(destination)

    if destination is not None and source is None:
        return {
            "success": False,
            "error": f"No indexed guide found for {destination}"
        }

    safe_top_k = max(3, min(top_k, 10))

    results = vector_store.search(
        query = query,
        source = source,
        top_k = safe_top_k)

    return {
        "success": True,
        "data": {
            "query": query,
            "destination": destination,
            "source_filter": source,
            "result_count": len(results),
            "results": results
        }
    }


def list_available_guides(vector_store: VectorStoreManager):
    guides = vector_store.list_available_guides()

    return {
        "success": True,
        "data": {
            "guide_count": len(guides),
            "indexed_chunk_count": vector_store.count_chunks(),
            "guides": guides
        }
    }

def execute_tool(
    tool_name: str,
    arguments: dict,
    vector_store: VectorStoreManager
):
    if tool_name == "search_travel_guides":
        params = SearchTravelGuidesParams.model_validate(arguments)

        return search_travel_guides(
            vector_store = vector_store,
            query = params.query,
            destination = params.destination,
            top_k = params.top_k
        )

    if tool_name == "list_available_guides":
        ListAvailableTravelGuidesParams.model_validate(arguments)
        return list_available_guides(vector_store)

    raise ValueError(f"Tool '{tool_name}' not found.")