from pathlib import Path

import chromadb

from config import client
from pdf_utils import extract_pdf_pages, split_text


class VectorStoreManager:
    def __init__(
        self,
        db_path,
        collection_name: str = "travel_guides",
        embedding_model="text-embedding-3-small",
    ):
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.embedding_model = embedding_model

        self.chroma_client = chromadb.PersistentClient(
            path=str(self.db_path)
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name
        )

    def add_pdf(self, pdf_path: str) -> None:
        source = Path(pdf_path).name
        pages = extract_pdf_pages(pdf_path)

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for page_data in pages:
            page_number = page_data["page"]
            chunks = split_text(page_data["text"])

            for chunk_index, chunk in enumerate(chunks):
                chunk_id = (
                    f"{source}_page{page_number}_{chunk_index}"
                )

                embedding = self._create_embedding(chunk)

                ids.append(chunk_id)
                documents.append(chunk)
                embeddings.append(embedding)

                metadatas.append({
                    "source": source,
                    "page": page_number,
                    "chunk_index": chunk_index
                })

        if not ids:
            print(f"No chunks found in {source}.")
            return

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print(f"Indexed {source} ({len(ids)} chunks)")

    def count_chunks(self):
        return self.collection.count()

    def _create_embedding(self, text):
        response = client.embeddings.create(
            model=self.embedding_model,
            input=text
        )

        return response.data[0].embedding

    def search(
        self,
        query: str,
        source: str | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if top_k < 1:
            raise ValueError(
                "top_k must be greater than zero."
            )

        normalized_query = query.strip().lower()

        query_embedding = self._create_embedding(
            query.strip()
        )

        query_arguments = {
            "query_embeddings": [query_embedding],
            "n_results": max(top_k, 5),
            "include": [
                "documents",
                "metadatas",
                "distances"
            ]
        }

        if source is not None:
            query_arguments["where"] = {
                "source": source
            }

        results = self.collection.query(
            **query_arguments
        )

        chunks = []

        result_ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for chunk_id, document, metadata, distance in zip(
            result_ids,
            documents,
            metadatas,
            distances
        ):
            normalized_document = document.strip().lower()

            exact_heading_match = (
                normalized_document.startswith(normalized_query)
            )

            adjusted_distance = distance

            if exact_heading_match:
                adjusted_distance -= 1.0

            chunks.append({
                "id": chunk_id,
                "text": document,
                "source": metadata.get("source"),
                "page": metadata.get("page"),
                "chunk_index": metadata.get("chunk_index"),
                "distance": distance,
                "_adjusted_distance": adjusted_distance
            })

        chunks.sort(key = lambda chunk: chunk["_adjusted_distance"])

        selected_chunks = chunks[:top_k]

        for chunk in selected_chunks:
            chunk.pop("_adjusted_distance", None)

        return selected_chunks

    def list_available_guides(self):
        results = self.collection.get(
            include=["metadatas"]
        )

        metadatas = results.get("metadatas", [])

        sources = set()

        for metadata in metadatas:
            if not metadata:
                continue

            source = metadata.get("source")

            if source:
                sources.add(source)

        return sorted(sources)