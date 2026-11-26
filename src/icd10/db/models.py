from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from icd10.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class DatasetVersion(Base):
    __tablename__ = "dataset_version"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    source_checksum: Mapped[str | None] = mapped_column(String(64))
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    status: Mapped[str] = mapped_column(String(16), default="draft")  # draft | active | archived
    code_count: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    chapters: Mapped[list[Chapter]] = relationship(back_populates="version")
    codes: Mapped[list[Code]] = relationship(back_populates="version")


class Chapter(Base):
    __tablename__ = "chapter"
    __table_args__ = (UniqueConstraint("version_id", "numeral", name="uq_chapter_version_numeral"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("dataset_version.id", ondelete="CASCADE"))
    numeral: Mapped[str] = mapped_column(String(8))
    title_en: Mapped[str] = mapped_column(Text)
    code_start: Mapped[str] = mapped_column(String(8))
    code_end: Mapped[str] = mapped_column(String(8))
    sort_order: Mapped[int] = mapped_column(Integer)
    notes: Mapped[list[dict[str, str]]] = mapped_column(JSONB, default=list)

    version: Mapped[DatasetVersion] = relationship(back_populates="chapters")
    blocks: Mapped[list[Block]] = relationship(back_populates="chapter")


class Block(Base):
    __tablename__ = "block"
    __table_args__ = (
        UniqueConstraint("chapter_id", "code_start", "code_end", name="uq_block_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapter.id", ondelete="CASCADE"))
    code_start: Mapped[str] = mapped_column(String(8))
    code_end: Mapped[str] = mapped_column(String(8))
    title_en: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer)

    chapter: Mapped[Chapter] = relationship(back_populates="blocks")


class Code(Base):
    __tablename__ = "code"
    __table_args__ = (
        UniqueConstraint("version_id", "code", name="uq_code_version_code"),
        Index("ix_code_parent_id", "parent_id"),
        Index("ix_code_chapter_id", "chapter_id"),
        Index("ix_code_block_id", "block_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("dataset_version.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(8))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("code.id", ondelete="SET NULL"))
    level: Mapped[int] = mapped_column(Integer)  # 1 = three-character category, 2 = four-character
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapter.id", ondelete="CASCADE"))
    block_id: Mapped[int | None] = mapped_column(ForeignKey("block.id", ondelete="SET NULL"))
    title_en: Mapped[str] = mapped_column(Text)
    is_leaf: Mapped[bool] = mapped_column(Boolean, default=False)
    dagger: Mapped[bool] = mapped_column(Boolean, default=False)
    asterisk: Mapped[bool] = mapped_column(Boolean, default=False)
    source_page: Mapped[int | None] = mapped_column(Integer)
    search_text: Mapped[str] = mapped_column(Text, default="")

    version: Mapped[DatasetVersion] = relationship(back_populates="codes")
    parent: Mapped[Code | None] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list[Code]] = relationship(back_populates="parent")
    notes: Mapped[list[CodeNote]] = relationship(
        back_populates="code", cascade="all, delete-orphan", order_by="CodeNote.ord"
    )
    chapter: Mapped[Chapter] = relationship()
    block: Mapped[Block | None] = relationship()


class CodeNote(Base):
    __tablename__ = "code_note"
    __table_args__ = (Index("ix_code_note_code_id", "code_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code_id: Mapped[int] = mapped_column(ForeignKey("code.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(24))  # includes | excludes | note | use_additional
    text: Mapped[str] = mapped_column(Text)
    ord: Mapped[int] = mapped_column(Integer, default=0)

    code: Mapped[Code] = relationship(back_populates="notes")


class CodeRelation(Base):
    __tablename__ = "code_relation"
    __table_args__ = (Index("ix_code_relation_from", "from_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("dataset_version.id", ondelete="CASCADE"))
    from_code: Mapped[str] = mapped_column(String(8))
    to_code: Mapped[str | None] = mapped_column(String(8))
    kind: Mapped[str] = mapped_column(String(24))  # dagger_asterisk | excludes | see | see_also
    raw_ref: Mapped[str] = mapped_column(Text)


class IndexTerm(Base):
    __tablename__ = "index_term"
    __table_args__ = (
        Index("ix_index_term_code", "code"),
        Index("ix_index_term_parent", "parent_id"),
        Index(
            "ix_index_term_trgm",
            "term_norm",
            postgresql_using="gin",
            postgresql_ops={"term_norm": "gin_trgm_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("dataset_version.id", ondelete="CASCADE"))
    term: Mapped[str] = mapped_column(Text)
    term_norm: Mapped[str] = mapped_column(Text)
    level: Mapped[int] = mapped_column(Integer, default=0)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("index_term.id", ondelete="CASCADE"))
    code: Mapped[str | None] = mapped_column(String(8))
    see_target: Mapped[str | None] = mapped_column(Text)
    see_also_target: Mapped[str | None] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(16), default="term")  # term | see | see_also | heading
    ord: Mapped[int] = mapped_column(Integer, default=0)

    parent: Mapped[IndexTerm | None] = relationship(
        remote_side=[id], back_populates="children"
    )
    children: Mapped[list[IndexTerm]] = relationship(back_populates="parent")


class GuidelineSection(Base):
    __tablename__ = "guideline_section"
    __table_args__ = (UniqueConstraint("version_id", "code", name="uq_section_version_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("dataset_version.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(16))
    title_th: Mapped[str] = mapped_column(Text)
    page_start: Mapped[int | None] = mapped_column(Integer)
    page_end: Mapped[int | None] = mapped_column(Integer)


class CaseExample(Base):
    __tablename__ = "case_example"
    __table_args__ = (
        UniqueConstraint("version_id", "example_no", name="uq_case_version_no"),
        Index("ix_case_section", "section_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("dataset_version.id", ondelete="CASCADE"))
    example_no: Mapped[str] = mapped_column(String(16))
    section_id: Mapped[int | None] = mapped_column(
        ForeignKey("guideline_section.id", ondelete="SET NULL")
    )
    page: Mapped[int | None] = mapped_column(Integer)
    scenario_th: Mapped[str] = mapped_column(Text, default="")
    source_ref: Mapped[str | None] = mapped_column(Text)

    lines: Mapped[list[CaseExampleLine]] = relationship(
        back_populates="case", cascade="all, delete-orphan", order_by="CaseExampleLine.ord"
    )


class CaseExampleLine(Base):
    __tablename__ = "case_example_line"
    __table_args__ = (Index("ix_case_line_code", "code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("case_example.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(24))  # principal | other | external_cause | underlying
    diagnosis_text: Mapped[str] = mapped_column(Text)
    code: Mapped[str | None] = mapped_column(String(8))
    code_title_en: Mapped[str | None] = mapped_column(Text)
    code_status: Mapped[str] = mapped_column(String(16), default="unresolved")
    ord: Mapped[int] = mapped_column(Integer, default=0)

    case: Mapped[CaseExample] = relationship(back_populates="lines")
