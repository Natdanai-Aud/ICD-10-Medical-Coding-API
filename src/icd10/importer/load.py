from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path

from sqlalchemy import delete, select, text

from icd10.db.base import Base
from icd10.db.models import (
    Block,
    CaseExample,
    CaseExampleLine,
    Chapter,
    Code,
    CodeNote,
    DatasetVersion,
    GuidelineSection,
    IndexTerm,
)
from icd10.db.session import SessionLocal, engine
from icd10.importer.parse_guideline import GuidelineResult
from icd10.importer.parse_index import IndexResult
from icd10.importer.parse_tabular import ParsedBlock, TabularResult

DEFAULT_VERSION = "ICD-10 WHO 2016 (5th ed.)"


def file_checksum(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def _code_key(code: str) -> int:
    letter = code[0]
    return (ord(letter) - ord("A")) * 100_000 + int(code[1:3]) * 10 + (
        int(code[4]) if len(code) > 4 else 0
    )


def _range_size(start: str, end: str) -> int:
    return _code_key(end) - _code_key(start)


def _block_lookup(blocks: list[ParsedBlock]) -> dict[str, list[tuple[str, str, int]]]:
    """chapter numeral -> [(start, end, sort_order)] for most-specific block matching."""
    out: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    for block in blocks:
        out[block.chapter_numeral].append(
            (block.code_start, block.code_end, block.sort_order)
        )
    return out


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_code_search "
                "ON code USING gin (to_tsvector('english', search_text))"
            )
        )


async def load_dataset(
    tabular: TabularResult,
    index: IndexResult,
    version_name: str = DEFAULT_VERSION,
    source_checksum: str = "",
) -> dict[str, object]:
    async with SessionLocal() as session:
        existing = await session.scalar(
            select(DatasetVersion).where(DatasetVersion.name == version_name)
        )
        if existing is not None:
            await session.execute(
                delete(DatasetVersion).where(DatasetVersion.id == existing.id)
            )
            await session.flush()

        version = DatasetVersion(
            name=version_name,
            source_checksum=source_checksum,
            status="draft",
        )
        session.add(version)
        await session.flush()

        chapters: dict[str, Chapter] = {}
        for parsed in tabular.chapters:
            chapter = Chapter(
                version_id=version.id,
                numeral=parsed.numeral,
                title_en=parsed.title,
                code_start=parsed.code_start,
                code_end=parsed.code_end,
                sort_order=parsed.sort_order,
                notes=[{"kind": n.kind, "text": n.text} for n in parsed.notes],
            )
            session.add(chapter)
            chapters[parsed.numeral] = chapter
        await session.flush()

        blocks: list[tuple[ParsedBlock, Block]] = []
        for parsed in tabular.blocks:
            chapter = chapters[parsed.chapter_numeral]
            block = Block(
                chapter_id=chapter.id,
                code_start=parsed.code_start,
                code_end=parsed.code_end,
                title_en=parsed.title,
                sort_order=parsed.sort_order,
            )
            session.add(block)
            blocks.append((parsed, block))
        await session.flush()

        block_index = _block_lookup(tabular.blocks)
        block_ids: dict[tuple[str, int], int] = {
            (parsed.chapter_numeral, parsed.sort_order): block.id for parsed, block in blocks
        }

        def best_block(chapter_numeral: str, code: str) -> int | None:
            key = code[:3]
            candidates = [
                (start, end, sort_order)
                for start, end, sort_order in block_index.get(chapter_numeral, [])
                if start <= key <= end
            ]
            if not candidates:
                return None
            start, end, sort_order = min(
                candidates, key=lambda item: _range_size(item[0], item[1])
            )
            return block_ids.get((chapter_numeral, sort_order))

        code_objects: dict[str, Code] = {}
        for parsed in tabular.codes:
            if parsed.level != 1:
                continue
            chapter = chapters[parsed.chapter_numeral]
            search_text = parsed.title
            for note in parsed.notes:
                if note.kind == "includes":
                    search_text += " " + note.text
            obj = Code(
                version_id=version.id,
                code=parsed.code,
                level=1,
                chapter_id=chapter.id,
                block_id=best_block(parsed.chapter_numeral, parsed.code),
                title_en=parsed.title,
                dagger=parsed.dagger,
                asterisk=parsed.asterisk,
                source_page=parsed.page,
                search_text=f"{search_text} {search_text.replace('-', '')}".strip(),
            )
            session.add(obj)
            code_objects[parsed.code] = obj
        await session.flush()

        for parsed in tabular.codes:
            if parsed.level != 2:
                continue
            chapter = chapters[parsed.chapter_numeral]
            parent = code_objects.get(parsed.code[:3])
            search_text = parsed.title
            for note in parsed.notes:
                if note.kind == "includes":
                    search_text += " " + note.text
            obj = Code(
                version_id=version.id,
                code=parsed.code,
                parent_id=parent.id if parent else None,
                level=2,
                chapter_id=chapter.id,
                block_id=best_block(parsed.chapter_numeral, parsed.code),
                title_en=parsed.title,
                dagger=parsed.dagger,
                asterisk=parsed.asterisk,
                source_page=parsed.page,
                search_text=f"{search_text} {search_text.replace('-', '')}".strip(),
            )
            session.add(obj)
            code_objects[parsed.code] = obj
        await session.flush()

        for parsed in tabular.codes:
            obj = code_objects[parsed.code]
            for order, note in enumerate(parsed.notes):
                session.add(CodeNote(code_id=obj.id, kind=note.kind, text=note.text, ord=order))

        children = {code.parent_id for code in code_objects.values() if code.parent_id}
        for code in code_objects.values():
            code.is_leaf = code.id not in children
        await session.flush()

        # Index terms: build the tree with ORM relationships so parent ids resolve.
        stack: list[IndexTerm] = []
        pending: list[IndexTerm] = []
        for parsed in index.terms:
            parent = (
                stack[parsed.level - 1]
                if parsed.level > 0 and parsed.level <= len(stack)
                else None
            )
            obj = IndexTerm(
                version_id=version.id,
                term=parsed.term,
                term_norm=parsed.term_norm,
                level=parsed.level,
                parent=parent,
                code=parsed.code,
                see_target=parsed.see_target,
                see_also_target=parsed.see_also_target,
                kind=parsed.kind,
                ord=parsed.ord,
            )
            if parsed.level < len(stack):
                stack = stack[: parsed.level]
            stack.append(obj)
            pending.append(obj)
            if len(pending) >= 5000:
                session.add_all(pending)
                await session.flush()
                pending.clear()
        if pending:
            session.add_all(pending)
            await session.flush()

        resolved = {t.code for t in index.terms if t.code} & set(code_objects)
        unresolved = sorted({t.code for t in index.terms if t.code} - set(code_objects))
        version.code_count = len(code_objects)
        version.status = "active"
        version.meta = {
            "chapters": len(chapters),
            "blocks": len(blocks),
            "codes": len(code_objects),
            "categories": sum(1 for c in tabular.codes if c.level == 1),
            "subcategories": sum(1 for c in tabular.codes if c.level == 2),
            "index_terms": len(index.terms),
            "index_codes_resolved": len(resolved),
            "index_codes_unresolved": unresolved,
            "warnings": tabular.warnings + index.warnings,
        }
        await session.commit()
        return dict(version.meta)


async def load_guideline_examples(
    guideline: GuidelineResult,
    version_name: str = DEFAULT_VERSION,
    source_checksum: str = "",
) -> dict[str, object]:
    async with SessionLocal() as session:
        version = await session.scalar(
            select(DatasetVersion).where(DatasetVersion.name == version_name)
        )
        if version is None:
            raise RuntimeError(
                f"dataset version {version_name!r} not found; import ICD data first"
            )

        # Replace existing guideline data for this version
        await session.execute(
            delete(CaseExample).where(CaseExample.version_id == version.id)
        )
        await session.execute(
            delete(GuidelineSection).where(GuidelineSection.version_id == version.id)
        )
        await session.flush()

        # Sections (optional, may be empty from parser)
        section_ids: dict[str, int] = {}
        for s in guideline.sections:
            code = str(s.get("code", "")).strip()
            if not code:
                continue
            section = GuidelineSection(
                version_id=version.id,
                code=code,
                title_th=str(s.get("title_th", "")),
                page_start=s.get("page_start"),
                page_end=s.get("page_end"),
            )
            session.add(section)
            await session.flush()
            section_ids[code] = section.id

        known_codes = {
            row[0]
            for row in (
                await session.execute(
                    select(Code.code).where(Code.version_id == version.id)
                )
            ).all()
        }

        example_count = 0
        line_count = 0
        resolved_count = 0
        unresolved_codes: set[str] = set()

        for ex in guideline.examples:
            section_id = None
            # try to infer section from example_no prefix
            prefix = ex.example_no.split("-")[0] if "-" in ex.example_no else None
            if prefix and prefix in section_ids:
                section_id = section_ids[prefix]

            case = CaseExample(
                version_id=version.id,
                example_no=ex.example_no,
                section_id=section_id,
                page=ex.page,
                scenario_th=ex.scenario_th,
                source_ref=ex.source_ref,
            )
            session.add(case)
            await session.flush()
            example_count += 1

            for ln in ex.lines:
                code = (ln.code or "").strip().upper() or None
                status = "unresolved"
                title_en = None
                if code:
                    if code in known_codes:
                        status = "resolved"
                        resolved_count += 1
                    else:
                        status = "unresolved"
                        unresolved_codes.add(code)
                session.add(
                    CaseExampleLine(
                        case_id=case.id,
                        role=ln.role,
                        diagnosis_text=ln.diagnosis_text,
                        code=code,
                        code_title_en=title_en,
                        code_status=status,
                        ord=ln.ord,
                    )
                )
                line_count += 1

        meta = dict(version.meta or {})
        guideline_meta = {
            "case_examples": example_count,
            "case_example_lines": line_count,
            "case_codes_resolved": resolved_count,
            "case_codes_unresolved": sorted(unresolved_codes),
            "warnings": guideline.warnings[:200],
            "source_checksum": source_checksum,
        }
        meta["guideline"] = guideline_meta
        # keep version active
        version.meta = meta
        version.status = "active"
        await session.commit()
        return guideline_meta
