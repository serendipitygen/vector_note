import os
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from dotenv import load_dotenv
from typing import List

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

def get_collections():
    return qdrant_client.get_collections()

def create_notes_collection():
    # 벡터 차원 1024, cosine similarity
    qdrant_client.recreate_collection(
        collection_name="notes",
        vectors_config=qmodels.VectorParams(size=1024, distance="Cosine")
    )

def insert_vectors(collection_name: str, vectors: List[List[float]], ids: List[int], note_ids: List[int], contents: List[str]):
    # 컬렉션이 없으면 자동 생성
    try:
        qdrant_client.get_collection(collection_name=collection_name)
    except Exception:
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(size=1024, distance="Cosine")
        )
    points = []
    for idx, (vec, note_id, content) in enumerate(zip(vectors, note_ids, contents)):
        points.append(qmodels.PointStruct(
            id=ids[idx],
            vector=vec,
            payload={"note_id": note_id, "content": content}
        ))
    qdrant_client.upsert(collection_name=collection_name, points=points)

def search_similar(collection_name: str, query_vector: List[float], top_k: int = 5):
    result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
    return [
        {
            "note_id": hit.payload.get("note_id"),
            "content": hit.payload.get("content"),
            "score": hit.score
        }
        for hit in result
    ]

def delete_vectors(collection_name: str, note_id: int):
    qdrant_client.delete(
        collection_name=collection_name,
        filter=qmodels.Filter(
            must=[qmodels.FieldCondition(
                key="note_id",
                match=qmodels.MatchValue(value=note_id)
            )]
        )
    ) 