# Notice on data sources and licensing

## ICD-10

The International Classification of Diseases (ICD-10) is published by the World
Health Organization (WHO). It is **not** in the public domain.

- The code titles, tabular structure and alphabetical index in this repository
  are derived from *ICD-10: International Statistical Classification of Diseases
  and Related Health Problems, 5th edition, 2016* (Volumes 1 and 3).
- WHO permits use of ICD-10 for internal, non-commercial purposes such as
  medical records, coding and statistics. Redistribution, public APIs, or
  commercial products require permission from WHO.
- Before exposing this API outside the hospital network, confirm that your
  organisation has the appropriate WHO licence. Do not publish the source PDFs
  or a public dump of the database without permission.

WHO contact: https://www.who.int/classifications/icd/en/

## Thai Standard Coding Guidelines 2017

The case examples are extracted from the Thai Standard Coding Guidelines 2017
(`pdf/Guideline 2017.pdf`). Copyright remains with the original publisher. The
extracted case text is kept for internal coding-reference use only.

## Software

- FastAPI, SQLAlchemy, PostgreSQL — MIT/BSD/PostgreSQL licences.
- PyMuPDF — AGPL (or commercial licence). If you redistribute this service,
  review PyMuPDF's AGPL obligations or replace it with a permissively licensed
  PDF library.
- Tesseract OCR — Apache 2.0.
- `tha.traineddata` from `tessdata_best` — Apache 2.0.

## Patient data

This API does not accept, store or log patient identifiers. Callers must not put
PHI in search queries; use codes and clinical terms only.
