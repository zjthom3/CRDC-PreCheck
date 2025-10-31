from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", summary="Liveness probe")
async def live() -> dict[str, str]:
    """Return liveness status for orchestration probes."""
    return {"status": "ok"}
