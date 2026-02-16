from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from db.adapters import init_db

# Routers
from api_gateway.routers import verticals
from api_gateway.routers.signals import router as signals_router
from api_gateway.routers.ops import router as ops_router
from api_gateway.routers.pains import router as pains_router
from api_gateway.routers.insights import router as insights_router
from api_gateway.routers.trends import router as trends_router
from api_gateway.routers.clusters import router as clusters_router


app = FastAPI(
    title="Sense OS API",
    version="0.1.0",
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

@app.on_event("startup")
def on_startup() -> None:
    init_db()


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(verticals.router)
app.include_router(pains_router)
app.include_router(insights_router)
app.include_router(trends_router)
app.include_router(signals_router)
app.include_router(ops_router)
app.include_router(clusters_router)

# ---------------------------------------------------------
# Static UI
# ---------------------------------------------------------
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="ui")


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/ui")
