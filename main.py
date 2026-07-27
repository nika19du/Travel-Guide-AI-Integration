from pathlib import Path

from console import print_ai_result
from rag_service import ask_ai
from vector_store import VectorStoreManager

DB_PATH = "./chroma_db"
GUIDES_DIRECTORY = "./travel_guides"


def index_guides_if_needed(
    vector_store: VectorStoreManager
):
    """
    Indexes the PDF files only when the ChromaDB
    collection is empty.
    """

    existing_chunks = vector_store.count_chunks()

    if existing_chunks > 0:
        print(
            f"Vector store already contains "
            f"{existing_chunks} chunks."
        )
        return

    guides_directory = Path(GUIDES_DIRECTORY)

    if not guides_directory.exists():
        raise FileNotFoundError(
            f"Travel guide directory does not exist: "
            f"{guides_directory.resolve()}"
        )

    pdf_files = sorted(
        guides_directory.glob("*.pdf")
    )

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files were found in: "
            f"{guides_directory.resolve()}"
        )

    print(
        f"Found {len(pdf_files)} PDF guide(s)."
    )

    for pdf_file in pdf_files:
        vector_store.add_pdf(
            str(pdf_file)
        )

    print(
        f"Total indexed chunks: "
        f"{vector_store.count_chunks()}"
    )


def run_cli(vector_store: VectorStoreManager):
    print(
        "\nTravel Guide AI Assistant"
    )
    print(
        "Type 'exit' or 'quit' to close the application."
    )

    while True:
        question = input(
            "\nAsk a travel question: "
        ).strip()

        if question.lower() in {
            "exit",
            "quit"
        }:
            print("Goodbye!")
            break

        if not question:
            print(
                "Please enter a question."
            )
            continue

        try:
            result = ask_ai(
                question=question,
                vector_store=vector_store
            )

            print_ai_result(result)

        except Exception as error:
            print(
                f"\nError: {error}"
            )


def main():

    vector_store = VectorStoreManager(
        db_path=DB_PATH,
        collection_name="travel_guides",
        embedding_model="text-embedding-3-small"
    )

    index_guides_if_needed(
        vector_store
    )

    available_guides = (
        vector_store.list_available_guides()
    )

    print("\nAvailable guides:")

    for guide in available_guides:
        print(f"- {guide}")

    run_cli(
        vector_store=vector_store
    )


if __name__ == "__main__":
    main()