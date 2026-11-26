from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select, text

from icd10.api.deps import SessionDep
from icd10.db.models import DatasetVersion

router = APIRouter(tags=["health"])


@router.get("/health/live", summary="Liveness probe")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", summary="Readiness probe")
async def ready(session: SessionDep) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    version = await session.scalar(
        select(DatasetVersion).where(DatasetVersion.status == "active").limit(1)
    )
    return {
        "status": "ok" if version else "degraded",
        "dataset": version.name if version else "",
    }
