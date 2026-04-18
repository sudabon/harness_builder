from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import GeneratedFile, Project
from app.services.answers import get_project_answers

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


@dataclass(frozen=True)
class TemplateDefinition:
    template_name: str
    output_path: str
    required_tool: str | None = None


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


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value in (None, ""):
        return []
    return [str(value)]


def build_template_context(project: Project, answers: dict[str, Any]) -> dict[str, Any]:
    ai_tools = _as_list(answers.get("ai_tools"))
    tests = _as_list(answers.get("test_strategy"))
    lint_tools = _as_list(answers.get("lint_format"))

    return {
        "project_name": project.name,
        "preset_id": project.preset_id or "custom",
        "project_kind": answers.get("project_kind", ""),
        "languages": _as_list(answers.get("languages")),
        "frameworks": _as_list(answers.get("frameworks")),
        "ai_tools": ai_tools,
        "test_strategy": tests,
        "lint_format": lint_tools,
        "prohibited_actions": answers.get("prohibited_actions", ""),
        "review_policy": answers.get("review_policy", ""),
        "branch_strategy": answers.get("branch_strategy", ""),
        "ci_command": answers.get("ci_command", ""),
        "deploy_constraints": answers.get("deploy_constraints", ""),
        "security_requirements": answers.get("security_requirements", ""),
        "failure_examples": answers.get("failure_examples", ""),
        "naming_convention": answers.get("naming_convention", ""),
        "tests_csv": ", ".join(tests) if tests else "未設定",
        "lint_csv": ", ".join(lint_tools) if lint_tools else "未設定",
        "frameworks_csv": ", ".join(_as_list(answers.get("frameworks"))) or "未設定",
        "languages_csv": ", ".join(_as_list(answers.get("languages"))) or "未設定",
        "ai_tools_csv": ", ".join(ai_tools) or "未設定",
    }


def generate_project_files(session: Session, project: Project) -> list[GeneratedFile]:
    answers = get_project_answers(session, project)
    context = build_template_context(project, answers)
    environment = _environment()
    selected_tools = set(_as_list(answers.get("ai_tools")))

    existing = {
        item.file_path: item
        for item in session.scalars(
            select(GeneratedFile).where(GeneratedFile.project_id == project.id)
        ).all()
    }
    generated_items: list[GeneratedFile] = []

    for definition in TEMPLATE_DEFINITIONS:
        if definition.required_tool and definition.required_tool not in selected_tools:
            continue

        content = (
            environment.get_template(definition.template_name).render(**context).strip()
            + "\n"
        )
        current = existing.get(definition.output_path)
        if current:
            current.content = content
            generated_items.append(current)
            continue

        item = GeneratedFile(
            project_id=project.id,
            file_path=definition.output_path,
            content=content,
        )
        session.add(item)
        generated_items.append(item)

    session.flush()
    return generated_items
