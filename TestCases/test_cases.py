import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_files_list_unauthenticated():
    response = client.get("/list_files")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_files_list_authenticated():
    response = client.get("/list_files", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Inlhc2hiaXNodDIwMDRAZ21haWwuY29tIiwicm9sZSI6ImNsaWVudCIsImlzX3ZlcmlmaWVkIjp0cnVlLCJjcmVhdGVkX2F0IjoiMjAyNS0wNy0wMiAxNDo1NDowNy44NjgxMzIiLCJleHAiOjE3NTUwNzA0MTB9.ktcXnOPbQ9PqXgny0U7Qi-I1ZeWfHD-Y4K9beXDphJo"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_upload_docx_should_fail():
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3QxMjM0QGdtYWlsLmNvbSIsInJvbGUiOiJvcHMiLCJpc192ZXJpZmllZCI6dHJ1ZSwiY3JlYXRlZF9hdCI6IjIwMjUtMDctMDIgMTY6NTA6MDMuMjE5MDI2IiwiZXhwIjoxNzU1MDg2MDcyfQ.ZgX-tShyoRpgCmp6wPyKNHjI2bXe9G0m1CJAxJtSjbY"
    }
    fake_file = io.BytesIO(b"dummy content")
    files = {
        "file": ("test_file.pdf", fake_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    response = client.post("/upload", headers=headers, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file type. Only .pptx, .docx, and .xlsx are allowed."

def test_upload_docx_should_pass():
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3QxMjM0QGdtYWlsLmNvbSIsInJvbGUiOiJvcHMiLCJpc192ZXJpZmllZCI6dHJ1ZSwiY3JlYXRlZF9hdCI6IjIwMjUtMDctMDIgMTY6NTA6MDMuMjE5MDI2IiwiZXhwIjoxNzU1MDg2MDcyfQ.ZgX-tShyoRpgCmp6wPyKNHjI2bXe9G0m1CJAxJtSjbY"
    }
    fake_file = io.BytesIO(b"dummy content")
    files = {
        "file": ("test_file.docx", fake_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    response = client.post("/upload", headers=headers, files=files)
    assert response.status_code == 200
    assert response.json() == {
        "message": "File 'test_file.docx' uploaded successfully."
    }


