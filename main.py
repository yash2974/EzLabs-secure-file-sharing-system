import time
import os
import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from utils.jwt_utils import create_access_token, get_current_user
from database.model import Base, User
from database.schema import LoginResponse, UploadResponse, UserCreate, SignUpResponse, UserLogin
from utils.util import hash_password, generate_verification_token, decrypt_verification_token, verify_password, encrypted_token
from utils.email_utils import send_verification_email
from fastapi.responses import FileResponse
from celery import Celery


Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def secure_file_sharing_system():
    return {"message": "Secure File Sharing System!"}

@app.post("/signup", response_model=SignUpResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    db_user = User(
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role,
        is_verified=False
    )
    db.add(db_user)
    db.commit()

    token = generate_verification_token(user.email)
    verification_url = f"http://127.0.0.1:8000/verify-email/{token}"

    # TODO: Send email to user.email with verification_url
    send_verification_email.delay(user.email, verification_url)


    return {
        "message": "User created. Please verify your email.",
        "verification_url": verification_url  # For demo; in prod, only email it
    }

@app.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        email = decrypt_verification_token(token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()

    return {"message": "Email successfully verified"}

@app.post("/login", response_model= LoginResponse)
def Login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not db_user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Successful login
    db_user_data = {
        "email": db_user.email,
        "role": db_user.role,
        "is_verified": db_user.is_verified,
        "created_at": str(db_user.created_at)
    }
    # Return user data without password
    access_token = create_access_token(data=db_user_data)


    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
@app.post("/upload", response_model= UploadResponse)
def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    if current_user.role != "ops":
        raise HTTPException(status_code=403, detail="Permission denied")
    if not file.filename.endswith((".pptx", ".docx", ".xlsx")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .pptx, .docx, and .xlsx are allowed.")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return {"message": f"File '{file.filename}' uploaded successfully."}

@app.get("/list_files")
def list_uploaded_files(current_user: User = Depends(get_current_user)):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="only client can list files")
    try:
        files = os.listdir(UPLOAD_DIR)
        return files
    except FileNotFoundError:
        return {"files": [], "message": "No upload directory found"}
    
@app.get("/download/{filename}")
def download_file(filename: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="only client can download files")
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    token = {
        "filename": filename,
        "user_email": current_user.email,
        "role": current_user.role,
        "timestamp": int(time.time())

    }
    Token = encrypted_token(json.dumps(token))
    return {
        "message": f"success",
        "download-link": f"http://127.0.0.1:8000/download_secure/{Token}"
    }

@app.get("/download_secure/{token}")
def download_secure_file(token: str, current_user: User = Depends(get_current_user)):
    try:
        decrypted_token = decrypt_verification_token(token, ttl_seconds=600000)
        token_data = json.loads(decrypted_token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if token_data["user_email"] != current_user.email or token_data["role"] != current_user.role:
        raise HTTPException(status_code=403, detail="Permission denied")

    file_path = os.path.join(UPLOAD_DIR, token_data["filename"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="application/octet-stream", filename=token_data["filename"])
    