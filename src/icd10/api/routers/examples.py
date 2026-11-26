from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from icd10.api.deps import ActiveVersion, SessionDep
from icd10.api.schemas import CaseExampleList, CaseExampleOut
from icd10.db.models import CaseExample, CaseExampleLine

router = APIRouter(tags=["examples"])


@router.get("/examples", response_model=CaseExampleList, summary="Coding guideline case examples")
async def list_examples(
    session: SessionDep,
    version: ActiveVersion,
    code: str | None = Query(default=None, description="Filter by ICD-10 code used in the case"),
    q: str | None = Query(default=None, max_length=120, description="Search Thai case text"),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> CaseExampleList:
    stmt = select(CaseExample).where(CaseExample.version_id == version.id)
    if code:
        stmt = stmt.where(
            CaseExample.id.in_(
                select(CaseExampleLine.case_id).where(CaseExampleLine.code == code.upper())
            )
        )
    if q:
        stmt = stmt.where(CaseExample.scenario_th.ilike(f"%{q}%"))

    total = await session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = (
        await session.scalars(
            stmt.options(selectinload(CaseExample.lines))
            .order_by(CaseExample.example_no)
            .limit(limit)
            .offset(offset)
        )
    ).all()
    return CaseExampleList(
        total=total,
        limit=limit,
        offset=offset,
        items=[CaseExampleOut.model_validate(row) for row in rows],
    )


@router.get("/examples/{example_id}", response_model=CaseExampleOut, summary="Case example detail")
async def get_example(
    example_id: int, session: SessionDep, version: ActiveVersion
) -> CaseExampleOut:
    row = await session.scalar(
        select(CaseExample)
        .options(selectinload(CaseExample.lines))
        .where(CaseExample.id == example_id, CaseExample.version_id == version.id)
    )
    if row is None:
        raise HTTPException(status_code=404, detail="case example not found")
    return CaseExampleOut.model_validate(row)


@router.get(
    "/examples/by-code/{code}",
    response_model=list[CaseExampleOut],
    summary="Case examples that use a given code",
)
async def examples_by_code(
    code: str, session: SessionDep, version: ActiveVersion
) -> list[CaseExampleOut]:
    normalized = code.strip().upper()
    rows = (
        await session.scalars(
            select(CaseExample)
            .options(selectinload(CaseExample.lines))
            .where(
                CaseExample.version_id == version.id,
                CaseExample.id.in_(
                    select(CaseExampleLine.case_id).where(
                        CaseExampleLine.code == normalized
                    )
                ),
            )
            .order_by(CaseExample.example_no)
        )
    ).all()
    return [CaseExampleOut.model_validate(row) for row in rows]
