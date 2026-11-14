from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import pytest
from app import oauth2
from app.database import get_db, Base
#i created a branch from neon for the test database and got a new url for it so it won't touch my development database.
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_f4bW1XvxjGKn@ep-delicate-pond-bd4muuoj-pooler.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

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