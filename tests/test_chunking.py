from ingest.chunking import chunk_text, make_chunks
def test_chunks_cover_text():
    text=" ".join(["word"]*2500)
    chunks=chunk_text(text,chunk_size=500,overlap=50)
    assert len(chunks)>1 and all(chunks)
def test_metadata_preserved():
    c=make_chunks("doc","Title","some documentation", "staff","Identity")[0]
    assert c["access_level"]=="staff" and c["product_area"]=="Identity"
