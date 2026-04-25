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
