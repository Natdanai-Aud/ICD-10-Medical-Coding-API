from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from icd10.api.deps import ActiveVersion, SessionDep
from icd10.api.schemas import DatasetMeta, MetaResponse
from icd10.core.config import get_settings
from icd10.db.models import DatasetVersion

router = APIRouter(tags=["meta"])

LICENSE_NOTICE = (
    "ICD-10 is published by the World Health Organization and is subject to WHO "
    "copyright. This service is intended for internal use; redistribution requires "
    "permission from WHO. Case examples are derived from the Thai Standard Coding "
    "Guidelines 2017."
)


@router.get("/meta", response_model=MetaResponse, summary="Dataset and API metadata")
async def get_meta(session: SessionDep, version: ActiveVersion) -> MetaResponse:
    settings = get_settings()
    return MetaResponse(
        api_version=settings.api_version,
        dataset=DatasetMeta.model_validate(version),
        license_notice=LICENSE_NOTICE,
    )


@router.get("/datasets", response_model=list[DatasetMeta], summary="All dataset versions")
async def list_datasets(session: SessionDep) -> list[DatasetMeta]:
    rows = (
        await session.scalars(
            select(DatasetVersion).order_by(DatasetVersion.imported_at.desc())
        )
    ).all()
    return [DatasetMeta.model_validate(row) for row in rows]
