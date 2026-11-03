import os, re
from serving.schemas import TriageResponse

VERSION = os.getenv("TRIAGE_MODEL_VERSION", "baseline-0.1.0")
LABELS = ["Authentication", "Billing", "Bug", "Feature Request", "Performance", "Other"]

def predict(ticket: str):
    t = ticket.lower()
    if any(x in t for x in ["login", "password", "sign in", "authentication"]): category, area = "Authentication", "Identity"
    elif any(x in t for x in ["payment", "invoice", "charge", "billing"]): category, area = "Billing", "Payments"
    elif any(x in t for x in ["slow", "latency", "timeout", "performance"]): category, area = "Performance", "Platform"
    elif any(x in t for x in ["feature", "please add", "request"]): category, area = "Feature Request", "Product"
    elif any(x in t for x in ["error", "crash", "broken", "bug", "fails"]): category, area = "Bug", "Application"
    else: category, area = "Other", "General"
    priority = "Critical" if any(x in t for x in ["all users", "production down", "data loss"]) else "High" if any(x in t for x in ["cannot", "unable", "blocked", "urgent"]) else "Medium" if category != "Other" else "Low"
    summary = re.sub(r"\s+", " ", ticket).strip()
    summary = summary[:157] + "..." if len(summary) > 160 else summary
    return {"category":category, "priority":priority, "product_area":area, "summary":summary, "model_version":VERSION}
