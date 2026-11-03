import os, re, uuid
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer, CrossEncoder

URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "technova_docs")
EMBEDDER_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_client = None
_embedder = None
_reranker = None

def components():
    global _client, _embedder, _reranker
    if _client is None:
        _client = QdrantClient(url=URL)
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDER_NAME)
    if _reranker is None:
        try: _reranker = CrossEncoder(os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"))
        except Exception: _reranker = None
    return _client, _embedder, _reranker

def ensure_collection():
    client, emb, _ = components()
    dim = emb.get_sentence_embedding_dimension()
    if not client.collection_exists(COLLECTION):
        client.create_collection(COLLECTION, vectors_config={"dense": models.VectorParams(size=dim, distance=models.Distance.COSINE)})

def index_chunks(chunks):
    ensure_collection()
    client, emb, _ = components()
    points = []
    for c in chunks:
        vec = emb.encode(c["text"]).tolist()
        points.append(models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, c["chunk_id"])),
            vector={"dense": vec}, payload=c))
    if points: client.upsert(collection_name=COLLECTION, points=points)

def search(question, role, k=12):
    ensure_collection()
    client, emb, reranker = components()
    qv = emb.encode(question).tolist()
    # ACL is applied in the vector database filter before any text is returned.
    allowed = ["public"] if role == "public" else ["public", "staff"] if role == "staff" else ["public", "staff", "admin"]
    flt = models.Filter(must=[models.FieldCondition(key="access_level", match=models.MatchAny(any=allowed))])
    hits = client.query_points(collection_name=COLLECTION, query=qv, using="dense", query_filter=flt, limit=k, with_payload=True).points
    rows = [{"payload": h.payload, "score": h.score} for h in hits]
    if reranker and rows:
        scores = reranker.predict([(question, r["payload"]["text"]) for r in rows])
        rows = [r for _, r in sorted(zip(scores, rows), key=lambda x: x[0], reverse=True)]
    return rows[:5]

def answer_question(question, role):
    rows = search(question, role)
    if not rows: return {"answer":"I cannot find sufficient information in the accessible documentation to answer that.", "citations":[], "refused":True}
    context = "\n\n".join(r["payload"]["text"] for r in rows)
    # Conservative extractive fallback; replace with a grounded open-LLM generation adapter for production.
    terms = set(re.findall(r"[a-zA-Z]{4,}", question.lower()))
    sentences = re.split(r"(?<=[.!?])\s+", context)
    selected = [s for s in sentences if terms.intersection(set(re.findall(r"[a-zA-Z]{4,}", s.lower())))]
    if not selected: return {"answer":"I cannot find sufficient supporting information in the retrieved documentation.", "citations":[], "refused":True}
    return {"answer":" ".join(selected[:3]), "citations":[{"document_id":r["payload"]["document_id"],"title":r["payload"]["title"],"chunk_id":r["payload"]["chunk_id"]} for r in rows[:3]], "refused":False}
