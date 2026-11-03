import hashlib, re

def chunk_text(text, chunk_size=900, overlap=120):
    words = text.split()
    if not words: return []
    out, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        out.append(" ".join(words[start:end]))
        if end == len(words): break
        start = max(end - overlap, start + 1)
    return out

def make_chunks(document_id, title, text, access_level="public", product_area="General"):
    chunks = []
    for i, part in enumerate(chunk_text(text)):
        cid = hashlib.sha256(f"{document_id}:{i}:{part}".encode()).hexdigest()[:20]
        chunks.append({"chunk_id":cid,"document_id":document_id,"title":title,"text":part,
                       "access_level":access_level,"product_area":product_area,"chunk_index":i})
    return chunks
