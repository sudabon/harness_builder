import io
from zipfile import ZipFile

from app.services.answers import answer_value_as_list


COMMON_GENERATED_PATHS = {
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


def test_answer_value_as_list_preserves_existing_normalization():
    assert answer_value_as_list(None) == []
    assert answer_value_as_list("") == []
    assert answer_value_as_list("Codex") == ["Codex"]
    assert answer_value_as_list(["Codex", 1]) == ["Codex", "1"]


def test_generate_codex_only_includes_common_and_codex_templates(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200

    paths = {item["file_path"] for item in generated.json()["items"]}
    assert paths == COMMON_GENERATED_PATHS | {TOOL_SPECIFIC_PATHS["Codex"]}
    assert TOOL_SPECIFIC_PATHS["Claude"] not in paths
    assert TOOL_SPECIFIC_PATHS["Cursor"] not in paths


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
        json={"answers": {"project_kind": "CLI"}},
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

    agent_file_id = second_ids_by_path["AGENTS.md"]
    detail = client.get(f"/api/v1/projects/{project_id}/files/{agent_file_id}")
    assert detail.status_code == 200
    assert "Project kind: CLI" in detail.json()["content"]


def test_export_uses_saved_file_paths_and_current_contents(client):
    project_id = _create_seeded_project(client, ai_tools=["Codex"])

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200
    codex_file = next(
        item
        for item in generated.json()["items"]
        if item["file_path"] == TOOL_SPECIFIC_PATHS["Codex"]
    )

    edited_content = "# Edited Codex Rules\n\n保存済みの内容です。\n"
    updated = client.put(
        f"/api/v1/projects/{project_id}/files/{codex_file['id']}",
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
    assert archived_contents[TOOL_SPECIFIC_PATHS["Codex"]] == edited_content


def test_generate_edit_and_export_files(client):
    project_id = _create_seeded_project(client)

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200
    items = generated.json()["items"]
    assert len(items) >= 10

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

    assert "AGENTS.md" in names
    assert "scripts/verify.sh" in names
    assert exported_content == "# Updated\n"
