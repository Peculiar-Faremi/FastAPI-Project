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
     


 
