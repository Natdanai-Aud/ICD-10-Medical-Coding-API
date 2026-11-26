from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import text

from icd10.api.deps import ActiveVersion, SessionDep
from icd10.api.schemas import SearchHit, SearchResponse
from icd10.core.config import get_settings

router = APIRouter(tags=["search"])

SEARCH_CTE = """
WITH params AS (SELECT CAST(:q AS text) AS term),
code_exact AS (
    SELECT c.code, c.title_en, c.level, c.is_leaf, 2.0::float AS score, c.code AS matched
    FROM code c CROSS JOIN params p
    WHERE c.version_id = :version_id AND c.code = upper(p.term)
),
code_prefix AS (
    SELECT c.code, c.title_en, c.level, c.is_leaf, 1.8::float AS score, c.code AS matched
    FROM code c CROSS JOIN params p
    WHERE c.version_id = :version_id AND c.code LIKE upper(p.term) || '%'
),
code_hits AS (
    SELECT c.code, c.title_en, c.level, c.is_leaf,
           ts_rank(to_tsvector('english', c.search_text),
                   plainto_tsquery('english', p.term))::float AS score,
           NULL::text AS matched
    FROM code c CROSS JOIN params p
    WHERE c.version_id = :version_id
      AND to_tsvector('english', c.search_text) @@ plainto_tsquery('english', p.term)
),
term_hits AS (
    SELECT c.code, c.title_en, c.level, c.is_leaf,
           GREATEST(
               similarity(t.term_norm, p.term),
               CASE WHEN t.term_norm = p.term THEN 1.5 ELSE 0.0 END,
               CASE WHEN t.term_norm LIKE p.term || '%' THEN 1.2 ELSE 0.0 END
           )::float AS score,
           t.term AS matched
    FROM index_term t
    JOIN code c ON c.code = t.code AND c.version_id = t.version_id
    CROSS JOIN params p
    WHERE t.version_id = :version_id
      AND t.code IS NOT NULL
      AND (t.term_norm % p.term OR t.term_norm LIKE p.term || '%')
),
merged AS (
    SELECT code, title_en, level, is_leaf, max(score) AS score, max(matched) AS matched
    FROM (
        SELECT * FROM code_exact
        UNION ALL SELECT * FROM code_prefix
        UNION ALL SELECT * FROM code_hits
        UNION ALL SELECT * FROM term_hits
    ) s
    GROUP BY code, title_en, level, is_leaf
)
"""


@router.get("/search", response_model=SearchResponse, summary="Search codes and index terms")
async def search(
    session: SessionDep,
    version: ActiveVersion,
    q: str = Query(min_length=1, max_length=120),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> SearchResponse:
    term = q.strip().lower()
    params = {"q": term, "version_id": version.id, "limit": limit, "offset": offset}

    total = await session.scalar(
        text(SEARCH_CTE + "SELECT count(*) FROM merged"), params
    )
    rows = (
        await session.execute(
            text(
                SEARCH_CTE
                + "SELECT code, title_en, level, is_leaf, score, matched "
                + "FROM merged ORDER BY score DESC, length(code), code "
                + "LIMIT :limit OFFSET :offset"
            ),
            params,
        )
    ).all()

    return SearchResponse(
        query=q,
        total=int(total or 0),
        limit=limit,
        offset=offset,
        items=[
            SearchHit(
                code=row.code,
                title_en=row.title_en,
                level=row.level,
                is_leaf=row.is_leaf,
                score=float(row.score),
                matched_term=row.matched,
            )
            for row in rows
        ],
    )


AUTOCOMPLETE_SQL = """
WITH params AS (SELECT CAST(:q AS text) AS term),
term_hits AS (
    SELECT c.code, c.title_en, c.level, min(length(t.term_norm)) AS rank
    FROM index_term t
    JOIN code c ON c.code = t.code AND c.version_id = t.version_id
    CROSS JOIN params p
    WHERE t.version_id = :version_id
      AND t.code IS NOT NULL
      AND t.term_norm LIKE p.term || '%'
    GROUP BY c.code, c.title_en, c.level
),
code_hits AS (
    SELECT c.code, c.title_en, c.level, 0 AS rank
    FROM code c CROSS JOIN params p
    WHERE c.version_id = :version_id AND c.code LIKE upper(p.term) || '%'
)
SELECT code, title_en, level
FROM (SELECT * FROM code_hits UNION ALL SELECT * FROM term_hits) s
GROUP BY code, title_en, level
ORDER BY min(rank), length(code), code
LIMIT :limit
"""


@router.get("/autocomplete", response_model=list[SearchHit], summary="Typeahead suggestions")
async def autocomplete(
    session: SessionDep,
    version: ActiveVersion,
    q: str = Query(min_length=1, max_length=80),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[SearchHit]:
    term = q.strip().lower()
    rows = (
        await session.execute(
            text(AUTOCOMPLETE_SQL),
            {"q": term, "version_id": version.id, "limit": limit},
        )
    ).all()
    return [
        SearchHit(
            code=row.code,
            title_en=row.title_en,
            level=row.level,
            is_leaf=False,
            score=0.0,
            matched_term=None,
        )
        for row in rows
    ]


@router.get("/search/config", include_in_schema=False)
async def search_config() -> dict[str, int]:
    settings = get_settings()
    return {
        "default_page_size": settings.default_page_size,
        "max_page_size": settings.max_page_size,
    }
