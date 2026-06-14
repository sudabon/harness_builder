import io
from datetime import date
from zipfile import ZipFile

import pytest
from jinja2 import UndefinedError

from app.services.answers import answer_value_as_list
from app.services.generator import _environment


CHANGE_ROOT = "openspec/changes/setup-ai-harness"
PROPOSAL_PATH = f"{CHANGE_ROOT}/proposal.md"
TASKS_PATH = f"{CHANGE_ROOT}/tasks.md"
OPENSPEC_CONFIG_PATH = f"{CHANGE_ROOT}/.openspec.yaml"
SPEC_PATH = f"{CHANGE_ROOT}/specs/ai-coding-harness/spec.md"

CHANGE_PACKAGE_PATHS = {
    PROPOSAL_PATH,
    TASKS_PATH,
    OPENSPEC_CONFIG_PATH,
    SPEC_PATH,
}

COMMON_DRAFT_PATHS = {
    "AGENTS.md",
    "PROJECT_RULES.md",
    "prompts/feature.md",
    "prompts/bugfix.md",
    "prompts/review.md",
    "definition_of_done.md",
    "review_checklist.md",
    "test_strategy.md",
    "scripts/verify.sh",
}

TOOL_SPECIFIC_PATHS = {
    "Claude": "CLAUDE.md",
    "Codex": ".codex/rules/general.md",
    "Cursor": ".cursor/rules/project.mdc",
}


def _required_answers(ai_tools: list[str] | None = None) -> dict[str, object]:
    return {
        "project_kind": "Web",
        "languages": ["Python", "TypeScript"],
        "frameworks": ["FastAPI", "React"],
        "ai_tools": ai_tools or ["Claude", "Codex", "Cursor"],
        "test_strategy": ["pytest", "jest"],
        "lint_format": ["ruff", "eslint", "prettier"],
        "prohibited_actions": "rm -rf 禁止",
        "review_policy": "厳格",
        "branch_strategy": "trunk-based",
        "ci_command": "pnpm lint && uv run pytest",
        "deploy_constraints": "平日昼のみ",
        "security_requirements": "機密情報は環境変数で管理",
        "failure_examples": "mainへ未レビューのまま直pushした",
        "naming_convention": "kebab-case / snake_case を用途で統一",
    }


def _create_seeded_project(client, ai_tools: list[str] | None = None) -> str:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "supersecret"},
    )
    created = client.post(
        "/api/v1/projects",
        json={"name": "Harness Demo", "preset_id": "fastapi-react"},
    )
    project_id = created.json()["id"]
    client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={"answers": _required_answers(ai_tools)},
    )
    return project_id


def _file_contents_by_path(client, project_id: str) -> dict[str, str]:
    files = client.get(f"/api/v1/projects/{project_id}/files")
    assert files.status_code == 200

    contents: dict[str, str] = {}
    for file in files.json()["items"]:
        detail = client.get(f"/api/v1/projects/{project_id}/files/{file['id']}")
        assert detail.status_code == 200
        body = detail.json()
        contents[body["file_path"]] = body["content"]
    return contents


def _tasks_content(client, project_id: str) -> str:
    return _file_contents_by_path(client, project_id)[TASKS_PATH]


def test_answer_value_as_list_preserves_existing_normalization():
    assert answer_value_as_list(None) == []
    assert answer_value_as_list("") == []
    assert answer_value_as_list("Codex") == ["Codex"]
    assert answer_value_as_list(["Codex", 1]) == ["Codex", "1"]


def test_generate_codex_only_includes_change_package_with_common_and_codex_drafts(
    client,
):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200

    paths = {item["file_path"] for item in generated.json()["items"]}
    assert paths == CHANGE_PACKAGE_PATHS

    tasks = _tasks_content(client, project_id)
    for draft_path in COMMON_DRAFT_PATHS | {TOOL_SPECIFIC_PATHS["Codex"]}:
        assert f"`{draft_path}`" in tasks
    assert f"`{TOOL_SPECIFIC_PATHS['Claude']}`" not in tasks
    assert f"`{TOOL_SPECIFIC_PATHS['Cursor']}`" not in tasks


def test_change_package_files_include_expected_openspec_content(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200

    contents = _file_contents_by_path(client, project_id)
    assert contents[OPENSPEC_CONFIG_PATH] == (
        f"schema: spec-driven\ncreated: {date.today().isoformat()}\n"
    )

    proposal = contents[PROPOSAL_PATH]
    assert "# Proposal: setup-ai-harness" in proposal
    assert "Harness Demo" in proposal
    assert "Project kind: Web" in proposal
    assert "Languages: Python, TypeScript" in proposal
    assert "Frameworks: FastAPI, React" in proposal
    assert "AI tools: Codex" in proposal

    spec = contents[SPEC_PATH]
    assert "# Delta: ai-coding-harness" in spec
    assert "## ADDED Requirements" in spec
    assert "### Requirement:" in spec
    assert "#### Scenario:" in spec
    assert "/opsx:apply setup-ai-harness" in spec


def test_tasks_draft_fence_handles_answers_containing_backticks(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])
    updated = client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={
            "answers": {
                "failure_examples": "事故例:\n```bash\nrm -rf .\n```",
            }
        },
    )
    assert updated.status_code == 200

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200

    tasks = _tasks_content(client, project_id)
    assert "````text\n# PROJECT_RULES.md" in tasks
    assert "```bash\nrm -rf .\n```" in tasks


def test_template_environment_rejects_missing_variables():
    with pytest.raises(UndefinedError):
        _environment().from_string("{{ missing_value }}").render()


def test_generate_reports_schema_required_answers(client):
    project_id = _create_seeded_project(client)

    updated = client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={"answers": {"prohibited_actions": ""}},
    )
    assert updated.status_code == 200

    generated = client.post(f"/api/v1/projects/{project_id}/generate")

    assert generated.status_code == 400
    assert generated.json()["detail"] == "Missing required answers: prohibited_actions"


def test_regenerate_updates_existing_files_without_duplicate_paths(client):
    project_id = _create_seeded_project(client)

    first = client.post(f"/api/v1/projects/{project_id}/generate")
    assert first.status_code == 200
    first_ids_by_path = {
        item["file_path"]: item["id"] for item in first.json()["items"]
    }

    updated = client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={"answers": {"project_kind": "API"}},
    )
    assert updated.status_code == 200

    second = client.post(f"/api/v1/projects/{project_id}/generate")
    assert second.status_code == 200

    files = client.get(f"/api/v1/projects/{project_id}/files")
    assert files.status_code == 200
    paths = [item["file_path"] for item in files.json()["items"]]
    second_ids_by_path = {
        item["file_path"]: item["id"] for item in files.json()["items"]
    }

    assert len(paths) == len(set(paths))
    assert second_ids_by_path == first_ids_by_path

    tasks_file_id = second_ids_by_path[TASKS_PATH]
    detail = client.get(f"/api/v1/projects/{project_id}/files/{tasks_file_id}")
    assert detail.status_code == 200
    assert "Project kind: API" in detail.json()["content"]


def test_regenerate_removes_files_for_deselected_tools(client):
    project_id = _create_seeded_project(client, ai_tools=["Claude", "Cursor"])

    first = client.post(f"/api/v1/projects/{project_id}/generate")
    assert first.status_code == 200
    first_paths = {item["file_path"] for item in first.json()["items"]}
    assert first_paths == CHANGE_PACKAGE_PATHS
    assert f"`{TOOL_SPECIFIC_PATHS['Cursor']}`" in _tasks_content(client, project_id)

    updated = client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={"answers": {"ai_tools": ["Claude"]}},
    )
    assert updated.status_code == 200

    second = client.post(f"/api/v1/projects/{project_id}/generate")
    assert second.status_code == 200
    second_paths = {item["file_path"] for item in second.json()["items"]}
    assert second_paths == CHANGE_PACKAGE_PATHS
    tasks = _tasks_content(client, project_id)
    assert f"`{TOOL_SPECIFIC_PATHS['Claude']}`" in tasks
    assert f"`{TOOL_SPECIFIC_PATHS['Cursor']}`" not in tasks

    files = client.get(f"/api/v1/projects/{project_id}/files")
    assert files.status_code == 200
    listed_paths = {item["file_path"] for item in files.json()["items"]}
    assert listed_paths == CHANGE_PACKAGE_PATHS

    exported = client.get(f"/api/v1/projects/{project_id}/export")
    assert exported.status_code == 200
    with ZipFile(io.BytesIO(exported.content)) as archive:
        names = set(archive.namelist())
        archived_tasks = archive.read(TASKS_PATH).decode()
    assert names == CHANGE_PACKAGE_PATHS
    assert f"`{TOOL_SPECIFIC_PATHS['Cursor']}`" not in archived_tasks
    assert f"`{TOOL_SPECIFIC_PATHS['Claude']}`" in archived_tasks


def test_regenerate_removes_files_not_in_template_definitions(client, session):
    from app.db.models import GeneratedFile

    project_id = _create_seeded_project(client, ai_tools=["Codex"])

    first = client.post(f"/api/v1/projects/{project_id}/generate")
    assert first.status_code == 200

    session.add(
        GeneratedFile(
            project_id=project_id,
            file_path="legacy/old_template.md",
            content="# Legacy\n",
        )
    )
    session.commit()

    second = client.post(f"/api/v1/projects/{project_id}/generate")
    assert second.status_code == 200

    files = client.get(f"/api/v1/projects/{project_id}/files")
    listed_paths = {item["file_path"] for item in files.json()["items"]}
    assert "legacy/old_template.md" not in listed_paths

    exported = client.get(f"/api/v1/projects/{project_id}/export")
    assert exported.status_code == 200
    with ZipFile(io.BytesIO(exported.content)) as archive:
        names = set(archive.namelist())
    assert "legacy/old_template.md" not in names
    assert names == CHANGE_PACKAGE_PATHS


def test_export_uses_saved_file_paths_and_current_contents(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200
    tasks_file = next(
        item for item in generated.json()["items"] if item["file_path"] == TASKS_PATH
    )

    edited_content = "# Edited OpenSpec Tasks\n\n保存済みの内容です。\n"
    updated = client.put(
        f"/api/v1/projects/{project_id}/files/{tasks_file['id']}",
        json={"content": edited_content},
    )
    assert updated.status_code == 200

    expected_contents = _file_contents_by_path(client, project_id)
    exported = client.get(f"/api/v1/projects/{project_id}/export")
    assert exported.status_code == 200
    assert exported.headers["content-type"] == "application/zip"

    with ZipFile(io.BytesIO(exported.content)) as archive:
        names = set(archive.namelist())
        archived_contents = {
            name: archive.read(name).decode() for name in archive.namelist()
        }

    assert names == set(expected_contents)
    assert archived_contents == expected_contents
    assert archived_contents[TASKS_PATH] == edited_content


def _generate_and_get_file(client, project_id: str, file_path: str) -> dict:
    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200
    return next(
        item for item in generated.json()["items"] if item["file_path"] == file_path
    )


def test_update_file_marks_edited_only_when_content_changes(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])
    tasks_file = _generate_and_get_file(client, project_id, TASKS_PATH)
    original_content = client.get(
        f"/api/v1/projects/{project_id}/files/{tasks_file['id']}"
    ).json()["content"]

    unchanged = client.put(
        f"/api/v1/projects/{project_id}/files/{tasks_file['id']}",
        json={"content": original_content},
    )
    assert unchanged.status_code == 200
    assert unchanged.json()["is_edited"] is False

    changed = client.put(
        f"/api/v1/projects/{project_id}/files/{tasks_file['id']}",
        json={"content": "# 手動編集済み\n"},
    )
    assert changed.status_code == 200
    assert changed.json()["is_edited"] is True


def test_generate_response_is_sorted_by_file_path(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200

    paths = [item["file_path"] for item in generated.json()["items"]]
    assert paths == sorted(paths)


def test_edited_file_is_protected_from_normal_regeneration(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])
    tasks_file = _generate_and_get_file(client, project_id, TASKS_PATH)
    assert tasks_file["is_edited"] is False

    edited_content = "# 手動編集済み tasks\n"
    updated = client.put(
        f"/api/v1/projects/{project_id}/files/{tasks_file['id']}",
        json={"content": edited_content},
    )
    assert updated.status_code == 200
    assert updated.json()["is_edited"] is True

    regenerated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert regenerated.status_code == 200
    regenerated_tasks = next(
        item for item in regenerated.json()["items"] if item["file_path"] == TASKS_PATH
    )
    assert regenerated_tasks["is_edited"] is True

    detail = client.get(f"/api/v1/projects/{project_id}/files/{tasks_file['id']}")
    assert detail.json()["content"] == edited_content

    # 未編集ファイルはテンプレート出力で更新される
    contents = _file_contents_by_path(client, project_id)
    assert contents[PROPOSAL_PATH] != edited_content


def test_force_regeneration_overwrites_edited_file_and_resets_flag(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])
    tasks_file = _generate_and_get_file(client, project_id, TASKS_PATH)
    original_content = client.get(
        f"/api/v1/projects/{project_id}/files/{tasks_file['id']}"
    ).json()["content"]

    client.put(
        f"/api/v1/projects/{project_id}/files/{tasks_file['id']}",
        json={"content": "# 手動編集済み\n"},
    )

    forced = client.post(
        f"/api/v1/projects/{project_id}/generate", json={"force": True}
    )
    assert forced.status_code == 200
    forced_tasks = next(
        item for item in forced.json()["items"] if item["file_path"] == TASKS_PATH
    )
    assert forced_tasks["is_edited"] is False

    detail = client.get(f"/api/v1/projects/{project_id}/files/{tasks_file['id']}")
    assert detail.json()["content"] == original_content
    assert detail.json()["is_edited"] is False


def test_normal_regeneration_preserves_edited_orphan_files(client, session):
    from app.db.models import GeneratedFile

    project_id = _create_seeded_project(client, ai_tools=["Claude", "Cursor"])
    client.post(f"/api/v1/projects/{project_id}/generate")

    session.add(
        GeneratedFile(
            project_id=project_id,
            file_path="legacy/edited.md",
            content="# 編集済みレガシー\n",
            is_edited=True,
        )
    )
    session.commit()

    regenerated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert regenerated.status_code == 200
    paths = {item["file_path"] for item in regenerated.json()["items"]}
    assert paths == CHANGE_PACKAGE_PATHS | {"legacy/edited.md"}

    files = client.get(f"/api/v1/projects/{project_id}/files")
    listed_paths = {item["file_path"] for item in files.json()["items"]}
    assert "legacy/edited.md" in listed_paths

    exported = client.get(f"/api/v1/projects/{project_id}/export")
    assert exported.status_code == 200
    with ZipFile(io.BytesIO(exported.content)) as archive:
        names = set(archive.namelist())
        preserved_content = archive.read("legacy/edited.md").decode()
    assert "legacy/edited.md" in names
    assert preserved_content == "# 編集済みレガシー\n"


def test_force_regeneration_removes_edited_orphan_files(client, session):
    from app.db.models import GeneratedFile

    project_id = _create_seeded_project(client, ai_tools=["Claude", "Cursor"])
    client.post(f"/api/v1/projects/{project_id}/generate")

    session.add(
        GeneratedFile(
            project_id=project_id,
            file_path="legacy/edited.md",
            content="# 編集済みレガシー\n",
            is_edited=True,
        )
    )
    session.commit()

    regenerated = client.post(
        f"/api/v1/projects/{project_id}/generate", json={"force": True}
    )
    assert regenerated.status_code == 200
    paths = {item["file_path"] for item in regenerated.json()["items"]}
    assert paths == CHANGE_PACKAGE_PATHS

    files = client.get(f"/api/v1/projects/{project_id}/files")
    listed_paths = {item["file_path"] for item in files.json()["items"]}
    assert "legacy/edited.md" not in listed_paths


def test_verify_sh_supports_playwright(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])
    client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={"answers": {"test_strategy": ["pytest", "jest", "playwright"]}},
    )

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200

    tasks = _tasks_content(client, project_id)
    assert "pnpm exec playwright test" in tasks
    assert "Skipping unsupported test tool" not in tasks


def test_generate_edit_and_export_files(client):
    project_id = _create_seeded_project(client)

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200
    items = generated.json()["items"]
    assert len(items) == len(CHANGE_PACKAGE_PATHS)

    files = client.get(f"/api/v1/projects/{project_id}/files")
    assert files.status_code == 200
    file_id = files.json()["items"][0]["id"]

    detail = client.get(f"/api/v1/projects/{project_id}/files/{file_id}")
    assert detail.status_code == 200
    assert detail.json()["content"]
    file_path = detail.json()["file_path"]

    updated = client.put(
        f"/api/v1/projects/{project_id}/files/{file_id}",
        json={"content": "# Updated\n"},
    )
    assert updated.status_code == 200
    assert updated.json()["content"] == "# Updated\n"

    exported = client.get(f"/api/v1/projects/{project_id}/export")
    assert exported.status_code == 200
    assert exported.headers["content-type"] == "application/zip"

    with ZipFile(io.BytesIO(exported.content)) as archive:
        names = set(archive.namelist())
        exported_content = archive.read(file_path).decode()

    assert PROPOSAL_PATH in names
    assert TASKS_PATH in names
    assert exported_content == "# Updated\n"
