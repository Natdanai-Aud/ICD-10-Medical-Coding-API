from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from icd10.api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as http:
        ready = await http.get("/v1/health/ready")
        if ready.status_code != 200 or ready.json().get("status") != "ok":
            pytest.skip("database not loaded")
        yield http


async def test_health(client: AsyncClient) -> None:
    assert (await client.get("/v1/health/live")).status_code == 200
    ready = await client.get("/v1/health/ready")
    assert ready.json()["status"] == "ok"


async def test_meta(client: AsyncClient) -> None:
    response = await client.get("/v1/meta")
    assert response.status_code == 200
    body = response.json()
    assert body["dataset"]["code_count"] == 12187


async def test_code_detail_and_hierarchy(client: AsyncClient) -> None:
    response = await client.get("/v1/codes/E11.9")
    assert response.status_code == 200
    body = response.json()
    assert body["title_en"] == "Without complications"
    assert body["ancestors"][0]["code"] == "E11"

    chapters = (await client.get("/v1/chapters")).json()
    assert len(chapters) == 22
    blocks = (await client.get(f"/v1/chapters/{chapters[0]['id']}/blocks")).json()
    assert blocks[0]["code_start"] == "A00"


async def test_search(client: AsyncClient) -> None:
    response = await client.get("/v1/search", params={"q": "myocardial infarction"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 10
    assert body["items"][0]["code"] == "Z03.4"


async def test_batch_lookup_and_validation(client: AsyncClient) -> None:
    lookup = await client.post(
        "/v1/codes/lookup", json={"codes": ["E11.9", "A00", "B12"]}
    )
    assert lookup.status_code == 200
    assert lookup.json()["not_found"] == ["B12"]

    validation = await client.post(
        "/v1/codes/validate", json={"codes": ["E11.9", "A99"]}
    )
    items = {item["code"]: item for item in validation.json()["items"]}
    assert items["E11.9"]["parent"]["code"] == "E11"
    assert items["A99"]["valid"] is True


async def test_errors(client: AsyncClient) -> None:
    missing = await client.get("/v1/codes/A00.8")
    assert missing.status_code == 404
    assert missing.headers["content-type"].startswith("application/problem+json")

    invalid = await client.get("/v1/codes/not-a-code")
    assert invalid.status_code == 422


async def test_csv_export(client: AsyncClient) -> None:
    response = await client.get("/v1/export/codes.csv")
    assert response.status_code == 200
    lines = response.text.splitlines()
    assert len(lines) == 12188
    assert lines[0].startswith("code,title_en")
