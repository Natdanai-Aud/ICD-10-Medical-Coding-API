from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from icd10.api.deps import ActiveVersion, SessionDep
from icd10.api.schemas import BlockOut, ChapterOut
from icd10.db.models import Block, Chapter

router = APIRouter(tags=["hierarchy"])


@router.get("/chapters", response_model=list[ChapterOut], summary="List chapters")
async def list_chapters(session: SessionDep, version: ActiveVersion) -> list[ChapterOut]:
    block_counts = (
        select(Block.chapter_id, func.count(Block.id).label("cnt"))
        .group_by(Block.chapter_id)
        .subquery()
    )
    rows = (
        await session.execute(
            select(Chapter, func.coalesce(block_counts.c.cnt, 0))
            .outerjoin(block_counts, block_counts.c.chapter_id == Chapter.id)
            .where(Chapter.version_id == version.id)
            .order_by(Chapter.sort_order)
        )
    ).all()
    return [
        ChapterOut(
            id=chapter.id,
            numeral=chapter.numeral,
            title_en=chapter.title_en,
            code_start=chapter.code_start,
            code_end=chapter.code_end,
            sort_order=chapter.sort_order,
            notes=chapter.notes or [],
            block_count=count,
        )
        for chapter, count in rows
    ]


@router.get(
    "/chapters/{chapter_id}/blocks",
    response_model=list[BlockOut],
    summary="List blocks in a chapter",
)
async def list_blocks(
    chapter_id: int, session: SessionDep, version: ActiveVersion
) -> list[BlockOut]:
    chapter = await session.get(Chapter, chapter_id)
    if chapter is None or chapter.version_id != version.id:
        raise HTTPException(status_code=404, detail="chapter not found")
    blocks = (
        await session.scalars(
            select(Block)
            .where(Block.chapter_id == chapter_id)
            .order_by(Block.sort_order)
        )
    ).all()
    return [BlockOut.model_validate(block) for block in blocks]
