import argparse, pathlib, re, yaml
from ingest.chunking import make_chunks
from serving.rag import index_chunks

def parse_file(path):
    text = path.read_text(encoding="utf-8")
    meta = {"title":path.stem,"access_level":"public","product_area":"General"}
    if text.startswith("---"):
        parts = text.split("---",2)
        if len(parts)==3:
            meta.update(yaml.safe_load(parts[1]) or {})
            text = parts[2]
    if meta["access_level"] not in {"public","staff","admin"}: raise ValueError("Invalid access level")
    return meta, text.strip()

def main():
    p=argparse.ArgumentParser(); p.add_argument("--source",default="data/docs"); args=p.parse_args()
    chunks=[]
    for path in pathlib.Path(args.source).rglob("*"):
        if path.suffix.lower() not in {".md",".txt"}: continue
        meta, body=parse_file(path)
        chunks.extend(make_chunks(str(path),meta["title"],body,meta["access_level"],meta["product_area"]))
    index_chunks(chunks)
    print(f"Indexed {len(chunks)} chunks from {args.source}")
if __name__=="__main__": main()
