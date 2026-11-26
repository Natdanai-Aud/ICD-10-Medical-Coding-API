from __future__ import annotations

import ipaddress
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from icd10.core.config import get_settings
from icd10.db.models import DatasetVersion
from icd10.db.session import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_active_version(session: SessionDep) -> DatasetVersion:
    version = await session.scalar(
        select(DatasetVersion)
        .where(DatasetVersion.status == "active")
        .order_by(DatasetVersion.imported_at.desc())
        .limit(1)
    )
    if version is None:
        raise HTTPException(status_code=503, detail="no active dataset loaded")
    return version


ActiveVersion = Annotated[DatasetVersion, Depends(get_active_version)]


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


async def require_auth(
    request: Request,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    settings = get_settings()
    if settings.auth_mode == "off":
        return

    if settings.auth_mode != "api_key":
        raise HTTPException(status_code=500, detail="invalid AUTH_MODE")

    if not settings.api_key_set:
        raise HTTPException(status_code=500, detail="AUTH_MODE=api_key but no API_KEYS set")

    if x_api_key not in settings.api_key_set:
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Key")

    allowed = settings.allowed_ip_set
    if allowed:
        ip = _client_ip(request)
        if ip is None:
            raise HTTPException(status_code=403, detail="client ip unavailable")
        address = ipaddress.ip_address(ip)
        if not any(address in ipaddress.ip_network(net, strict=False) for net in allowed):
            raise HTTPException(status_code=403, detail="client ip not allowed")
