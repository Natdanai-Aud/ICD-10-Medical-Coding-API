from __future__ import annotations

from icd10.api.routers.codes import normalize_code


def test_normalize_code() -> None:
    assert normalize_code(" e11.9 ") == "E11.9"
    assert normalize_code("a00") == "A00"


def test_tabular_counts(tabular) -> None:
    assert len(tabular.chapters) == 22
    assert len(tabular.blocks) == 265
    assert len(tabular.codes) == 12187
    assert sum(1 for c in tabular.codes if c.level == 1) == 2049
    assert sum(1 for c in tabular.codes if c.level == 2) == 10138
    assert not tabular.warnings


def test_tabular_first_and_last_chapter(tabular) -> None:
    first, last = tabular.chapters[0], tabular.chapters[-1]
    assert (first.numeral, first.code_start, first.code_end) == ("I", "A00", "B99")
    assert (last.numeral, last.code_start, last.code_end) == ("XXII", "U00", "U99")


def test_known_codes(tabular) -> None:
    codes = {c.code: c for c in tabular.codes}
    assert codes["E11.9"].title == "Without complications"
    assert codes["A00"].level == 1
    assert codes["B25.0"].dagger is True
    assert codes["D63.0"].asterisk is True
    assert "A00" in codes["A09"].notes[0].text or any(
        "A00" in n.text for n in codes["A09"].notes
    )


def test_shared_subdivisions_expanded(tabular) -> None:
    codes = {c.code for c in tabular.codes}
    for code in ("E10.0", "E11.9", "E14.9", "F10.0", "F19.9", "K25.0", "K28.9"):
        assert code in codes
    assert {"V01.0", "V01.1", "V01.9"} <= codes


def test_index_resolution(tabular, index) -> None:
    valid = {c.code for c in tabular.codes}
    referenced = {t.code for t in index.terms if t.code}
    assert len(index.terms) == 60400
    assert len(referenced) == 8817
    # B12 is a dangling reference in the WHO index itself (D51 is the real code).
    assert referenced - valid == {"B12"}
