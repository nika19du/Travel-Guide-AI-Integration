from pathlib import  Path

import chromadb

from config import client
from pdf_utils import extract_pdf_pages, split_text

class VectorStoreManager:
    def __init__(
        self,
        collection_name: str="travel_guides",
        db_path: str = "chroma_db"
    ):
        self.chroma_client = chromadb.PersistentClient(
            path = db_path
        )

        self.collection = self.chroma_client.get_or_create_collection(name = collection_name)

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

                embedding = client.embeddings.create(
                    model="text-embedding-3-small",
                    input = chunk
                ).data[0].embedding

                ids.append(chunk_id)
                documents.append(chunk)
                embeddings.append(embedding)
                metadatas.append({
                    "source": source, # - source: the PDF filename
                    "page": page_number, # - page: the PDF page number
                    "chunk_index": chunk_index # - chunk_index: the chunk position within the page/document
                })

        self.collection.upsert(
            ids = ids,
            documents = documents,
            embeddings = embeddings,
            metadatas = metadatas
        )

        print(f"Indexed {source} ({len(ids)} chunks)")

    def search(
        self,
        query: str,
        top_k: int = 3,
        source: str | None = None
    ) -> list[dict]:

        # Convert the user search query into an embedding vector.
        # this vector captures the semantic meaning of the query.
        query_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input = query
        ).data[0].embedding

        # build the query parameters for ChromaDB.
        # Scratch by embedding similarity, not by keyword matching. (Cosine similarity)
        query_arguments = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include":[
                "documents",
                "metadatas",
                "distances"
            ]
        }

        # Optionally limit the search to a specific PDF.
        if source is not None:
            query_arguments["where"] = {
                "source": source
            }

        # Perform semantic search in ChromaDB.
        # Chroma compares the query embedding with the stored chunk
        # embeddings using cosine similarity and returns the most
        # relevant original text chunk.
        results = self.collection.query(**query_arguments) # **means dictionary unpacking

        chunks = []

        # ChromaDb returns separate lists for ids, documents,
        # metadata and distances. Zip combines them into
        # commplete chunk object
        for chunk_id, document, metadata, distance in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # convert the ChromaDb response into a similar structure
            # used by the RAG pipeline
            chunks.append({
                "id": chunk_id,
                "text": document,
                "source": metadata["source"],
                "page":metadata["page"],
                "chunk_index":metadata["chunk_index"],
                "distance": distance
            })

        return chunks