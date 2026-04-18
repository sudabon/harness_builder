def test_register_login_and_restore_session(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "supersecret"},
    )
    assert response.status_code == 201
    assert response.json()["user"]["email"] == "owner@example.com"

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "owner@example.com"

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "supersecret"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["email"] == "owner@example.com"
