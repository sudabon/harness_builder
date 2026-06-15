def test_list_presets(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "supersecret"},
    )

    response = client.get("/api/v1/presets")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 5
    assert {item["id"] for item in body} == {
        "fastapi-react",
        "go/echo-react",
        "nextjs",
        "python-api",
        "go-grpc",
    }
