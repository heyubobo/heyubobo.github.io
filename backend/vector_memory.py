import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

import config

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

_embedding_model: SentenceTransformer | None = None
_index: faiss.IndexFlatL2 | None = None
_memory_store: list[str] = []


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def _load_store() -> None:
    global _index, _memory_store

    if _index is not None:
        return

    if config.MEMORY_INDEX_PATH.exists() and config.MEMORY_PKL_PATH.exists():
        _index = faiss.read_index(str(config.MEMORY_INDEX_PATH))
        with open(config.MEMORY_PKL_PATH, "rb") as f:
            _memory_store = pickle.load(f)
    else:
        _index = faiss.IndexFlatL2(EMBEDDING_DIM)
        _memory_store = []


def _persist() -> None:
    faiss.write_index(_index, str(config.MEMORY_INDEX_PATH))
    with open(config.MEMORY_PKL_PATH, "wb") as f:
        pickle.dump(_memory_store, f)


def _encode(text: str) -> np.ndarray:
    model = _get_embedding_model()
    vector = model.encode([text])
    return np.array(vector, dtype=np.float32)


def add_memory(text: str) -> None:
    _load_store()
    _index.add(_encode(text))
    _memory_store.append(text)
    _persist()


def search_memory(query: str, k: int = config.MEMORY_SEARCH_K) -> list[str]:
    _load_store()

    if not _memory_store:
        return []

    _, indices = _index.search(_encode(query), min(k, len(_memory_store)))

    results: list[str] = []
    seen: set[str] = set()
    for idx in indices[0]:
        if 0 <= idx < len(_memory_store):
            item = _memory_store[idx]
            if item not in seen:
                seen.add(item)
                results.append(item)
    return results
