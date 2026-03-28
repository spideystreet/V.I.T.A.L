"""HTTP server to receive health data from Apple Shortcuts."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uvicorn import run as uvicorn_run

from vital.config import HEALTH_SERVER_HOST, HEALTH_SERVER_PORT
from vital.health_store import get_summary, init_db, insert_metrics

logger = logging.getLogger("vital.server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Health database initialized")
    yield


app = FastAPI(title="V.I.T.A.L Health Receiver", version="0.1.0", lifespan=lifespan)


class HealthPayload(BaseModel):
    """Payload sent by the Apple Shortcut."""

    metrics: list[dict]


@app.post("/health")
async def receive_health_data(payload: HealthPayload):
    """Receive health metrics from Apple Shortcuts."""
    if not payload.metrics:
        raise HTTPException(status_code=400, detail="No metrics provided")

    count = insert_metrics(payload.metrics)
    return {"status": "ok", "inserted": count}


@app.get("/health/summary")
async def health_summary(hours: int = 24):
    """Get aggregated health summary."""
    return get_summary(hours)


@app.get("/health/ping")
async def ping():
    return {"status": "alive"}


def main():
    """Entry point for vital-server."""
    init_db()
    uvicorn_run(
        "vital.health_server:app",
        host=HEALTH_SERVER_HOST,
        port=HEALTH_SERVER_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()
