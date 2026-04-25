from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.questionnaire import (
    answer_value_as_list,
    normalize_questionnaire_answers,
)
from app.db.models import GeneratedFile, Project
from app.services.answers import get_project_answers

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


@dataclass(frozen=True)
class TemplateDefinition:
    template_name: str
    output_path: str
    required_tool: str | None = None


@dataclass(frozen=True)
class RenderedTemplate:
    output_path: str
    content: str


TEMPLATE_DEFINITIONS = [
    TemplateDefinition("agent_rules/AGENTS.md.j2", "AGENTS.md"),
    TemplateDefinition("agent_rules/PROJECT_RULES.md.j2", "PROJECT_RULES.md"),
    TemplateDefinition("tool_configs/CLAUDE.md.j2", "CLAUDE.md", "Claude"),
    TemplateDefinition(
        "tool_configs/codex.general.md.j2", ".codex/rules/general.md", "Codex"
    ),
    TemplateDefinition(
        "tool_configs/cursor.project.mdc.j2", ".cursor/rules/project.mdc", "Cursor"
    ),
    TemplateDefinition("prompts/feature.md.j2", "prompts/feature.md"),
    TemplateDefinition("prompts/bugfix.md.j2", "prompts/bugfix.md"),
    TemplateDefinition("prompts/review.md.j2", "prompts/review.md"),
    TemplateDefinition("quality/definition_of_done.md.j2", "definition_of_done.md"),
    TemplateDefinition("quality/review_checklist.md.j2", "review_checklist.md"),
    TemplateDefinition("quality/test_strategy.md.j2", "test_strategy.md"),
    TemplateDefinition("scripts/verify.sh.j2", "scripts/verify.sh"),
]


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def build_template_context(project: Project, answers: dict[str, Any]) -> dict[str, Any]:
    normalized_answers = normalize_questionnaire_answers(answers)
    ai_tools = answer_value_as_list(normalized_answers.get("ai_tools"))
    tests = answer_value_as_list(normalized_answers.get("test_strategy"))
    lint_tools = answer_value_as_list(normalized_answers.get("lint_format"))
    frameworks = answer_value_as_list(normalized_answers.get("frameworks"))
    languages = answer_value_as_list(normalized_answers.get("languages"))

    return {
        "project_name": project.name,
        "preset_id": project.preset_id or "custom",
        "project_kind": normalized_answers.get("project_kind", ""),
        "languages": languages,
        "frameworks": frameworks,
        "ai_tools": ai_tools,
        "test_strategy": tests,
        "lint_format": lint_tools,
        "prohibited_actions": normalized_answers.get("prohibited_actions", ""),
        "review_policy": normalized_answers.get("review_policy", ""),
        "branch_strategy": normalized_answers.get("branch_strategy", ""),
        "ci_command": normalized_answers.get("ci_command", ""),
        "deploy_constraints": normalized_answers.get("deploy_constraints", ""),
        "security_requirements": normalized_answers.get("security_requirements", ""),
        "failure_examples": normalized_answers.get("failure_examples", ""),
        "naming_convention": normalized_answers.get("naming_convention", ""),
        "tests_csv": ", ".join(tests) if tests else "未設定",
        "lint_csv": ", ".join(lint_tools) if lint_tools else "未設定",
        "frameworks_csv": ", ".join(frameworks) or "未設定",
        "languages_csv": ", ".join(languages) or "未設定",
        "ai_tools_csv": ", ".join(ai_tools) or "未設定",
    }


def _template_matches_tools(
    definition: TemplateDefinition, selected_tools: set[str]
) -> bool:
    return (
        definition.required_tool is None or definition.required_tool in selected_tools
    )


def _select_template_definitions(selected_tools: set[str]) -> list[TemplateDefinition]:
    return [
        definition
        for definition in TEMPLATE_DEFINITIONS
        if _template_matches_tools(definition, selected_tools)
    ]


def _render_template(
    environment: Environment,
    definition: TemplateDefinition,
    context: dict[str, Any],
) -> RenderedTemplate:
    content = (
        environment.get_template(definition.template_name).render(**context).strip()
        + "\n"
    )
    return RenderedTemplate(output_path=definition.output_path, content=content)


def _load_existing_generated_files(
    session: Session, project: Project
) -> dict[str, GeneratedFile]:
    return {
        item.file_path: item
        for item in session.scalars(
            select(GeneratedFile).where(GeneratedFile.project_id == project.id)
        ).all()
    }


def _upsert_generated_file(
    session: Session,
    project: Project,
    rendered: RenderedTemplate,
    existing: dict[str, GeneratedFile],
) -> GeneratedFile:
    current = existing.get(rendered.output_path)
    if current:
        current.content = rendered.content
        return current

    item = GeneratedFile(
        project_id=project.id,
        file_path=rendered.output_path,
        content=rendered.content,
    )
    session.add(item)
    return item


def generate_project_files(session: Session, project: Project) -> list[GeneratedFile]:
    answers = get_project_answers(session, project)
    context = build_template_context(project, answers)
    environment = _environment()
    normalized_answers = normalize_questionnaire_answers(answers)
    selected_tools = set(answer_value_as_list(normalized_answers.get("ai_tools")))
    definitions = _select_template_definitions(selected_tools)
    existing = _load_existing_generated_files(session, project)
    generated_items: list[GeneratedFile] = []

    for definition in definitions:
        rendered = _render_template(environment, definition, context)
        generated_items.append(
            _upsert_generated_file(session, project, rendered, existing)
        )

    session.flush()
    return generated_items
