import io
from zipfile import ZipFile


def _create_seeded_project(client) -> str:
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
        json={
            "answers": {
                "project_kind": "Web",
                "languages": ["Python", "TypeScript"],
                "frameworks": ["FastAPI", "React"],
                "ai_tools": ["Claude", "Codex", "Cursor"],
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
        },
    )
    return project_id


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
