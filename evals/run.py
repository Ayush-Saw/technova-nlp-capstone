import argparse, json
from evals.metrics import recall_at_k, bootstrap_ci

def main():
    p=argparse.ArgumentParser(); p.add_argument("--data",default="evals/data/qa_eval.jsonl"); a=p.parse_args()
    rows=[json.loads(x) for x in open(a.data,encoding="utf-8")]
    scores=[1.0 if set(r["relevant_ids"]) & set(r["retrieved_ids"][:5]) else 0.0 for r in rows]
    print(json.dumps({"n":len(rows),"recall_at_5":recall_at_k([r["relevant_ids"] for r in rows],[r["retrieved_ids"] for r in rows]),"recall_ci95":bootstrap_ci(scores)},indent=2))
if __name__=="__main__": main()
