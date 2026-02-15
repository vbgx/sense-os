from __future__ import annotations

import os
from pathlib import Path

import redis  # type: ignore
from fastapi import APIRouter, HTTPException, Query

from api_gateway.schemas.ops import LogsResponse, QueuesResponse, RunRequest, RunResponse
from api_gateway.services.run_service import list_fixtures, list_runs, start_run

router = APIRouter(prefix="/ops", tags=["ops"])

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DOCKER_HOST = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
COMPOSE_PROJECT = os.getenv("COMPOSE_PROJECT_NAME")


@router.get("/queues", response_model=QueuesResponse)
def queues_status():
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    queues = {}
    for q in ("ingest", "process", "cluster", "trend"):
        pending = int(r.llen(q))
        retry = int(r.zcard(f"{q}:retry"))
        dlq = int(r.llen(f"{q}:dlq"))
        queues[q] = {"pending": pending, "retry": retry, "dlq": dlq}
    return {"queues": queues}


@router.get("/runs")
def runs_list():
    return {"items": list_runs()}


@router.post("/run", response_model=RunResponse)
def run_pipeline(req: RunRequest):
    run_id = start_run(
        mode=req.mode,
        vertical_id=req.vertical_id,
        source=req.source,
        query=req.query,
        limit=req.limit,
        fixture_name=req.fixture,
    )
    return {"run_id": run_id, "status": "running"}


@router.get("/fixtures")
def fixtures_list():
    items = []
    for fx in list_fixtures():
        path = Path(fx.get("path", ""))
        items.append(
            {
                "name": fx.get("name"),
                "description": fx.get("description"),
                "default_queries": fx.get("default_queries") or [],
                "file": path.name,
            }
        )
    return {"items": items}


@router.get("/logs", response_model=LogsResponse)
def logs(
    *,
    service: str = Query(..., min_length=1),
    tail: int = Query(default=200, ge=1, le=2000),
):
    try:
        import docker  # type: ignore
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"docker SDK not available: {exc}")

    if DOCKER_HOST.startswith("unix://"):
        sock = DOCKER_HOST.replace("unix://", "", 1)
        if not Path(sock).exists():
            raise HTTPException(status_code=503, detail="docker socket not available")

    try:
        client = docker.DockerClient(base_url=DOCKER_HOST)
        filters = {"label": [f"com.docker.compose.service={service}"]}
        if COMPOSE_PROJECT:
            filters["label"].append(f"com.docker.compose.project={COMPOSE_PROJECT}")
        containers = client.containers.list(all=True, filters=filters)
        if not containers:
            raise HTTPException(status_code=404, detail=f"service not found: {service}")
        containers.sort(
            key=lambda c: c.attrs.get("State", {}).get("StartedAt", ""),
            reverse=True,
        )
        container = containers[0]
        raw = container.logs(tail=tail)
        text = raw.decode("utf-8", errors="replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
        return {"service": service, "container_id": container.id[:12], "lines": text.splitlines()}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"failed to fetch logs: {exc}")
