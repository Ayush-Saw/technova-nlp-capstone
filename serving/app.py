import logging, os, time
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from serving.schemas import QARequest, QAResponse, TriageRequest, TriageResponse
from serving.security import authenticate, enforce_size, rate_limit
from serving.rag import answer_question
from serving.triage import predict

logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"), format="%(message)s")
log = logging.getLogger("technova")
app = FastAPI(title="TechNova NLP Gateway", version="1.0.0")
REQUESTS = Counter("http_requests_total","HTTP requests",["endpoint","status"])
LATENCY = Histogram("request_latency_seconds","Request latency",["endpoint"])

@app.middleware("http")
async def observe(request: Request, call_next):
    start = time.perf_counter()
    try:
        rate_limit(request.client.host if request.client else "unknown")
        response = await call_next(request)
    except Exception:
        raise
    elapsed = time.perf_counter() - start
    endpoint = request.url.path
    LATENCY.labels(endpoint).observe(elapsed)
    REQUESTS.labels(endpoint, str(response.status_code)).inc()
    log.info({"path":endpoint,"status":response.status_code,"latency_s":round(elapsed,4)})
    response.headers["X-Model-Version"] = "technova-gateway-1.0.0"
    return response

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/metrics")
def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/v1/qa", response_model=QAResponse, dependencies=[Depends(authenticate), Depends(enforce_size)])
def qa(body: QARequest):
    result = answer_question(body.question, body.user_role)
    return {**result, "model_version":"rag-baseline-0.1.0"}

@app.post("/v1/triage", response_model=TriageResponse, dependencies=[Depends(authenticate), Depends(enforce_size)])
def triage(body: TriageRequest):
    return predict(body.ticket)
