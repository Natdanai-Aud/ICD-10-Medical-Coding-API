from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import fitz
import numpy as np
import pytesseract
from PIL import Image

from icd10.core.config import get_settings

# Example markers in Thai guideline: "ตัวอย่างที่ 12-0" etc. OCR can garble some chars.
EXAMPLE_RE = re.compile(
    r"(?:ตัวอย่างที่|ตัวอย[่้]างที่|ตัวอยางที่|ตัวอย่างท[ี่ี])\s*([0-9OoIl]{1,3}\s*[-–.]\s*[0-9OoIl]{1,3})"
)
CODE_RE = re.compile(r"\b([A-TV-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?)\b")
ROLE_MAP = {
    "หลัก": "principal",
    "principal": "principal",
    "pdx": "principal",
    "วินิจฉัยหลัก": "principal",
    "รอง": "other",
    "other": "other",
    "comorb": "other",
    "วินิจฉัยรอง": "other",
    "สาเหตุภายนอก": "external_cause",
    "external": "external_cause",
    "สาเหตุ": "external_cause",
    "มูลเหตุ": "underlying",
    "underlying": "underlying",
}


@dataclass
class ParsedCaseLine:
    role: str
    diagnosis_text: str
    code: str | None
    code_status: str = "unresolved"
    ord: int = 0


@dataclass
class ParsedCaseExample:
    example_no: str
    page: int
    scenario_th: str
    lines: list[ParsedCaseLine] = field(default_factory=list)
    source_ref: str | None = None


@dataclass
class GuidelineResult:
    sections: list[dict[str, object]]
    examples: list[ParsedCaseExample]
    warnings: list[str]
    review: list[dict[str, object]]


def _norm_example_no(raw: str) -> str:
    cleaned = raw.replace(" ", "").replace("–", "-").replace(".", "-")
    trans = str.maketrans({"O": "0", "o": "0", "I": "1", "l": "1", "S": "5", "B": "8"})
    cleaned = cleaned.translate(trans)
    m = re.match(r"^(\d{1,3})-(\d{1,3})$", cleaned)
    if not m:
        return cleaned
    return f"{int(m.group(1))}-{int(m.group(2))}"


def _norm_code(raw: str | None) -> str | None:
    if not raw:
        return None
    c = raw.upper().strip().replace(" ", "").replace(",", ".")
    # Common OCR confusions in code positions
    if len(c) >= 3:
        chars = list(c)
        for i in (1, 2):
            if chars[i] in "OQ":
                chars[i] = "0"
            if chars[i] in "IL":
                chars[i] = "1"
            if chars[i] == "S":
                chars[i] = "5"
            if chars[i] == "B":
                chars[i] = "8"
        for i in range(4, len(chars)):
            if chars[i] in "OQ":
                chars[i] = "0"
            if chars[i] in "IL":
                chars[i] = "1"
            if chars[i] == "S":
                chars[i] = "5"
            if chars[i] == "B":
                chars[i] = "8"
        c = "".join(chars)
    if not re.match(r"^[A-TV-Z][0-9]{2}[0-9A-Z]?(\.[0-9A-Z]{1,4})?$", c):
        return None
    # Reject implausible 3-char-only noise unless it looks real
    return c


def _detect_role(text: str) -> str:
    low = text.lower()
    for key, role in ROLE_MAP.items():
        if key.lower() in low:
            return role
    return "other"


def _render_page(doc: fitz.Document, page_index: int, dpi: int = 300) -> np.ndarray:
    page = doc[page_index]
    pix = page.get_pixmap(dpi=dpi)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif pix.n == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


def _preprocess(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 15
    )


def _ocr_text(img: np.ndarray, lang: str = "tha+eng", psm: int = 6) -> str:
    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    return pytesseract.image_to_string(Image.fromarray(img), lang=lang, config=f"--psm {psm}")


def _ocr_tsv(img: np.ndarray, lang: str = "tha+eng", psm: int = 6) -> list[dict[str, object]]:
    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    data = pytesseract.image_to_data(
        Image.fromarray(img), lang=lang, config=f"--psm {psm}", output_type=pytesseract.Output.DICT
    )
    rows: list[dict[str, object]] = []
    for i, text in enumerate(data.get("text", [])):
        t = str(text).strip()
        if not t:
            continue
        try:
            conf = float(data["conf"][i])
        except Exception:
            conf = -1.0
        rows.append(
            {
                "text": t,
                "conf": conf,
                "left": int(data["left"][i]),
                "top": int(data["top"][i]),
                "width": int(data["width"][i]),
                "height": int(data["height"][i]),
                "line_num": int(data["line_num"][i]),
                "block_num": int(data["block_num"][i]),
                "par_num": int(data["par_num"][i]),
            }
        )
    return rows


def _extract_codes(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for m in CODE_RE.finditer(text.upper()):
        norm = _norm_code(m.group(1))
        if norm and norm not in seen:
            seen.add(norm)
            out.append(norm)
    return out


def _find_markers(text: str) -> list[tuple[str, int]]:
    found: list[tuple[str, int]] = []
    for m in EXAMPLE_RE.finditer(text):
        found.append((_norm_example_no(m.group(1)), m.start()))
    return found


def _ocr_cell(img: np.ndarray, *, code_mode: bool = False) -> str:
    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    if img.size == 0:
        return ""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 15)
    # add white border to help tesseract
    bw = cv2.copyMakeBorder(bw, 8, 8, 8, 8, cv2.BORDER_CONSTANT, value=255)
    pil = Image.fromarray(bw)
    if code_mode:
        config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789."
        try:
            txt = pytesseract.image_to_string(pil, lang="eng", config=config)
        except Exception:
            txt = ""
    else:
        config = "--psm 6"
        try:
            txt = pytesseract.image_to_string(pil, lang="tha+eng", config=config)
        except Exception:
            txt = ""
    return re.sub(r"\s+", " ", txt).strip()


def _detect_grid_cells(img: np.ndarray) -> list[list[tuple[int, int, int, int]]]:
    """Return rows of cell boxes (x,y,w,h) detected from table grid lines."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bw_inv = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 35, 15
    )
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(40, img.shape[1] // 25), 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(40, img.shape[0] // 25)))
    h_lines = cv2.morphologyEx(bw_inv, cv2.MORPH_OPEN, h_kernel, iterations=2)
    v_lines = cv2.morphologyEx(bw_inv, cv2.MORPH_OPEN, v_kernel, iterations=2)
    grid = cv2.add(h_lines, v_lines)
    contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    raw_boxes: list[tuple[int, int, int, int]] = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w < 60 or h < 25:
            continue
        if w > img.shape[1] * 0.98 and h > img.shape[0] * 0.98:
            continue
        raw_boxes.append((x, y, w, h))
    if len(raw_boxes) < 4:
        return []

    # Cluster boxes into rows by top coordinate
    raw_boxes.sort(key=lambda b: (b[1], b[0]))
    rows: list[list[tuple[int, int, int, int]]] = []
    for box in raw_boxes:
        x, y, w, h = box
        placed = False
        for row in rows:
            ry = sum(b[1] for b in row) / len(row)
            rh = sum(b[3] for b in row) / len(row)
            if abs(y - ry) <= max(15, rh * 0.5):
                row.append(box)
                placed = True
                break
        if not placed:
            rows.append([box])
    # Keep rows with multiple cells, sort cells left-to-right
    out: list[list[tuple[int, int, int, int]]] = []
    for row in rows:
        if len(row) < 2:
            continue
        row.sort(key=lambda b: b[0])
        # dedupe overlapping boxes in same row
        deduped: list[tuple[int, int, int, int]] = []
        for b in row:
            if not deduped:
                deduped.append(b)
                continue
            px, py, pw, ph = deduped[-1]
            if b[0] < px + pw * 0.7:
                # keep larger
                if b[2] * b[3] > pw * ph:
                    deduped[-1] = b
            else:
                deduped.append(b)
        if len(deduped) >= 2:
            out.append(deduped)
    out.sort(key=lambda r: min(b[1] for b in r))
    return out


def _extract_rows_from_grid(img: np.ndarray) -> list[dict[str, str]]:
    """Extract table rows as dicts with text/code candidates from grid cells."""
    rows_cells = _detect_grid_cells(img)
    if not rows_cells:
        return []
    extracted: list[dict[str, str]] = []
    for row in rows_cells:
        cell_texts: list[str] = []
        cell_codes: list[str] = []
        for (x, y, w, h) in row:
            pad = 3
            crop = img[max(0, y + pad): max(0, y + h - pad), max(0, x + pad): max(0, x + w - pad)]
            if crop.size == 0:
                cell_texts.append("")
                continue
            # Try code-mode OCR first for narrow-ish cells or any cell; pick if looks like code
            text_mode = _ocr_cell(crop, code_mode=False)
            code_mode = _ocr_cell(crop, code_mode=True)
            code_norm = _norm_code(code_mode.strip().split()[0]) if code_mode.strip() else None
            if code_norm:
                cell_codes.append(code_norm)
                cell_texts.append(text_mode)
            else:
                # also check text for codes
                found = _extract_codes(text_mode)
                cell_codes.extend(found)
                cell_texts.append(text_mode)
        row_text = " ".join(t for t in cell_texts if t).strip()
        # dedupe codes
        seen: set[str] = set()
        codes: list[str] = []
        for c in cell_codes:
            if c not in seen:
                seen.add(c)
                codes.append(c)
        if row_text or codes:
            extracted.append({"text": row_text, "codes": "|".join(codes)})
    return extracted


def _group_words_by_line(words: list[dict[str, object]]) -> list[list[dict[str, object]]]:
    # Group by (block, par, line_num) when reliable, else by y proximity
    groups: dict[tuple[int, int, int], list[dict[str, object]]] = {}
    for w in words:
        key = (int(w["block_num"]), int(w["par_num"]), int(w["line_num"]))
        groups.setdefault(key, []).append(w)
    lines = [sorted(g, key=lambda x: int(x["left"])) for g in groups.values()]
    lines.sort(key=lambda g: (min(int(w["top"]) for w in g), min(int(w["left"]) for w in g)))
    return lines


def _line_text(line: list[dict[str, object]]) -> str:
    return " ".join(str(w["text"]) for w in line).strip()


def _parse_page(img: np.ndarray, page_num: int) -> list[ParsedCaseExample]:
    bw = _preprocess(img)
    text = _ocr_text(bw, lang="tha+eng", psm=6)
    markers = _find_markers(text)
    if not markers:
        return []

    # TSV line-based parsing
    words = _ocr_tsv(bw, lang="tha+eng", psm=6)
    tsv_lines = _group_words_by_line(words)
    tsv_line_texts = [_line_text(ln) for ln in tsv_lines]

    marker_line_idxs: list[tuple[str, int]] = []
    for i, lt in enumerate(tsv_line_texts):
        for m in EXAMPLE_RE.finditer(lt):
            marker_line_idxs.append((_norm_example_no(m.group(1)), i))
    seen_m: set[tuple[str, int]] = set()
    uniq_markers: list[tuple[str, int]] = []
    for ex_no, idx in marker_line_idxs:
        k = (ex_no, idx)
        if k not in seen_m:
            seen_m.add(k)
            uniq_markers.append(k)

    # Grid-based row extraction (best effort)
    grid_rows = _extract_rows_from_grid(img)
    grid_by_example: dict[str, list[dict[str, str]]] = {}
    if grid_rows:
        current_ex: str | None = None
        for row in grid_rows:
            row_text = row.get("text", "")
            found_markers = _find_markers(row_text)
            if found_markers:
                current_ex = found_markers[0][0]
                grid_by_example.setdefault(current_ex, [])
                # row may also contain data besides marker
            if current_ex:
                grid_by_example.setdefault(current_ex, []).append(row)

    examples: list[ParsedCaseExample] = []
    blocks: list[tuple[str, str]] = []
    for i, (ex_no, pos) in enumerate(markers):
        end = markers[i + 1][1] if i + 1 < len(markers) else len(text)
        blocks.append((ex_no, text[pos:end]))

    if uniq_markers:
        for i, (ex_no, start_idx) in enumerate(uniq_markers):
            end_idx = uniq_markers[i + 1][1] if i + 1 < len(uniq_markers) else len(tsv_lines)
            block_lines = tsv_lines[start_idx:end_idx]
            ex = _parse_example_from_tsv_lines(ex_no, block_lines, page_num)
            # enrich with grid rows for this example
            g_rows = grid_by_example.get(ex_no, [])
            if g_rows:
                _merge_grid_rows(ex, g_rows)
            for bno, btext in blocks:
                if bno == ex_no:
                    scenario = _extract_scenario(btext)
                    if len(scenario) > len(ex.scenario_th):
                        ex.scenario_th = scenario
                    break
            examples.append(ex)
    else:
        for ex_no, block_text in blocks:
            ex = _parse_example_from_text(ex_no, block_text, page_num)
            g_rows = grid_by_example.get(ex_no, [])
            if g_rows:
                _merge_grid_rows(ex, g_rows)
            examples.append(ex)

    return examples


def _merge_grid_rows(ex: ParsedCaseExample, grid_rows: list[dict[str, str]]) -> None:
    existing = {(ln.code, ln.diagnosis_text[:80]) for ln in ex.lines}
    for row in grid_rows:
        row_text = row.get("text", "")
        codes_str = row.get("codes", "")
        codes = [c for c in codes_str.split("|") if c]
        if not codes:
            codes = _extract_codes(row_text)
        if not codes:
            continue
        diag = _clean_diag_text(row_text)
        role = _detect_role(row_text)
        for c in codes:
            key = (c, diag[:80])
            if key in existing:
                continue
            existing.add(key)
            ex.lines.append(
                ParsedCaseLine(
                    role=role,
                    diagnosis_text=diag if diag else row_text[:200],
                    code=c,
                    code_status="unresolved",
                    ord=len(ex.lines),
                )
            )


def _extract_scenario(block_text: str) -> str:
    lines = [ln.strip() for ln in block_text.splitlines() if ln.strip()]
    scenario_parts: list[str] = []
    for ln in lines:
        if EXAMPLE_RE.search(ln) and not scenario_parts:
            remainder = EXAMPLE_RE.sub("", ln).strip(" :-\t|")
            if remainder:
                scenario_parts.append(remainder)
            continue
        if _extract_codes(ln):
            break
        if len(" ".join(scenario_parts)) < 600 and not re.match(r"^[\W\d_]+$", ln):
            clean = re.sub(r"[|]{2,}", " ", ln).strip()
            if clean:
                scenario_parts.append(clean)
    scenario = re.sub(r"\s+", " ", " ".join(scenario_parts)).strip()
    return scenario[:2000]


def _clean_diag_text(text: str) -> str:
    text = CODE_RE.sub("", text)
    text = re.sub(r"[|]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text).strip(" :-\t")
    return text


def _parse_example_from_tsv_lines(
    ex_no: str, lines: list[list[dict[str, object]]], page_num: int
) -> ParsedCaseExample:
    scenario_parts: list[str] = []
    case_lines: list[ParsedCaseLine] = []
    seen: set[tuple[str | None, str]] = set()
    marker_seen = False

    for line_words in lines:
        lt = _line_text(line_words)
        if not lt:
            continue
        has_marker = bool(EXAMPLE_RE.search(lt))
        if has_marker and not marker_seen:
            marker_seen = True
            remainder = EXAMPLE_RE.sub("", lt).strip(" :-\t|")
            if remainder and not _extract_codes(remainder):
                scenario_parts.append(remainder)
            # a marker line can also contain codes in same row - handle below
            if not _extract_codes(lt):
                continue

        codes = _extract_codes(lt)
        if codes:
            role = _detect_role(lt)
            diag = _clean_diag_text(lt)
            # if diagnosis is very short, try borrowing from adjacent non-code text in same line
            if len(diag) < 3:
                diag = lt.strip()
            for c in codes:
                key = (c, diag[:80])
                if key in seen:
                    continue
                seen.add(key)
                case_lines.append(
                    ParsedCaseLine(
                        role=role,
                        diagnosis_text=diag,
                        code=c,
                        code_status="unresolved",
                        ord=len(case_lines),
                    )
                )
        else:
            if not case_lines and len(" ".join(scenario_parts)) < 600:
                clean = re.sub(r"[|]{2,}", " ", lt).strip()
                if clean and not re.match(r"^[\W\d_]+$", clean):
                    scenario_parts.append(clean)

    # If no lines found, try a looser pass: scan all text for codes
    if not case_lines:
        all_text = " ".join(_line_text(ln) for ln in lines)
        for c in _extract_codes(all_text):
            key = (c, "")
            if key not in seen:
                seen.add(key)
                case_lines.append(
                    ParsedCaseLine(
                        role="other",
                        diagnosis_text="",
                        code=c,
                        code_status="unresolved",
                        ord=len(case_lines),
                    )
                )

    scenario = re.sub(r"\s+", " ", " ".join(scenario_parts)).strip()[:2000]
    return ParsedCaseExample(
        example_no=ex_no,
        page=page_num,
        scenario_th=scenario,
        lines=case_lines,
        source_ref=f"Guideline 2017 p.{page_num} example {ex_no}",
    )


def _parse_example_from_text(ex_no: str, block_text: str, page_num: int) -> ParsedCaseExample:
    # simple fallback
    fake_line = [
        {
            "text": t,
            "conf": 0,
            "left": 0,
            "top": i,
            "width": 0,
            "height": 0,
            "line_num": i,
            "block_num": 0,
            "par_num": 0,
        }
        for i, t in enumerate(block_text.splitlines())
        if t.strip()
    ]
    # group each as its own line
    lines = [[w] for w in fake_line]
    return _parse_example_from_tsv_lines(ex_no, lines, page_num)


def parse_guideline(
    pdf_path: Path,
    *,
    page_start: int = 1,
    page_end: int | None = None,
    dpi: int = 300,
) -> GuidelineResult:
    settings = get_settings()
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    doc = fitz.open(pdf_path)
    total = len(doc)
    start = max(1, page_start)
    end = min(total, page_end or total)

    examples_by_no: dict[str, ParsedCaseExample] = {}
    warnings: list[str] = []
    review: list[dict[str, object]] = []

    for page_num in range(start, end + 1):
        try:
            img = _render_page(doc, page_num - 1, dpi=dpi)
            parsed_examples = _parse_page(img, page_num)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"page {page_num}: OCR failed: {exc}")
            continue

        for ex in parsed_examples:
            if not ex.lines:
                warnings.append(
                    f"page {page_num}: example {ex.example_no} has no parseable code lines"
                )
            review.append(
                {
                    "page": page_num,
                    "example_no": ex.example_no,
                    "line_count": len(ex.lines),
                    "codes": [ln.code for ln in ex.lines if ln.code],
                    "scenario_preview": ex.scenario_th[:120],
                }
            )
            existing = examples_by_no.get(ex.example_no)
            if existing is None:
                examples_by_no[ex.example_no] = ex
            else:
                existing_keys = {(ln.code, ln.diagnosis_text[:80]) for ln in existing.lines}
                for ln in ex.lines:
                    k = (ln.code, ln.diagnosis_text[:80])
                    if k not in existing_keys:
                        ln.ord = len(existing.lines)
                        existing.lines.append(ln)
                        existing_keys.add(k)
                if len(ex.scenario_th) > len(existing.scenario_th):
                    existing.scenario_th = ex.scenario_th

    def _sort_key(e: ParsedCaseExample) -> tuple[int, int, str]:
        parts = e.example_no.split("-")
        nums = []
        for p in parts:
            try:
                nums.append(int(p))
            except ValueError:
                nums.append(9999)
        while len(nums) < 2:
            nums.append(0)
        return (nums[0], nums[1], e.example_no)

    examples = sorted(examples_by_no.values(), key=_sort_key)
    return GuidelineResult(sections=[], examples=examples, warnings=warnings, review=review)
