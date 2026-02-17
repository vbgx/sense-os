from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.routers import (
    clusters,
    health,
    insights,
    ops,
    pains,
    signals,
    timeline,
    trends,
    verticals,
    meta,
    overview
)

app = FastAPI(title="sense-os api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ops.router)
app.include_router(insights.router)
app.include_router(clusters.router)
app.include_router(timeline.router)
app.include_router(trends.router)
app.include_router(verticals.router)
app.include_router(pains.router)
app.include_router(signals.router)
app.include_router(meta.router)
app.include_router(overview.router) 