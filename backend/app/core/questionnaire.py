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


@dataclass(frozen=True)
class ProjectKindProfile:
    value: str
    label: str
    description: str
    focus: str


PROJECT_KIND_PROFILES: tuple[ProjectKindProfile, ...] = (
    ProjectKindProfile(
        value="Web",
        label="Webアプリ",
        description="ブラウザで使う画面体験が主役のリポジトリ。",
        focus="UI状態、アクセシビリティ、E2E、画面回帰を重視する。",
    ),
    ProjectKindProfile(
        value="API",
        label="APIサービス",
        description="外部または内部システムへ機能を提供するサービス。",
        focus="API契約、認証、エラー設計、互換性、負荷を重視する。",
    ),
    ProjectKindProfile(
        value="OSS",
        label="OSS / ライブラリ",
        description="公開・再利用・配布されるパッケージやCLI。",
        focus="README、SemVer、破壊的変更、リリース手順を重視する。",
    ),
    ProjectKindProfile(
        value="SaaS",
        label="SaaSプロダクト",
        description="顧客向けに継続運用するプロダクト。",
        focus="テナント分離、課金、監査ログ、SLO、セキュリティを重視する。",
    ),
)
PROJECT_KIND_OPTIONS = tuple(profile.value for profile in PROJECT_KIND_PROFILES)
PROJECT_KIND_PROFILE_BY_VALUE = {
    profile.value: profile for profile in PROJECT_KIND_PROFILES
}


QUESTIONNAIRE_FIELDS: tuple[QuestionDefinition, ...] = (
    QuestionDefinition(
        key="project_kind",
        label="成果物タイプ",
        input_type="single_choice",
        required=True,
        default="",
        options=PROJECT_KIND_OPTIONS,
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
        options=("FastAPI", "React", "Next.js", "Django", "Echo", "Buf"),
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
        options=("pytest", "vitest", "testing", "jest", "playwright"),
    ),
    QuestionDefinition(
        key="lint_format",
        label="lint_format",
        input_type="multi_choice",
        required=True,
        default=(),
        options=("ruff", "mypy", "eslint", "prettier", "gofmt", "golangci-lint"),
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


def project_kind_profile(value: Any) -> ProjectKindProfile | None:
    project_kind = answer_value_as_string(value)
    return PROJECT_KIND_PROFILE_BY_VALUE.get(project_kind)


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
    normalized_value = normalize_answer_value(key, value)
    if field.input_type == "multi_choice":
        values = answer_value_as_list(normalized_value)
        invalid = [item for item in values if item not in field.options]
        if invalid:
            errors.append(f"{key} has invalid choices: {', '.join(invalid)}")
        return errors

    value_as_string = answer_value_as_string(normalized_value)
    if field.options and value_as_string and value_as_string not in field.options:
        errors.append(f"{key} has invalid choice: {value_as_string}")
    return errors


def validate_answers_payload(answers: dict[str, Any]) -> list[str]:
    """Validate values for known questionnaire keys (normalization handled per-value).

    Unknown keys are intentionally passed through without validation to allow the
    schema to evolve (forward-compat); their values are stored verbatim.
    """
    errors: list[str] = []
    for key, value in answers.items():
        if key not in QUESTIONNAIRE_BY_KEY:
            continue
        errors.extend(validate_known_answer_value(key, value))
    return errors


def normalize_answers_payload_for_storage(answers: dict[str, Any]) -> dict[str, Any]:
    """Normalize known questionnaire keys before persisting; unknown keys pass through.

    Unknown keys are kept as-is for forward-compat (see ``validate_answers_payload``).
    """
    return {
        key: (
            normalize_answer_value(key, value) if key in QUESTIONNAIRE_BY_KEY else value
        )
        for key, value in answers.items()
    }


def validate_preset_answers(answers: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, value in answers.items():
        errors.extend(validate_known_answer_value(key, value))
    return errors
