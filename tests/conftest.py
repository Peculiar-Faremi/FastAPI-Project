from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import pytest
from app.config import settings
from app import oauth2
from app.database import get_db, Base
from app.redis_client import r

#i created a branch from neon for the test database and got a new url for it so it won't touch my development database.
SQLALCHEMY_DATABASE_URL = settings.TEST_DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

@pytest.fixture(autouse=True)  # autouse means it runs before EVERY test automatically
def clear_redis():
    r.flushdb()  # empty Redis so one test's cache can't affect the next
    yield           

@pytest.fixture
def product_id(authorized_client):
    response = authorized_client.post("/products/post", json={"name": "Test Product", "details": {"description": "A product for testing"}, "price": 999})  # your real product payload
    return response.json()["id"]

@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)  # Drop all tables in the test database before each test
    Base.metadata.create_all(bind=engine)  # Create all tables in the test database before each test
    db= TestingSessionLocal() #this creates a new session for the test database, allowing me to interact with the database during testing
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db #this will override the get_db dependency in the app with the test database session
    yield TestClient(app) #runs the test client for the FastAPI app, allowing you to make requests to the API endpoints during testing
    app.dependency_overrides.clear()  # Clear the dependency overrides after the test is done

@pytest.fixture()
def test_user(client): 
    user_data={"email": "user@example.com", "password": "string"}
    response = client.post("/user", json=user_data)
    assert response.status_code == 201
    new_user=response.json()
    new_user["password"]=user_data["password"]
    return new_user

@pytest.fixture()
def token(test_user):
    return oauth2.create_access_token(data={"user_id": test_user["id"]})

@pytest.fixture()
def authorized_client(client, token):
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client