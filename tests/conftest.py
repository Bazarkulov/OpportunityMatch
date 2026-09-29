import os
os.environ["DATABASE_URL"] = "sqlite:///./test_opportunitymatch.db"
os.environ["AUTH_SECRET"] = "test-secret"
import pytest
from fastapi.testclient import TestClient
from backend.database import Base, engine
from backend.main import app
@pytest.fixture(autouse=True)
def clean_database(): Base.metadata.drop_all(engine); Base.metadata.create_all(engine); yield
@pytest.fixture
def client():
    with TestClient(app) as value: yield value
