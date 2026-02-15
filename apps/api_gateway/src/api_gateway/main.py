from fastapi import FastAPI

from db.init_db import init_db

# Routers
from api_gateway.routers import verticals
from api_gateway.routers.pains import router as pains_router
from api_gateway.routers.trends import router as trends_router


app = FastAPI(
    title="Sense OS API",
    version="0.1.0",
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
app.include_router(trends_router)
