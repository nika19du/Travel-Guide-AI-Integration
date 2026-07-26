from rag_service import ask_ai
from vector_store import VectorStoreManager


def main() -> None:
    vector_store = VectorStoreManager(
        collection_name="travel_guides"
    )

    # Индексиране на PDF файловете
    vector_store.add_pdf("data/prague_tour_guide.pdf")
    vector_store.add_pdf("data/malaga_tour_guide.pdf")

    question = (
        "What are the best and cheapest months to travel "
        "to Prague and Malaga according to the guides?"
    )

    result = ask_ai(
        question=question,
        vector_store=vector_store
    )

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(result.answer)

    print("\nJSON:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()