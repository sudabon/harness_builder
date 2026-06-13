from __future__ import annotations

import re
from pathlib import Path

from app.core.presets import PRESETS
from app.core.questionnaire import (
    QUESTIONNAIRE_FIELDS,
    REQUIRED_ANSWER_KEYS,
    missing_required_answer_keys,
    normalize_answers_payload_for_storage,
    normalize_questionnaire_answers,
    validate_answers_payload,
    validate_preset_answers,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_SCHEMA_PATH = (
    REPO_ROOT / "frontend/src/pages/project-wizard/questionnaire-schema.ts"
)


def _fully_answered_required_fields() -> dict[str, object]:
    return {
        "project_kind": "Web",
        "languages": ["Python"],
        "frameworks": ["FastAPI"],
        "ai_tools": ["Codex"],
        "test_strategy": ["pytest"],
        "lint_format": ["ruff"],
        "prohibited_actions": "本番DBの直接変更禁止",
        "review_policy": "厳格",
    }


def _frontend_schema_summary() -> dict[str, dict[str, object]]:
    source = FRONTEND_SCHEMA_PATH.read_text()
    blocks = re.findall(r"\{\n\s+key: \"[^\"]+\"[\s\S]*?\n\s+\},", source)

    summary: dict[str, dict[str, object]] = {}
    for block in blocks:
        key = re.search(r'key: "([^"]+)"', block)
        required = re.search(r"required: (true|false)", block)
        options = re.search(r"options: \[([^\]]*)\]", block)
        assert key is not None
        assert required is not None

        summary[key.group(1)] = {
            "required": required.group(1) == "true",
            "options": tuple(re.findall(r'"([^"]+)"', options.group(1)))
            if options
            else (),
        }

    return summary


def test_required_answer_detection_uses_questionnaire_schema():
    assert REQUIRED_ANSWER_KEYS == (
        "project_kind",
        "languages",
        "frameworks",
        "ai_tools",
        "test_strategy",
        "lint_format",
        "prohibited_actions",
        "review_policy",
    )
    assert missing_required_answer_keys({}) == list(REQUIRED_ANSWER_KEYS)

    answers = _fully_answered_required_fields()
    answers.pop("prohibited_actions")

    assert missing_required_answer_keys(answers) == ["prohibited_actions"]


def test_questionnaire_normalization_preserves_unknown_answers():
    answers = normalize_questionnaire_answers(
        {
            "languages": "Python",
            "prohibited_actions": ["rm -rf 禁止"],
            "future_key": {"custom": True},
        }
    )

    assert answers["languages"] == ["Python"]
    assert answers["prohibited_actions"] == "rm -rf 禁止"
    assert answers["future_key"] == {"custom": True}


def test_presets_match_questionnaire_schema():
    for preset in PRESETS:
        assert validate_preset_answers(preset["answers"]) == []


def test_validate_answers_payload_accepts_valid_answers():
    assert validate_answers_payload(_fully_answered_required_fields()) == []


def test_validate_answers_payload_rejects_invalid_choice():
    errors = validate_answers_payload({"ai_tools": ["claude"]})
    assert errors == ["ai_tools has invalid choices: claude"]
    assert validate_answers_payload({"ai_tools": "claude"}) == [
        "ai_tools has invalid choices: claude"
    ]


def test_validate_answers_payload_accepts_normalizable_shapes():
    assert validate_answers_payload({"ai_tools": "Claude"}) == []
    assert validate_answers_payload({"project_kind": ["Web"]}) == []
    assert validate_answers_payload({"prohibited_actions": ["rm -rf 禁止"]}) == []
    assert validate_answers_payload({"review_policy": ""}) == []


def test_normalize_answers_payload_for_storage_persists_canonical_shapes():
    normalized = normalize_answers_payload_for_storage(
        {
            "project_kind": ["Web"],
            "languages": "Python",
            "ai_tools": "Codex",
            "prohibited_actions": ["rm -rf 禁止"],
            "future_key": {"custom": True},
        }
    )

    assert normalized == {
        "project_kind": "Web",
        "languages": ["Python"],
        "ai_tools": ["Codex"],
        "prohibited_actions": "rm -rf 禁止",
        "future_key": {"custom": True},
    }


def test_validate_answers_payload_passes_unknown_keys_through():
    assert validate_answers_payload({"future_key": {"custom": True}}) == []
    errors = validate_answers_payload(
        {"future_key": "anything", "review_policy": "ゆるい"}
    )
    assert errors == ["review_policy has invalid choice: ゆるい"]


def test_frontend_schema_matches_backend_keys_required_flags_and_options():
    frontend = _frontend_schema_summary()
    backend = {
        field.key: {
            "required": field.required,
            "options": field.options,
        }
        for field in QUESTIONNAIRE_FIELDS
    }

    assert frontend == backend
