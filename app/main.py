from __future__ import annotations

from fastapi import FastAPI

from .services.orchestrator import run_collectors
from .store import DashboardStore

app = FastAPI(title="FedRAMP Evidence Dashboard API", version="0.2.0")
store = DashboardStore()


@app.on_event("startup")
def startup() -> None:
    items, collectors = run_collectors()
    store.refresh(items, collectors)


@app.get("/health")
def health():
    snapshot = store.snapshot()
    return {
        "status": "ok",
        "generated_at_utc": snapshot.generated_at_utc,
        "collector_count": len(snapshot.collectors),
    }


@app.get("/snapshot")
def snapshot():
    return store.snapshot().model_dump()


@app.post("/refresh")
def refresh():
    items, collectors = run_collectors()
    store.refresh(items, collectors)
    return store.snapshot().model_dump()
