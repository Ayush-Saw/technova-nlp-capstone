import os, time
from collections import defaultdict, deque
from fastapi import Header, HTTPException, Request

API_KEY = os.getenv("API_KEY", "change-me-before-use")
_hits = defaultdict(deque)

async def authenticate(x_api_key: str = Header(default="")):
    if not API_KEY or API_KEY == "change-me-before-use" or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

async def enforce_size(request: Request):
    length = int(request.headers.get("content-length", "0") or 0)
    if length > int(os.getenv("MAX_REQUEST_BYTES", "20000")):
        raise HTTPException(status_code=413, detail="Request too large")

def rate_limit(client: str):
    now = time.time()
    q = _hits[client]
    while q and q[0] < now - 60: q.popleft()
    if len(q) >= int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    q.append(now)
