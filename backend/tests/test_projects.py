import io
from zipfile import ZipFile


CHANGE_ROOT = "openspec/changes/setup-ai-harness"
CHANGE_PACKAGE_PATHS = {
    f"{CHANGE_ROOT}/proposal.md",
    f"{CHANGE_ROOT}/design.md",
    f"{CHANGE_ROOT}/tasks.md",
    f"{CHANGE_ROOT}/.openspec.yaml",
    f"{CHANGE_ROOT}/specs/ai-coding-harness/spec.md",
}


def _register(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "supersecret"},
    )


def test_create_project_and_save_answers(client):
    _register(client)

    created = client.post(
        "/api/v1/projects",
        json={"name": "Harness Demo", "preset_id": "fastapi-react"},
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    updated = client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={
            "answers": {
                "project_kind": "Web",
                "languages": ["Python", "TypeScript"],
                "frameworks": ["FastAPI", "React"],
                "ai_tools": ["Claude", "Codex", "Cursor"],
                "test_strategy": ["pytest", "jest"],
                "lint_format": ["ruff", "eslint", "prettier"],
                "prohibited_actions": "本番DBの直接変更禁止",
                "review_policy": "厳格",
                "branch_strategy": "main + feature branches",
                "future_custom_key": "既存クライアントの拡張値",
            }
        },
    )

    assert updated.status_code == 200
    assert updated.json()["answers"]["frameworks"] == ["FastAPI", "React"]
    assert updated.json()["answers"]["future_custom_key"] == "既存クライアントの拡張値"

    loaded = client.get(f"/api/v1/projects/{project_id}")
    assert loaded.status_code == 200
    assert loaded.json()["name"] == "Harness Demo"
    assert loaded.json()["answers"]["future_custom_key"] == "既存クライアントの拡張値"


def _create_project(client) -> str:
    _register(client)
    created = client.post(
        "/api/v1/projects",
        json={"name": "Validation Demo", "preset_id": None},
    )
    assert created.status_code == 201
    return created.json()["id"]


def test_update_answers_rejects_invalid_choice(client):
    project_id = _create_project(client)

    response = client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={"answers": {"ai_tools": ["claude"]}},
    )

    assert response.status_code == 400
    assert "ai_tools has invalid choices: claude" in response.json()["detail"]

    loaded = client.get(f"/api/v1/projects/{project_id}")
    assert "ai_tools" not in {
        key for key, value in loaded.json()["answers"].items() if value
    }


def test_update_answers_accepts_normalizable_payload_shapes(client):
    project_id = _create_project(client)

    response = client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={
            "answers": {
                "project_kind": ["Web"],
                "languages": "Python",
                "frameworks": "FastAPI",
                "ai_tools": "Codex",
                "test_strategy": "pytest",
                "lint_format": "ruff",
                "prohibited_actions": ["本番DBの直接変更禁止"],
                "review_policy": ["厳格"],
            }
        },
    )

    assert response.status_code == 200
    answers = response.json()["answers"]
    assert answers["project_kind"] == "Web"
    assert answers["languages"] == ["Python"]
    assert answers["frameworks"] == ["FastAPI"]
    assert answers["ai_tools"] == ["Codex"]
    assert answers["test_strategy"] == ["pytest"]
    assert answers["lint_format"] == ["ruff"]
    assert answers["prohibited_actions"] == "本番DBの直接変更禁止"
    assert answers["review_policy"] == "厳格"

    generated = client.post(f"/api/v1/projects/{project_id}/generate")
    assert generated.status_code == 200
    generated_paths = {item["file_path"] for item in generated.json()["items"]}
    assert generated_paths == CHANGE_PACKAGE_PATHS

    exported = client.get(f"/api/v1/projects/{project_id}/export")
    assert exported.status_code == 200
    with ZipFile(io.BytesIO(exported.content)) as archive:
        assert set(archive.namelist()) == CHANGE_PACKAGE_PATHS


def test_update_answers_accepts_valid_answers(client):
    project_id = _create_project(client)

    response = client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={"answers": {"ai_tools": ["Claude", "Codex"], "project_kind": "Web"}},
    )

    assert response.status_code == 200
    assert response.json()["answers"]["ai_tools"] == ["Claude", "Codex"]


def test_update_answers_preserves_unknown_keys(client):
    project_id = _create_project(client)

    response = client.put(
        f"/api/v1/projects/{project_id}/answers",
        json={"answers": {"future_custom_key": "拡張値"}},
    )

    assert response.status_code == 200
    assert response.json()["answers"]["future_custom_key"] == "拡張値"
