from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

AnswerInputType = Literal["single_choice", "multi_choice", "text", "textarea"]


@dataclass(frozen=True)
class QuestionDefinition:
    key: str
    label: str
    input_type: AnswerInputType
    required: bool
    default: str | tuple[str, ...]
    options: tuple[str, ...] = ()

    def default_value(self) -> str | list[str]:
        if isinstance(self.default, tuple):
            return list(self.default)
        return self.default


QUESTIONNAIRE_FIELDS: tuple[QuestionDefinition, ...] = (
    QuestionDefinition(
        key="project_kind",
        label="プロジェクト種別",
        input_type="single_choice",
        required=True,
        default="",
        options=("Web", "API", "OSS", "SaaS"),
    ),
    QuestionDefinition(
        key="languages",
        label="languages",
        input_type="multi_choice",
        required=True,
        default=(),
        options=("Python", "TypeScript", "Go", "Rust"),
    ),
    QuestionDefinition(
        key="frameworks",
        label="frameworks",
        input_type="multi_choice",
        required=True,
        default=(),
        options=("FastAPI", "React", "Next.js", "Django"),
    ),
    QuestionDefinition(
        key="ai_tools",
        label="ai_tools",
        input_type="multi_choice",
        required=True,
        default=(),
        options=("Claude", "Codex", "Cursor"),
    ),
    QuestionDefinition(
        key="test_strategy",
        label="test_strategy",
        input_type="multi_choice",
        required=True,
        default=(),
        options=("pytest", "jest", "playwright"),
    ),
    QuestionDefinition(
        key="lint_format",
        label="lint_format",
        input_type="multi_choice",
        required=True,
        default=(),
        options=("ruff", "eslint", "prettier"),
    ),
    QuestionDefinition(
        key="prohibited_actions",
        label="禁止事項",
        input_type="textarea",
        required=True,
        default="",
    ),
    QuestionDefinition(
        key="review_policy",
        label="レビュー方針",
        input_type="single_choice",
        required=True,
        default="",
        options=("厳格", "柔軟"),
    ),
    QuestionDefinition(
        key="branch_strategy",
        label="ブランチ戦略",
        input_type="text",
        required=False,
        default="",
    ),
    QuestionDefinition(
        key="ci_command",
        label="CI コマンド",
        input_type="text",
        required=False,
        default="",
    ),
    QuestionDefinition(
        key="deploy_constraints",
        label="デプロイ制約",
        input_type="textarea",
        required=False,
        default="",
    ),
    QuestionDefinition(
        key="security_requirements",
        label="セキュリティ要件",
        input_type="textarea",
        required=False,
        default="",
    ),
    QuestionDefinition(
        key="failure_examples",
        label="過去の失敗事例",
        input_type="textarea",
        required=False,
        default="",
    ),
    QuestionDefinition(
        key="naming_convention",
        label="命名規約",
        input_type="text",
        required=False,
        default="",
    ),
)

QUESTIONNAIRE_BY_KEY = {field.key: field for field in QUESTIONNAIRE_FIELDS}
REQUIRED_ANSWER_KEYS = tuple(
    field.key for field in QUESTIONNAIRE_FIELDS if field.required
)


def answer_value_as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value in (None, ""):
        return []
    return [str(value)]


def answer_value_as_string(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def normalize_answer_value(key: str, value: Any) -> Any:
    field = QUESTIONNAIRE_BY_KEY.get(key)
    if field is None:
        return value
    if field.input_type == "multi_choice":
        return answer_value_as_list(value)
    return answer_value_as_string(value)


def normalize_questionnaire_answers(answers: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        field.key: normalize_answer_value(
            field.key, answers.get(field.key, field.default_value())
        )
        for field in QUESTIONNAIRE_FIELDS
    }
    normalized.update(
        {
            key: value
            for key, value in answers.items()
            if key not in QUESTIONNAIRE_BY_KEY
        }
    )
    return normalized


def missing_required_answer_keys(answers: dict[str, Any]) -> list[str]:
    normalized = normalize_questionnaire_answers(answers)
    missing: list[str] = []
    for key in REQUIRED_ANSWER_KEYS:
        value = normalized[key]
        if isinstance(value, list):
            if len(value) == 0:
                missing.append(key)
        elif not value:
            missing.append(key)
    return missing


def validate_known_answer_value(key: str, value: Any) -> list[str]:
    field = QUESTIONNAIRE_BY_KEY.get(key)
    if field is None:
        return [f"Unknown answer key: {key}"]

    errors: list[str] = []
    if field.input_type == "multi_choice":
        if not isinstance(value, list):
            return [f"{key} must be a list"]
        values = [str(item) for item in value]
        invalid = [item for item in values if item not in field.options]
        if invalid:
            errors.append(f"{key} has invalid choices: {', '.join(invalid)}")
        return errors

    if not isinstance(value, str):
        return [f"{key} must be a string"]
    if field.options and value not in field.options:
        errors.append(f"{key} has invalid choice: {value}")
    return errors


def validate_preset_answers(answers: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, value in answers.items():
        errors.extend(validate_known_answer_value(key, value))
    return errors
