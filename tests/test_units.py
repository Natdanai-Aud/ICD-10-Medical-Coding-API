from __future__ import annotations

from icd10.importer.parse_index import _normalize
from icd10.importer.parse_tabular import smart_join


def test_smart_join_keeps_hyphen() -> None:
    assert smart_join(["blood-", "forming organs"]) == "blood-forming organs"


def test_smart_join_collapses_spaces() -> None:
    assert smart_join(["Type   2", " diabetes"]) == "Type 2 diabetes"


def test_index_normalize_ligatures() -> None:
    assert _normalize("Classiﬁcation") == "classification"


def test_index_normalize_dashes() -> None:
    assert _normalize("Adenoma––continued") == "adenoma-continued"
