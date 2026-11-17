import pytest
from app.config import settings
from app import schemas
from jose import jwt

def test_create_user(client):
    response = client.post("/user", json={"email": "user@example.com", "password": "string"})
    new_user = schemas.UserResponse(**response.json())
    assert response.status_code == 201
    assert new_user.email == "user@example.com"

def test_login_user(client, test_user):
    response=client.post("/login", data={"username": test_user["email"], "password": test_user["password"]})
    login_response=schemas.Token(**response.json())
    payload = jwt.decode(login_response.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("user_id") == test_user["id"]
    assert response.status_code==200
    assert login_response.access_token is not None
    assert login_response.token_type == "bearer"
    assert login_response.refresh_token is not None

@pytest.mark.parametrize("email, password, status_code", [
    ("user@example.com", "wrongpassword", 403),
    ("nonexistent@example.com", "string", 403),
    ("", "string", 422),
    ("user@example.com", "", 422) 
])
def test_incorrect_login(client, test_user,email,password,status_code):
    response=client.post("/login", data={"username": email, "password":password})
    assert response.status_code==status_code

def test_login_ip_rate_limit(client):
    for i in range(6):
        response = client.post(
            "/login",
            data={"username": f"fake{i}@test.com", "password": "wrongpassword"}
        )
        if i < 5:
            assert response.status_code == 403
             
    assert response.status_code == 429
    assert "Too many login attempts from this IP" in response.json()["detail"]


def test_login_email_fail_limit(client): 
    fake_email = "victim@test.com"
     
    for i in range(4):
        response = client.post(
            "/login",
            data={"username": fake_email, "password": "wrongpassword"}
        )
        assert response.status_code == 403 
    # On the 5th attempt, the email Vault Guard locks it!
    response = client.post(
        "/login",
        data={"username": fake_email, "password": "wrongpassword"}
    )
    assert response.status_code == 429
    assert "Too many failed attempts for this account" in response.json()["detail"]
