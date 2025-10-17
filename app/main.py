from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal
from .rules.loader import load_rules_from_dir
from .intel.loader import load_intel_from_dir

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Open Threat Situational Awareness", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and templates for a minimal UI
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Routers will be included after they are created
from .routers import ingest, ui, search, admin  # noqa: E402
from .routers import alerts as alerts_router  # noqa: E402

app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(alerts_router.router, prefix="/search", tags=["search"])  # unify under /search

# UI endpoints are in their own router
app.include_router(ui.router)


@app.on_event("startup")
def on_startup():
    # Load rules and intel on start
    db = SessionLocal()
    try:
        load_rules_from_dir(db)
        load_intel_from_dir(db)
    finally:
        db.close()
