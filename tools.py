from vector_store import VectorStoreManager

SOURCE_MAPPING = {
    "Prague": "prague_tour_guide.pdf",
    "Malaga": "malaga_tour_guide.pdf",
}

TRAVEL_GUIDE_TOOLS = [
    {
        "type": "function",
        "name": "search_travel_guides",
        "description": (
            "Search the indexed travel guides for information "
            "about destinations, weather, prices, attractions, "
            "transport, accommodation and recommended travel periods."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The information that should be searched for."
                    ),
                },
                "destination": {
                    "type": ["string", "null"],
                    "description": (
                        "Optional destination filter, "
                        "for example Prague or Malaga."
                    ),
                },
                "top_k": {
                    "type": "integer",
                    "description": (
                        "Maximum number of results."
                    ),
                    "minimum": 1,
                    "maximum": 10,
                },
            },
            "required": [
                "query",
                "destination",
                "top_k"
            ],
            "additionalProperties": False
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_available_guides",
        "description": (
            "List the destinations and travel guides "
            "available in the vector database."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True,
    },
]


def search_travel_guides(
    vector_store,
    query,
    source = None,
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

    results = vector_store.search(
        query = query,
        source = source,
        top_k=top_k)

    return {
        "query": query,
        "source_filter": source,
        "result_count": len(results),
        "results": results
    }


def list_available_guides(vector_store: VectorStoreManager):
    guides = vector_store.list_available_guides()

    return {
        "guide_count": len(guides),
        "indexed_chunk_count":vector_store.count_chunks(),
        "guides": guides
    }

def execute_tool(tool_name,arguments, vector_store):
    if tool_name == "search_travel_guides":
        destination = arguments.get("destination")
        source = SOURCE_MAPPING.get(destination)

        return search_travel_guides(
            vector_store = vector_store,
            query = arguments["query"],
            source = source,
            top_k = arguments.get("top_k", 5)
        )
    elif tool_name == "list_available_guides":
        return list_available_guides(vector_store = vector_store)

    raise ValueError(f"Unknown tool: {tool_name}")