from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.core.config import get_settings


BACKEND_DIR = Path(__file__).resolve().parents[1]
EXPECTED_TABLES = {
    "alembic_version",
    "generated_files",
    "projects",
    "questionnaire_answers",
    "users",
}


def _alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def _column_names(inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _foreign_key_targets(inspector, table_name: str) -> set[tuple[str, str, str]]:
    targets: set[tuple[str, str, str]] = set()
    for foreign_key in inspector.get_foreign_keys(table_name):
        referred_table = foreign_key["referred_table"]
        for column, referred_column in zip(
            foreign_key["constrained_columns"],
            foreign_key["referred_columns"],
            strict=True,
        ):
            targets.add((column, referred_table, referred_column))
    return targets


def _unique_constraint_names(inspector, table_name: str) -> set[str]:
    return {
        constraint["name"]
        for constraint in inspector.get_unique_constraints(table_name)
    }


def _index_names(inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def test_alembic_upgrade_head_creates_expected_schema(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'migration-test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()

    try:
        command.upgrade(_alembic_config(database_url), "head")

        engine = create_engine(database_url, future=True)
        inspector = inspect(engine)

        assert set(inspector.get_table_names()) == EXPECTED_TABLES
        assert _column_names(inspector, "users") == {
            "id",
            "email",
            "password_hash",
            "created_at",
            "updated_at",
        }
        assert _column_names(inspector, "projects") == {
            "id",
            "user_id",
            "name",
            "preset_id",
            "created_at",
            "updated_at",
        }
        assert _column_names(inspector, "questionnaire_answers") == {
            "id",
            "project_id",
            "question_key",
            "answer_value",
            "created_at",
            "updated_at",
        }
        assert _column_names(inspector, "generated_files") == {
            "id",
            "project_id",
            "file_path",
            "content",
            "is_edited",
            "created_at",
            "updated_at",
        }

        assert _foreign_key_targets(inspector, "projects") == {
            ("user_id", "users", "id")
        }
        assert _foreign_key_targets(inspector, "questionnaire_answers") == {
            ("project_id", "projects", "id")
        }
        assert _foreign_key_targets(inspector, "generated_files") == {
            ("project_id", "projects", "id")
        }

        assert "uq_questionnaire_answers_key" in _unique_constraint_names(
            inspector, "questionnaire_answers"
        )
        assert "uq_generated_files_path" in _unique_constraint_names(
            inspector, "generated_files"
        )
        assert "ix_users_email" in _index_names(inspector, "users")
        assert "ix_projects_user_id" in _index_names(inspector, "projects")
        assert "ix_questionnaire_answers_project_id" in _index_names(
            inspector, "questionnaire_answers"
        )
        assert "ix_generated_files_project_id" in _index_names(
            inspector, "generated_files"
        )
    finally:
        get_settings.cache_clear()


def test_alembic_downgrade_removes_is_edited_column(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'migration-downgrade-test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()

    try:
        config = _alembic_config(database_url)
        command.upgrade(config, "head")
        command.downgrade(config, "20260418_0001")

        engine = create_engine(database_url, future=True)
        inspector = inspect(engine)

        assert "is_edited" not in _column_names(inspector, "generated_files")

        command.upgrade(config, "head")
        inspector = inspect(create_engine(database_url, future=True))
        assert "is_edited" in _column_names(inspector, "generated_files")
    finally:
        get_settings.cache_clear()
