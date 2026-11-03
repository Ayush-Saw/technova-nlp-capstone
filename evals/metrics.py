import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

def triage_metrics(y_true,y_pred):
    p,r,f,_=precision_recall_fscore_support(y_true,y_pred,average="macro",zero_division=0)
    return {"accuracy":float(accuracy_score(y_true,y_pred)),"macro_precision":float(p),"macro_recall":float(r),"macro_f1":float(f)}

def json_validity(outputs, validator):
    valid=0
    for x in outputs:
        try: validator.model_validate_json(x); valid+=1
        except Exception: pass
    return valid/max(len(outputs),1)

def recall_at_k(relevant_ids, retrieved_ids, k=5):
    vals=[]
    for rel,ret in zip(relevant_ids,retrieved_ids):
        vals.append(len(set(rel)&set(ret[:k]))/max(len(set(rel)),1))
    return float(np.mean(vals)) if vals else 0.0

def bootstrap_ci(values, n=2000, alpha=.05, seed=42):
    rng=np.random.default_rng(seed); a=np.asarray(values,dtype=float)
    if not len(a): return [0.0,0.0]
    samples=[rng.choice(a,len(a),replace=True).mean() for _ in range(n)]
    return [float(np.quantile(samples,alpha/2)),float(np.quantile(samples,1-alpha/2))]
