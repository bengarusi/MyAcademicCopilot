from typing import List, Tuple, Optional
import numpy as np
import litellm
from langfuse import observe

EMBEDDING_MODEL = "gemini/text-embedding-004"


def get_embedding(text: str) -> np.ndarray:
    """
    Get an embedding vector for the given text using Gemini via LiteLLM.
    Returns a 1D numpy array of dtype float32.
    """
    resp = litellm.embedding(
        model=EMBEDDING_MODEL,
        input=text,
    )
    vec = resp["data"][0]["embedding"]
    return np.array(vec, dtype="float32")


class SimpleRAGStore:
    def __init__(self) -> None:
        # Parallel lists – same index across all three
        self.doc_ids: List[str] = []
        self.docs: List[str] = []
        self.embeddings: Optional[np.ndarray] = None  # Shape: (N, D)

    def add_document(self, doc_id: str, text: str) -> None:
        """
        Add a single document and compute its embedding.
        """
        emb_input = f"{doc_id}\n{text}"
        emb = get_embedding(emb_input)  # Shape: (D,)

        self.doc_ids.append(doc_id)
        self.docs.append(text)


        if self.embeddings is None:
            # First document – start the matrix
            self.embeddings = emb[None, :]
        else:
            # Stack as new row
            self.embeddings = np.vstack([self.embeddings, emb])

    def save_cache(self, path: str) -> None:
        """
        Save embeddings + documents to a compressed NPZ file.
        """
        if self.embeddings is None:
            return
        np.savez_compressed(
            path,
            embeddings=self.embeddings,
            doc_ids=np.array(self.doc_ids, dtype=object),
            docs=np.array(self.docs, dtype=object),
        )

    @classmethod
    def load_cache(cls, path: str) -> "SimpleRAGStore":
        """
        Load embeddings + documents from a compressed NPZ file.
        """
        data = np.load(path, allow_pickle=True)
        store = cls()
        store.embeddings = data["embeddings"]
        store.doc_ids = list(data["doc_ids"])
        store.docs = list(data["docs"])
        return store

    @observe(name="rag_retrieval")
    def search(self, query: str, k: int = 3) -> List[Tuple[str, str]]:
        """
        Return the top-k most similar documents for the given query.
        Uses cosine similarity between query embedding and doc embeddings.
        Returns a list of (doc_id, text) tuples.
        """
        if self.embeddings is None or len(self.doc_ids) == 0:
            return []

        # Compute query embedding
        q_emb = get_embedding(query)

        # Cosine similarity
        doc_embs = self.embeddings  # (N, D)
        dot_products = doc_embs @ q_emb  # (N,)
        norms = np.linalg.norm(doc_embs, axis=1) * np.linalg.norm(q_emb)
        sims = dot_products / (norms + 1e-8)

        # Get indices of top-k documents, highest similarity first
        top_indices = sims.argsort()[::-1][:k]

        results: List[Tuple[str, str]] = []
        for i in top_indices:
            idx = int(i)
            results.append((self.doc_ids[idx], self.docs[idx]))
        return results
