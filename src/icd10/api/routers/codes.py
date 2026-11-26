from __future__ import annotations

import csv
import io
import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from icd10.api.deps import ActiveVersion, SessionDep
from icd10.api.schemas import (
    BlockRef,
    ChapterRef,
    CodeDetail,
    CodeRef,
    CodeSummary,
    LookupRequest,
    LookupResponse,
    NoteOut,
    ValidationItem,
    ValidationRequest,
    ValidationResponse,
)
from icd10.core.config import get_settings
from icd10.db.models import Code

router = APIRouter(tags=["codes"])

CODE_PATTERN = re.compile(r"^[A-Z]\d{2}(\.\d)?$")


def normalize_code(raw: str) -> str:
    return raw.strip().upper().replace(" ", "")


def _require_valid_format(code: str) -> None:
    if not CODE_PATTERN.match(code):
        raise HTTPException(
            status_code=422,
            detail=f"invalid ICD-10 code format: {code!r} (expected e.g. A00 or A00.0)",
        )


async def _load_code(session, version_id: int, code: str) -> Code | None:
    return await session.scalar(
        select(Code)
        .options(
            selectinload(Code.chapter),
            selectinload(Code.block),
            selectinload(Code.notes),
        )
        .where(Code.version_id == version_id, Code.code == code)
    )


@router.get("/codes/{code}", response_model=CodeDetail, summary="Look up a code")
async def get_code(code: str, session: SessionDep, version: ActiveVersion) -> CodeDetail:
    normalized = normalize_code(code)
    _require_valid_format(normalized)
    row = await _load_code(session, version.id, normalized)
    if row is None:
        raise HTTPException(status_code=404, detail=f"code {normalized} not found")

    ancestors = (
        await session.execute(
            text(
                """
                WITH RECURSIVE anc AS (
                    SELECT id, code, title_en, level, parent_id, 0 AS depth
                    FROM code WHERE id = :code_id
                    UNION ALL
                    SELECT c.id, c.code, c.title_en, c.level, c.parent_id, a.depth + 1
                    FROM code c JOIN anc a ON c.id = a.parent_id
                )
                SELECT code, title_en, level FROM anc
                WHERE depth > 0 ORDER BY depth DESC
                """
            ),
            {"code_id": row.id},
        )
    ).all()

    children = (
        await session.scalars(
            select(Code)
            .options(selectinload(Code.chapter), selectinload(Code.block))
            .where(Code.parent_id == row.id)
            .order_by(Code.code)
        )
    ).all()

    return CodeDetail(
        code=row.code,
        title_en=row.title_en,
        level=row.level,
        is_leaf=row.is_leaf,
        dagger=row.dagger,
        asterisk=row.asterisk,
        chapter=ChapterRef.model_validate(row.chapter) if row.chapter else None,
        block=BlockRef.model_validate(row.block) if row.block else None,
        ancestors=[CodeRef(code=r.code, title_en=r.title_en, level=r.level) for r in ancestors],
        children=[CodeSummary.model_validate(child) for child in children],
        notes=[NoteOut.model_validate(note) for note in row.notes],
    )


@router.get(
    "/codes/{code}/children",
    response_model=list[CodeSummary],
    summary="Direct children of a code",
)
async def get_children(
    code: str, session: SessionDep, version: ActiveVersion
) -> list[CodeSummary]:
    normalized = normalize_code(code)
    _require_valid_format(normalized)
    parent = await session.scalar(
        select(Code).where(Code.version_id == version.id, Code.code == normalized)
    )
    if parent is None:
        raise HTTPException(status_code=404, detail=f"code {normalized} not found")
    children = (
        await session.scalars(
            select(Code)
            .options(selectinload(Code.chapter), selectinload(Code.block))
            .where(Code.parent_id == parent.id)
            .order_by(Code.code)
        )
    ).all()
    return [CodeSummary.model_validate(child) for child in children]


@router.get(
    "/codes/{code}/ancestors",
    response_model=list[CodeRef],
    summary="Ancestors (breadcrumb) of a code",
)
async def get_ancestors(
    code: str, session: SessionDep, version: ActiveVersion
) -> list[CodeRef]:
    normalized = normalize_code(code)
    _require_valid_format(normalized)
    row = await session.scalar(
        select(Code).where(Code.version_id == version.id, Code.code == normalized)
    )
    if row is None:
        raise HTTPException(status_code=404, detail=f"code {normalized} not found")
    rows = (
        await session.execute(
            text(
                """
                WITH RECURSIVE anc AS (
                    SELECT id, code, title_en, level, parent_id, 0 AS depth
                    FROM code WHERE id = :code_id
                    UNION ALL
                    SELECT c.id, c.code, c.title_en, c.level, c.parent_id, a.depth + 1
                    FROM code c JOIN anc a ON c.id = a.parent_id
                )
                SELECT code, title_en, level FROM anc
                WHERE depth > 0 ORDER BY depth DESC
                """
            ),
            {"code_id": row.id},
        )
    ).all()
    return [CodeRef(code=r.code, title_en=r.title_en, level=r.level) for r in rows]


@router.post("/codes/lookup", response_model=LookupResponse, summary="Batch code lookup")
async def batch_lookup(
    payload: LookupRequest, session: SessionDep, version: ActiveVersion
) -> LookupResponse:
    settings = get_settings()
    if len(payload.codes) > settings.max_batch_lookup:
        raise HTTPException(
            status_code=422,
            detail=f"at most {settings.max_batch_lookup} codes per request",
        )
    normalized = list(dict.fromkeys(normalize_code(code) for code in payload.codes))
    rows = (
        await session.scalars(
            select(Code)
            .options(selectinload(Code.chapter), selectinload(Code.block))
            .where(Code.version_id == version.id, Code.code.in_(normalized))
            .order_by(Code.code)
        )
    ).all()
    found_codes = {row.code for row in rows}
    return LookupResponse(
        found=[CodeSummary.model_validate(row) for row in rows],
        not_found=[code for code in normalized if code not in found_codes],
    )


@router.post(
    "/codes/validate", response_model=ValidationResponse, summary="Validate codes"
)
async def validate_codes(
    payload: ValidationRequest, session: SessionDep, version: ActiveVersion
) -> ValidationResponse:
    normalized = list(dict.fromkeys(normalize_code(code) for code in payload.codes))
    rows = (
        await session.scalars(
            select(Code)
            .options(selectinload(Code.chapter), selectinload(Code.parent))
            .where(Code.version_id == version.id, Code.code.in_(normalized))
        )
    ).all()
    by_code = {row.code: row for row in rows}
    items: list[ValidationItem] = []
    for code in normalized:
        row = by_code.get(code)
        if row is None:
            items.append(
                ValidationItem(
                    code=code,
                    valid=False,
                    reason="not found in ICD-10 WHO 2016",
                )
            )
            continue
        items.append(
            ValidationItem(
                code=row.code,
                valid=True,
                level=row.level,
                is_leaf=row.is_leaf,
                parent=CodeRef.model_validate(row.parent) if row.parent else None,
                chapter=ChapterRef.model_validate(row.chapter) if row.chapter else None,
            )
        )
    return ValidationResponse(items=items)


@router.get(
    "/export/codes.csv",
    summary="Full code list as CSV (snapshot for HIS caching)",
    response_class=StreamingResponse,
)
async def export_codes_csv(session: SessionDep, version: ActiveVersion) -> StreamingResponse:
    rows = (
        await session.scalars(
            select(Code)
            .options(selectinload(Code.chapter), selectinload(Code.block))
            .where(Code.version_id == version.id)
            .order_by(Code.code)
        )
    ).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "code",
            "title_en",
            "level",
            "parent_code",
            "chapter",
            "block",
            "is_leaf",
            "dagger",
            "asterisk",
        ]
    )
    parents = {row.id: row.code for row in rows}
    for row in rows:
        writer.writerow(
            [
                row.code,
                row.title_en,
                row.level,
                parents.get(row.parent_id, ""),
                row.chapter.numeral if row.chapter else "",
                f"{row.block.code_start}-{row.block.code_end}" if row.block else "",
                "true" if row.is_leaf else "false",
                "true" if row.dagger else "false",
                "true" if row.asterisk else "false",
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="icd10-codes.csv"'},
    )
