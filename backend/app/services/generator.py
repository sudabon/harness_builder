from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.questionnaire import (
    answer_value_as_list,
    normalize_questionnaire_answers,
    project_kind_profile,
)
from app.db.models import GeneratedFile, Project
from app.services.answers import get_project_answers

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
CHANGE_NAME = "setup-ai-harness"
CHANGE_ROOT = f"openspec/changes/{CHANGE_NAME}"


@dataclass(frozen=True)
class TemplateDefinition:
    template_name: str
    output_path: str
    required_tool: str | None = None


@dataclass(frozen=True)
class RenderedTemplate:
    output_path: str
    content: str

    @property
    def markdown_fence(self) -> str:
        longest_backtick_run = max(
            (len(match.group(0)) for match in re.finditer(r"`+", self.content)),
            default=0,
        )
        return "`" * max(4, longest_backtick_run + 1)


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

CHANGE_TEMPLATE_DEFINITIONS = [
    TemplateDefinition("openspec/proposal.md.j2", f"{CHANGE_ROOT}/proposal.md"),
    TemplateDefinition("openspec/design.md.j2", f"{CHANGE_ROOT}/design.md"),
    TemplateDefinition("openspec/tasks.md.j2", f"{CHANGE_ROOT}/tasks.md"),
    TemplateDefinition("openspec/openspec.yaml.j2", f"{CHANGE_ROOT}/.openspec.yaml"),
    TemplateDefinition(
        "openspec/spec.md.j2", f"{CHANGE_ROOT}/specs/ai-coding-harness/spec.md"
    ),
]


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        undefined=StrictUndefined,
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
    project_kind = normalized_answers.get("project_kind", "")
    kind_profile = project_kind_profile(project_kind)

    return {
        "project_name": project.name,
        "preset_id": project.preset_id or "custom",
        "project_kind": project_kind,
        "project_kind_label": kind_profile.label if kind_profile else project_kind,
        "project_kind_focus": kind_profile.focus if kind_profile else "未設定",
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


def _render_all_drafts(
    project: Project, answers: dict[str, Any]
) -> list[RenderedTemplate]:
    context = build_template_context(project, answers)
    environment = _environment()
    normalized_answers = normalize_questionnaire_answers(answers)
    selected_tools = set(answer_value_as_list(normalized_answers.get("ai_tools")))
    definitions = _select_template_definitions(selected_tools)
    return [
        _render_template(environment, definition, context) for definition in definitions
    ]


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
    force: bool,
) -> GeneratedFile:
    current = existing.get(rendered.output_path)
    if current:
        if not current.is_edited or force:
            current.content = rendered.content
            current.is_edited = False
        return current

    item = GeneratedFile(
        project_id=project.id,
        file_path=rendered.output_path,
        content=rendered.content,
    )
    session.add(item)
    return item


def _delete_orphan_generated_files(
    session: Session,
    existing: dict[str, GeneratedFile],
    selected_paths: set[str],
    *,
    force: bool,
) -> list[GeneratedFile]:
    preserved: list[GeneratedFile] = []
    for file_path, item in list(existing.items()):
        if file_path not in selected_paths:
            if item.is_edited and not force:
                logger.info(
                    "Preserving edited orphan generated file: project_id=%s path=%s",
                    item.project_id,
                    file_path,
                )
                preserved.append(item)
                continue
            logger.info(
                "Deleting orphan generated file: project_id=%s path=%s is_edited=%s",
                item.project_id,
                file_path,
                item.is_edited,
            )
            session.delete(item)
            del existing[file_path]
    return preserved


def generate_project_change(
    session: Session, project: Project, *, force: bool = False
) -> list[GeneratedFile]:
    answers = get_project_answers(session, project)
    rendered_drafts = _render_all_drafts(project, answers)
    context = build_template_context(project, answers) | {
        "change_name": CHANGE_NAME,
        "created": date.today().isoformat(),
        "rendered_files": rendered_drafts,
    }
    environment = _environment()
    rendered_change_files = [
        _render_template(environment, definition, context)
        for definition in CHANGE_TEMPLATE_DEFINITIONS
    ]

    existing = _load_existing_generated_files(session, project)
    generated_items = _delete_orphan_generated_files(
        session,
        existing,
        {rendered.output_path for rendered in rendered_change_files},
        force=force,
    )

    for rendered in rendered_change_files:
        generated_items.append(
            _upsert_generated_file(session, project, rendered, existing, force)
        )

    session.flush()
    return generated_items
