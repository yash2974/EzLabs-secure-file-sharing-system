from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_files_list_unauthenticated():
    response = client.get("/list_files")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


