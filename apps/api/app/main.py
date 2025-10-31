from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import connectors, districts, health, imports, rule_results, rule_runs, rule_versions, schools, students


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="CRDC PreCheck API",
        version="0.1.0",
        description="Tenant-aware API for CRDC data ingestion and validation.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(connectors.router)
    app.include_router(districts.router)
    app.include_router(imports.router)
    app.include_router(schools.router)
    app.include_router(students.router)
    app.include_router(rule_versions.router)
    app.include_router(rule_runs.router)
    app.include_router(rule_results.router)
    return app


app = create_app()
