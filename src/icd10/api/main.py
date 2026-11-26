from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from icd10.api.deps import require_auth
from icd10.api.routers import chapters, codes, examples, health, meta, search
from icd10.api.schemas import Problem
from icd10.core.config import get_settings
from icd10.core.logging import configure_logging

settings = get_settings()
logger = logging.getLogger("icd10.api")

TAGS_METADATA = [
    {"name": "meta", "description": "Dataset versions and licence information"},
    {"name": "hierarchy", "description": "Chapters and blocks"},
    {"name": "codes", "description": "Code lookup, batch lookup, validation and CSV export"},
    {"name": "search", "description": "Free-text search and autocomplete"},
    {"name": "examples", "description": "Case examples from the Thai coding guideline 2017"},
    {"name": "health", "description": "Liveness and readiness"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("starting api")
    yield
    logger.info("stopping api")


app = FastAPI(
    title="ICD-10 Medical Coding API",
    summary="ICD-10 WHO 2016 lookup, hierarchy and search with Thai coding guideline case examples",
    version=settings.api_version,
    description=(
        "Read-only API for hospital information systems. Dataset: ICD-10 WHO 2016 "
        "(5th edition) tabular list and alphabetical index, plus case examples from "
        "the Standard Coding Guidelines 2017 (Thailand).\n\n"
        "The API never accepts patient data; requests contain codes or search terms only."
    ),
    license_info={
        "name": "WHO ICD-10 copyright notice",
        "url": "https://www.who.int/classifications/icd/en/",
    },
    contact={"name": "ICD-10 API maintainers"},
    openapi_tags=TAGS_METADATA,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    problem = Problem(
        title=str(exc.detail) if exc.status_code < 500 else "Internal Server Error",
        status=exc.status_code,
        detail=str(exc.detail) if exc.status_code >= 500 else None,
        instance=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    problem = Problem(
        title="Request validation failed",
        status=422,
        detail=f"{'.'.join(str(x) for x in first.get('loc', []))}: {first.get('msg', '')}",
        instance=request.url.path,
    )
    return JSONResponse(
        status_code=422,
        content=problem.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )


app.include_router(health.router, prefix="/v1")

protected = APIRouter(prefix="/v1", dependencies=[Depends(require_auth)])
protected.include_router(meta.router)
protected.include_router(chapters.router)
protected.include_router(codes.router)
protected.include_router(search.router)
protected.include_router(examples.router)
app.include_router(protected)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "version": settings.api_version,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
