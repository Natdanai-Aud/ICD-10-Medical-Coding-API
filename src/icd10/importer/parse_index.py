from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

PAGE_WIDTH_SPLIT = 190.0
HEADER_Y = 45.0
FOOTER_MARGIN = 35.0

CODE_RE = re.compile(
    r"\s([A-Z]\d{2}(?:\.\d)?)[\u2020*]?(?:\s+([A-Z]\d{2}(?:\.\d)?)[\u2020*]?)?\s*$"
)
SEE_ALSO_RE = re.compile(r"\s[\u2013\-]\s+see also\s+(.+)$", re.IGNORECASE)
SEE_RE = re.compile(r"\s[\u2013\-]\s+see\s+(.+)$", re.IGNORECASE)
LEVEL_RE = re.compile(r"^((?:[\u2013\-]\s+)*)")
PAGE_NUM_RE = re.compile(r"^\s*\d{1,4}\s*$")
SECTION_HEADERS = {
    "ALPHABETICAL INDEX TO DISEASES AND NATURE OF INJURY",
    "EXTERNAL CAUSES OF INJURY",
    "TABLE OF DRUGS AND CHEMICALS",
    "INTERNATIONAL CLASSIFICATION OF DISEASES",
}

# The alphabetical index starts after the introduction (PDF page 17) and ends
# before Section III (Table of drugs and chemicals, PDF page 723).
INDEX_FIRST_PAGE = 17
INDEX_LAST_PAGE = 722  # 1-based PDF page, inclusive bound via range()


@dataclass
class IndexLine:
    column: int
    x0: float
    y0: float
    text: str


@dataclass
class ParsedIndexTerm:
    term: str
    term_norm: str
    level: int
    code: str | None
    see_target: str | None
    see_also_target: str | None
    kind: str
    page: int
    ord: int


@dataclass
class IndexResult:
    terms: list[ParsedIndexTerm]
    warnings: list[str] = field(default_factory=list)


def _page_lines(page: pymupdf.Page) -> list[IndexLine]:
    words = page.get_text("words")
    grouped: dict[tuple[int, int], list[tuple[float, float, str]]] = {}
    for x0, y0, _x1, _y1, text, block, line, _word_no in words:
        grouped.setdefault((block, line), []).append((x0, y0, text))

    out: list[IndexLine] = []
    for items in grouped.values():
        items.sort(key=lambda item: item[0])
        x0 = items[0][0]
        y0 = items[0][1]
        text = " ".join(item[2] for item in items)
        if y0 < HEADER_Y or y0 > page.rect.height - FOOTER_MARGIN:
            continue
        if PAGE_NUM_RE.match(text):
            continue
        if text.strip().upper() in SECTION_HEADERS:
            continue
        column = 0 if x0 < PAGE_WIDTH_SPLIT else 1
        out.append(IndexLine(column=column, x0=x0, y0=y0, text=text.strip()))
    return out


def _merge_continuations(lines: list[IndexLine]) -> list[IndexLine]:
    merged: list[IndexLine] = []
    for column in (0, 1):
        col_lines = sorted((line for line in lines if line.column == column), key=lambda x: x.y0)
        if not col_lines:
            continue
        base_x = min(line.x0 for line in col_lines)
        current: IndexLine | None = None
        for line in col_lines:
            is_subterm = line.text.startswith("\u2013")
            is_new_heading = line.x0 <= base_x + 6
            if current is not None and not is_subterm and not is_new_heading:
                current.text = f"{current.text} {line.text}"
                continue
            current = IndexLine(
                column=line.column, x0=line.x0, y0=line.y0, text=line.text
            )
            merged.append(current)
    merged.sort(key=lambda x: (x.column, x.y0))
    return merged


def _normalize(term: str) -> str:
    text = term.lower().replace("\u2013", "-").replace("\u2014", "-")
    text = (
        text.replace("\ufb01", "fi")
        .replace("\ufb02", "fl")
        .replace("\ufb00", "ff")
        .replace("\ufb03", "ffi")
        .replace("\ufb04", "ffl")
    )
    text = re.sub(r"[^\w\s\-']", " ", text)
    text = re.sub(r"-{2,}", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_line(line: IndexLine, page_no: int, ord_no: int) -> ParsedIndexTerm | None:
    text = line.text.strip()
    if not text:
        return None
    level_match = LEVEL_RE.match(text)
    prefix = level_match.group(1) if level_match else ""
    level = prefix.count("\u2013")
    rest = text[len(prefix) :].strip()
    if not rest:
        return None

    rest = rest.rstrip(" .;,")
    see_target = see_also_target = None
    kind = "heading" if level == 0 else "term"

    m = SEE_ALSO_RE.search(rest)
    if m:
        see_also_target = m.group(1).strip()
        rest = rest[: m.start()].strip()
        kind = "see_also"
    else:
        m = SEE_RE.search(rest)
        if m:
            see_target = m.group(1).strip()
            rest = rest[: m.start()].strip()
            kind = "see"

    code = None
    m = CODE_RE.search(rest)
    if m:
        code = m.group(1)
        rest = rest[: m.start()].strip()

    if not rest:
        return None
    if kind == "term" and code:
        kind = "term"
    return ParsedIndexTerm(
        term=rest,
        term_norm=_normalize(rest),
        level=level,
        code=code,
        see_target=see_target,
        see_also_target=see_also_target,
        kind=kind,
        page=page_no,
        ord=ord_no,
    )


def parse_index(
    pdf_path: Path, first_page: int = INDEX_FIRST_PAGE, last_page: int = INDEX_LAST_PAGE
) -> IndexResult:
    terms: list[ParsedIndexTerm] = []
    warnings: list[str] = []
    with pymupdf.open(pdf_path) as doc:
        for page_idx in range(first_page - 1, min(last_page, doc.page_count)):
            page = doc[page_idx]
            lines = _merge_continuations(_page_lines(page))
            for ord_no, line in enumerate(lines):
                parsed = _parse_line(line, page_idx + 1, ord_no)
                if parsed is not None:
                    terms.append(parsed)
    return IndexResult(terms=terms, warnings=warnings)
