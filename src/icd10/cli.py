from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from icd10.core.config import get_settings
from icd10.importer.load import file_checksum, init_db, load_dataset, load_guideline_examples
from icd10.importer.parse_guideline import parse_guideline
from icd10.importer.parse_index import parse_index
from icd10.importer.parse_tabular import parse_tabular


def _find_pdf(pattern: str) -> Path:
    matches = sorted(get_settings().pdf_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"no PDF matching {pattern!r} in {get_settings().pdf_dir}")
    return matches[0]


async def _import_icd(skip_index: bool) -> None:
    tabular_pdf = _find_pdf("ICD10-WHO-2016 Volume 1*.pdf")
    print(f"parsing {tabular_pdf.name} ...")
    tabular = parse_tabular(tabular_pdf)
    print(
        f"  chapters={len(tabular.chapters)} blocks={len(tabular.blocks)} "
        f"codes={len(tabular.codes)} warnings={len(tabular.warnings)}"
    )

    index = None
    source_paths = [tabular_pdf]
    if not skip_index:
        index_pdf = _find_pdf("ICD10-WHO-2016 Volume 3*.pdf")
        print(f"parsing {index_pdf.name} ...")
        index = parse_index(index_pdf)
        source_paths.append(index_pdf)
        print(f"  index terms={len(index.terms)}")

    print("initialising schema ...")
    await init_db()
    print("loading dataset ...")
    meta = await load_dataset(
        tabular=tabular,
        index=index,
        source_checksum=file_checksum(source_paths),
    )
    print(json.dumps(meta, indent=2, ensure_ascii=False))


async def _import_guideline(page_start: int, page_end: int | None, dpi: int) -> None:
    guideline_pdf = _find_pdf("Guideline 2017*.pdf")
    print(f"parsing {guideline_pdf.name} pages {page_start}-{page_end or 'end'} dpi={dpi} ...")
    result = parse_guideline(guideline_pdf, page_start=page_start, page_end=page_end, dpi=dpi)
    print(
        f"  examples={len(result.examples)} "
        f"lines={sum(len(e.lines) for e in result.examples)} "
        f"warnings={len(result.warnings)}"
    )
    report_path = Path("data/guideline-review.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "examples": len(result.examples),
                "warnings": result.warnings,
                "review": result.review,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"  review report: {report_path}")
    print("loading guideline examples ...")
    meta = await load_guideline_examples(
        result,
        source_checksum=file_checksum([guideline_pdf]),
    )
    print(json.dumps(meta, indent=2, ensure_ascii=False))


def _export_openapi(output: Path) -> None:
    from icd10.api.main import app

    spec = app.openapi()
    output.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {output} ({output.stat().st_size} bytes, {len(spec['paths'])} paths)")


def main() -> None:
    parser = argparse.ArgumentParser(prog="icd10", description="ICD-10 data tooling")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="create extension and tables")

    import_cmd = sub.add_parser("import-icd", help="parse WHO PDFs and load PostgreSQL")
    import_cmd.add_argument("--skip-index", action="store_true")

    gl_cmd = sub.add_parser("import-guideline", help="OCR Guideline 2017 and load case examples")
    gl_cmd.add_argument("--page-start", type=int, default=1)
    gl_cmd.add_argument("--page-end", type=int, default=None)
    gl_cmd.add_argument("--dpi", type=int, default=300)

    export_cmd = sub.add_parser("export-openapi", help="write the OpenAPI document")
    export_cmd.add_argument(
        "--output", type=Path, default=Path("ICD-10 Medical Coding API.json")
    )

    serve_cmd = sub.add_parser("serve", help="run the API server")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8000)
    serve_cmd.add_argument("--reload", action="store_true")

    args = parser.parse_args()
    if args.command == "init-db":
        asyncio.run(init_db())
        print("schema ready")
    elif args.command == "import-icd":
        asyncio.run(_import_icd(args.skip_index))
    elif args.command == "import-guideline":
        asyncio.run(_import_guideline(args.page_start, args.page_end, args.dpi))
    elif args.command == "export-openapi":
        _export_openapi(args.output)
    elif args.command == "serve":
        import uvicorn

        uvicorn.run(
            "icd10.api.main:app", host=args.host, port=args.port, reload=args.reload
        )


if __name__ == "__main__":
    main()
