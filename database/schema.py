from pydantic import BaseModel, ConfigDict, EmailStr, constr
from uuid import UUID
from datetime import datetime
from typing import Literal

from pydantic.fields import Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Literal["ops", "client"]

class SignUpResponse(BaseModel):
    message: str
    verification_url: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_verified: bool
    created_at: datetime

class UserTokenData(BaseModel):
    email: EmailStr
    role: Literal["ops", "client"]
    is_verified: bool
    created_at: datetime
    
class UploadResponse(BaseModel):
    message: str

model_config = ConfigDict(from_attributes=True)

    



    
