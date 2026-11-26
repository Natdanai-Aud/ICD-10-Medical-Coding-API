from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

_PDFTOTEXT = shutil.which("pdftotext") or "pdftotext"

# Page furniture that must never reach the parser.
_NOISE_PATTERNS = [
    re.compile(r"^\s*INTERNATIONAL CLASSIFICATION OF DISEASES\s*$"),
    re.compile(r"^\s*Vol1_B&W\.indb.*$"),
    re.compile(r"^\s*Vol3_Index.*$"),
    re.compile(r"^\s*\d{1,4}\s*$"),
]
_ALL_CAPS_RE = re.compile(r"^[A-Z][A-Z0-9 ,;:\-\(\)/]+$")


def page_count(pdf_path: Path) -> int:
    with pymupdf.open(pdf_path) as doc:
        return doc.page_count


def extract_layout_pages(pdf_path: Path) -> list[list[str]]:
    """Return page -> lines using poppler's layout mode (preserves indentation/columns)."""
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    result = subprocess.run(
        [_PDFTOTEXT, "-layout", "-enc", "UTF-8", str(pdf_path), "-"],
        capture_output=True,
        check=True,
    )
    text = result.stdout.decode("utf-8", errors="replace")
    return [page.splitlines() for page in text.split("\f")]


def is_noise(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("Vol1_B&W") or stripped.startswith("Vol3_"):
        return True
    if any(p.match(line) for p in _NOISE_PATTERNS):
        return True
    # running headers are all caps; keep the left-aligned "CHAPTER X" marker
    return bool(
        len(stripped) >= 10
        and _ALL_CAPS_RE.match(stripped)
        and not CHAPTER_HEADER_RE.match(line)
    )


def clean_lines(lines: list[str]) -> list[str]:
    return ["" if is_noise(line) else line.rstrip() for line in lines]


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


_HYPHEN_END = re.compile(r"[A-Za-z]-$")


def smart_join(parts: list[str]) -> str:
    """Join wrapped lines, repairing hyphenation and keeping bullets readable."""
    out = ""
    for raw in parts:
        part = raw.strip()
        if not part:
            continue
        if not out:
            out = part
        elif out.endswith("-") and _HYPHEN_END.search(out) and part[:1].islower():
            out = out + part
        else:
            out = out + " " + part
    return re.sub(r"\s+", " ", out).strip()


@dataclass
class ParsedNote:
    kind: str
    text: str


@dataclass
class ParsedChapter:
    numeral: str
    title: str
    code_start: str
    code_end: str
    sort_order: int
    page: int
    notes: list[ParsedNote] = field(default_factory=list)


@dataclass
class ParsedBlock:
    chapter_numeral: str
    code_start: str
    code_end: str
    title: str
    sort_order: int


@dataclass
class ParsedCode:
    code: str
    title: str
    level: int
    chapter_numeral: str
    dagger: bool
    asterisk: bool
    page: int
    notes: list[ParsedNote] = field(default_factory=list)


@dataclass
class TabularResult:
    chapters: list[ParsedChapter]
    blocks: list[ParsedBlock]
    codes: list[ParsedCode]
    warnings: list[str] = field(default_factory=list)


@dataclass
class FlatLine:
    page: int
    text: str


NOTE_KEYWORDS: list[tuple[str, str]] = [
    ("Use additional external cause code", "use_additional"),
    ("Use additional code", "use_additional"),
    ("Incl.:", "includes"),
    ("Excl.:", "excludes"),
    ("Note:", "note"),
]

CHAPTER_RANGE_RE = re.compile(r"^\s*\(([A-Z]\d{2})[\u2013\-]([A-Z]\d{2})\)\s*$")
CHAPTER_HEADER_RE = re.compile(r"^\s{0,20}CHAPTER\s+([IVX]+)\s*$")
BLOCK_RE = re.compile(r"^\s*([A-Z]\d{2})[\u2013\-]([A-Z]\d{2})\s+(\S.*)$")
CODE_RE = re.compile(r"^\s*([A-Z]\d{2}(?:\.\d)?)([\u2020*])?\s+(\S.*)$")
SUBDIV_RE = re.compile(r"^\s*\.(\d)([\u2020*])?\s+(\S.*)$")
SUBDIV_BARE_RE = re.compile(r"^\s*(\d)([\u2020*])?\s{2,}(\S.*)$")
CAT_RANGE_RE = re.compile(r"categor(?:y|ies)\s+([A-Z]\d{2})\s*[\u2013\-]\s*([A-Z]\d{2})")


def _note_kind(line: str) -> str | None:
    stripped = line.strip()
    for prefix, kind in NOTE_KEYWORDS:
        if stripped.startswith(prefix):
            return kind
    return None


def _note_text(line: str, kind: str) -> str:
    stripped = line.strip()
    for prefix, k in NOTE_KEYWORDS:
        if k == kind and stripped.startswith(prefix):
            return stripped[len(prefix) :].strip()
    return stripped


def _flatten(pages: list[list[str]]) -> list[FlatLine]:
    return [FlatLine(page=p + 1, text=line) for p, lines in enumerate(pages) for line in lines]


def parse_tabular(pdf_path: Path) -> TabularResult:
    pages = extract_layout_pages(pdf_path)
    flat = _flatten([clean_lines(p) for p in pages])

    warnings: list[str] = []
    chapters, chapter_starts = _parse_chapters(flat, warnings)
    if not chapters:
        raise ValueError("no chapters detected")

    blocks = _parse_blocks(flat, chapter_starts, warnings)
    codes = _parse_codes(flat, chapters, chapter_starts[0][0], warnings)
    shared = _parse_shared_subdivisions(flat, codes, warnings)
    for code in shared:
        codes.setdefault(code.code, code)

    return TabularResult(
        chapters=chapters,
        blocks=blocks,
        codes=list(codes.values()),
        warnings=warnings,
    )


def _parse_chapters(
    flat: list[FlatLine], warnings: list[str]
) -> tuple[list[ParsedChapter], list[tuple[int, ParsedChapter]]]:
    chapters: list[ParsedChapter] = []
    starts: list[tuple[int, ParsedChapter]] = []
    for i, fl in enumerate(flat):
        nm = CHAPTER_HEADER_RE.match(fl.text)
        if not nm:
            continue
        numeral = nm.group(1)
        title_lines: list[str] = []
        found: tuple[str, str, int] | None = None
        j = i + 1
        scanned = 0
        while j < len(flat) and scanned < 60:
            text = flat[j].text
            stripped = text.strip()
            if not stripped:
                j += 1
                continue
            scanned += 1
            rm = CHAPTER_RANGE_RE.match(text)
            if rm:
                found = (rm.group(1), rm.group(2), j)
                break
            if CHAPTER_HEADER_RE.match(text) or CODE_RE.match(text):
                break
            if indent_of(text) <= 20:
                title_lines.append(stripped)
            j += 1
        if not found or not title_lines:
            continue
        chapter = ParsedChapter(
            numeral=numeral,
            title=smart_join(title_lines),
            code_start=found[0],
            code_end=found[1],
            sort_order=len(chapters) + 1,
            page=flat[found[2]].page,
        )
        chapters.append(chapter)
        starts.append((found[2], chapter))

    if len(chapters) != 22:
        warnings.append(f"expected 22 chapters, found {len(chapters)}")
    return chapters, starts


def _parse_blocks(
    flat: list[FlatLine], chapter_starts: list[tuple[int, ParsedChapter]], warnings: list[str]
) -> list[ParsedBlock]:
    blocks: list[ParsedBlock] = []
    for range_idx, chapter in chapter_starts:
        marker = None
        for j in range(range_idx + 1, min(range_idx + 120, len(flat))):
            if flat[j].text.strip().startswith("This chapter contains the following blocks"):
                marker = j
                break
        if marker is None:
            warnings.append(f"block list not found for chapter {chapter.numeral}")
            continue

        # chapter-level notes live between the range line and the block list
        note_kind: str | None = None
        note_parts: list[str] = []
        for j in range(range_idx + 1, marker):
            text = flat[j].text
            stripped = text.strip()
            if not stripped:
                continue
            kind = _note_kind(text)
            if kind:
                if note_kind and note_parts:
                    chapter.notes.append(ParsedNote(note_kind, smart_join(note_parts)))
                note_kind, note_parts = kind, [_note_text(text, kind)]
            elif note_kind:
                note_parts.append(stripped)
        if note_kind and note_parts:
            chapter.notes.append(ParsedNote(note_kind, smart_join(note_parts)))

        order = 0
        current: list[str] | None = None
        current_range: tuple[str, str] | None = None
        for j in range(marker + 1, min(marker + 250, len(flat))):
            text = flat[j].text
            stripped = text.strip()
            if not stripped:
                continue
            m = BLOCK_RE.match(text)
            if m:
                if current and current_range:
                    order += 1
                    blocks.append(
                        ParsedBlock(
                            chapter_numeral=chapter.numeral,
                            code_start=current_range[0],
                            code_end=current_range[1],
                            title=smart_join(current),
                            sort_order=order,
                        )
                    )
                current_range = (m.group(1), m.group(2))
                current = [m.group(3)]
                continue
            if current is not None and indent_of(text) >= 8 and not CODE_RE.match(text):
                current.append(stripped)
                continue
            break
        if current and current_range:
            order += 1
            blocks.append(
                ParsedBlock(
                    chapter_numeral=chapter.numeral,
                    code_start=current_range[0],
                    code_end=current_range[1],
                    title=smart_join(current),
                    sort_order=order,
                )
            )
    return blocks


def _parse_codes(
    flat: list[FlatLine],
    chapters: list[ParsedChapter],
    first_idx: int,
    warnings: list[str],
) -> dict[str, ParsedCode]:
    codes: dict[str, ParsedCode] = {}
    i = first_idx
    while i < len(flat):
        text = flat[i].text
        m = CODE_RE.match(text)
        if not m:
            i += 1
            continue
        code, marker, first_title = m.group(1), m.group(2) or "", m.group(3)
        if code in codes:
            i += 1
            continue
        title_indent = text.index(first_title)
        title_parts = [first_title]
        notes: list[ParsedNote] = []
        j = i + 1
        in_title = True
        while j < len(flat):
            nxt = flat[j].text
            if not nxt.strip():
                j += 1
                continue
            if CODE_RE.match(nxt):
                break
            kind = _note_kind(nxt)
            if kind:
                in_title = False
                note_parts = [_note_text(nxt, kind)]
                note_indent = indent_of(nxt)
                k = j + 1
                while k < len(flat):
                    cand = flat[k].text
                    if not cand.strip():
                        k += 1
                        continue
                    if CODE_RE.match(cand) or _note_kind(cand):
                        break
                    if indent_of(cand) >= note_indent + 2:
                        note_parts.append(cand.strip())
                        k += 1
                        continue
                    break
                notes.append(ParsedNote(kind, smart_join(note_parts)))
                j = k
                continue
            if in_title and abs(indent_of(nxt) - title_indent) <= 1:
                title_parts.append(nxt)
                j += 1
                continue
            break

        chapter = _chapter_for(code, chapters)
        if chapter is None:
            warnings.append(f"code {code} outside chapter ranges (page {flat[i].page})")
            i = j
            continue
        codes[code] = ParsedCode(
            code=code,
            title=smart_join(title_parts),
            level=1 if "." not in code else 2,
            chapter_numeral=chapter.numeral,
            dagger="\u2020" in marker,
            asterisk="*" in marker,
            page=flat[i].page,
            notes=notes,
        )
        i = j
    return codes


def _subdiv_match(line: str) -> re.Match[str] | None:
    return SUBDIV_RE.match(line) or SUBDIV_BARE_RE.match(line)


def _parse_shared_subdivisions(
    flat: list[FlatLine],
    codes: dict[str, ParsedCode],
    warnings: list[str],
) -> list[ParsedCode]:
    """Expand 'The following fourth-character subdivisions ... categories X-Y' blocks.

    WHO ICD-10 lists the fourth character once for a family of categories
    (E10-E14, F10-F19, K25-K28, V01-V06, ...).  Those codes are not present as
    literal lines in the tabular list, so they must be generated.
    """
    out: list[ParsedCode] = []
    i = 0
    while i < len(flat):
        if not flat[i].text.strip().startswith("The following fourth-character subdivisions"):
            i += 1
            continue

        stmt_parts = [flat[i].text.strip()]
        j = i + 1
        while j < len(flat) and j < i + 60:
            text = flat[j].text
            if _subdiv_match(text) or CODE_RE.match(text):
                break
            if text.strip():
                stmt_parts.append(text.strip())
            j += 1

        m = CAT_RANGE_RE.search(" ".join(stmt_parts))
        if not m:
            warnings.append(f"shared subdivision range not found (page {flat[i].page})")
            i = j
            continue
        start, end = m.group(1), m.group(2)
        categories = sorted(
            c.code for c in codes.values() if c.level == 1 and start <= c.code <= end
        )
        if not categories:
            warnings.append(
                f"shared subdivision categories {start}-{end} missing (page {flat[i].page})"
            )
            i = j
            continue

        entries: list[tuple[str, str, str, list[ParsedNote]]] = []
        while j < len(flat) and j < i + 600:
            text = flat[j].text
            em = _subdiv_match(text)
            if not em:
                if CODE_RE.match(text) or "fourth-character subdivisions" in text:
                    break
                j += 1
                continue
            digit = em.group(1)
            marker = em.group(2) or ""
            title = em.group(3).strip()
            entry_indent = indent_of(text)
            include_parts: list[str] = []
            notes: list[ParsedNote] = []
            k = j + 1
            while k < len(flat):
                cand = flat[k].text
                if not cand.strip():
                    k += 1
                    continue
                if _subdiv_match(cand) or CODE_RE.match(cand):
                    break
                if indent_of(cand) <= entry_indent:
                    break
                kind = _note_kind(cand)
                if kind:
                    note_parts = [_note_text(cand, kind)]
                    note_indent = indent_of(cand)
                    kk = k + 1
                    while kk < len(flat):
                        cc = flat[kk].text
                        if not cc.strip():
                            kk += 1
                            continue
                        if _subdiv_match(cc) or CODE_RE.match(cc) or _note_kind(cc):
                            break
                        if indent_of(cc) >= note_indent + 2:
                            note_parts.append(cc.strip())
                            kk += 1
                            continue
                        break
                    notes.append(ParsedNote(kind, smart_join(note_parts)))
                    k = kk
                    continue
                include_parts.append(cand.strip())
                k += 1
            if include_parts:
                notes.insert(0, ParsedNote("includes", smart_join(include_parts)))
            entries.append((digit, marker, title, notes))
            j = k

        for cat in categories:
            parent = codes[cat]
            for digit, marker, title, notes in entries:
                code = f"{cat}.{digit}"
                if code in codes:
                    continue
                out.append(
                    ParsedCode(
                        code=code,
                        title=title,
                        level=2,
                        chapter_numeral=parent.chapter_numeral,
                        dagger="\u2020" in marker,
                        asterisk="*" in marker,
                        page=flat[i].page,
                        notes=list(notes),
                    )
                )
        i = j
    return out


def _chapter_for(code: str, chapters: list[ParsedChapter]) -> ParsedChapter | None:
    key = code[:3]
    for chapter in chapters:
        if chapter.code_start <= key <= chapter.code_end:
            return chapter
    return None
