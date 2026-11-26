from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ICD-10 Medical Coding API"
    api_version: str = "1.0.0"
    dataset_name: str = "ICD-10 WHO 2016 (5th ed.) + Standard Coding Guidelines 2017"

    database_url: str = "postgresql+asyncpg://icd10:icd10@localhost:5432/icd10"

    # off | api_key
    auth_mode: str = "off"
    api_keys: str = ""
    allowed_ips: str = ""

    tesseract_cmd: str = r"C:\Users\natda\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    pdf_dir: Path = PROJECT_ROOT / "pdf"
    data_dir: Path = PROJECT_ROOT / "data"

    default_page_size: int = 20
    max_page_size: int = 200
    max_batch_lookup: int = 500

    @property
    def api_key_set(self) -> set[str]:
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}

    @property
    def allowed_ip_set(self) -> set[str]:
        return {k.strip() for k in self.allowed_ips.split(",") if k.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
