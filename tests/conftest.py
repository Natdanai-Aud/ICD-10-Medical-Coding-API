from __future__ import annotations

from pathlib import Path

import pytest

from icd10.importer.parse_index import parse_index
from icd10.importer.parse_tabular import parse_tabular

PDF_DIR = Path(__file__).resolve().parents[1] / "pdf"


def _pdf(pattern: str) -> Path:
    matches = sorted(PDF_DIR.glob(pattern))
    if not matches:
        pytest.skip(f"missing test data: {pattern}")
    return matches[0]


@pytest.fixture(scope="session")
def tabular():
    return parse_tabular(_pdf("ICD10-WHO-2016 Volume 1*.pdf"))


@pytest.fixture(scope="session")
def index():
    return parse_index(_pdf("ICD10-WHO-2016 Volume 3*.pdf"))
