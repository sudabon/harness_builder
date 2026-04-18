from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime, String


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    projects: Mapped[list["Project"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    preset_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped[User] = relationship(back_populates="projects")
    answers: Mapped[list["QuestionnaireAnswer"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    generated_files: Mapped[list["GeneratedFile"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class QuestionnaireAnswer(TimestampMixin, Base):
    __tablename__ = "questionnaire_answers"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "question_key", name="uq_questionnaire_answers_key"
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    question_key: Mapped[str] = mapped_column(String(100))
    answer_value: Mapped[str] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="answers")


class GeneratedFile(TimestampMixin, Base):
    __tablename__ = "generated_files"
    __table_args__ = (
        UniqueConstraint("project_id", "file_path", name="uq_generated_files_path"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    file_path: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="generated_files")
