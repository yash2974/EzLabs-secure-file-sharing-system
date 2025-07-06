# 📁 Secure File Sharing System

This is a backend API for securely uploading, listing, and downloading files with user authentication and role-based access.
Used Celery for non blocking Email verification.
Create a .env file for Postgresql db and email/google-app-password

## 🚀 Base URL
```
http://127.0.0.1:8000/

```
## 🚀 How to run
 
```
fastapi dev main.py     
celery -A utils.celery_worker.celery_app worker --loglevel=info --pool=solo
```

## 📤 Database Schema

```
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  role VARCHAR(10) NOT NULL CHECK (role IN ('ops', 'client')),
  is_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```


## 🔐 Authentication

- **Type:** Bearer Token (JWT)
- **How to get it:** Use the `/login` endpoint to retrieve `access_token`
- **Where to use it:** Pass it in the `Authorization` header as `Bearer <access_token>`

---

## 📝 1. Sign Up

**Endpoint:** `POST /signup`  
**Auth Required:** ❌ No  
**Request Body (JSON):**
```json
{
  "email": "example@mail.com",
  "password": "yourpassword",
  "role": "ops" // or "client"
}
```

**Response:**
- Success or error message

---

## 🔑 2. Log In

**Endpoint:** `POST /login`  
**Auth Required:** ❌ No  
**Request Body (JSON):**
```json
{
  "email": "example@mail.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access_token": "your-jwt-token"
}
```

---

## 📤 3. Upload File

**Endpoint:** `POST /upload`  
**Auth Required:** ✅ Yes  
**Form-Data:**
- `file`: Upload `.pptx`, `.docx`, or `.xlsx` file only

**Response:**
- Success or error message

---

## 📃 4. List Files

**Endpoint:** `GET /list_files`  
**Auth Required:** ✅ Yes  

**Response:**
```json
[
  "file1.xlsx",
  "file2.docx"
]
```

---

## 🔗 5. Get Secure Download Link

**Endpoint:** `GET /download/{filename}`  
**Auth Required:** ✅ Yes  
**Example:**
```
GET /download/data-1749407797375.xlsx
```

**Response:**
```json
{
  "download-link": "http://127.0.0.1:8000/download_secure/<token>"
}
```

---

## ⬇️ 6. Download File via Secure Link

**Endpoint:** `GET /download_secure/{token}`  
**Auth Required:** ✅ Yes  

**Description:** Accesses and downloads the file using the encrypted token link.

---

## 🌐 Postman Collection Variables

- `{{access_token}}`: Set after login
- `{{secure_encrypted_token}}`: Set after requesting download link

---

## 📌 Notes

- Only users with role `"ops"` can upload files.
- All download links are time-limited and encrypted for added security.
