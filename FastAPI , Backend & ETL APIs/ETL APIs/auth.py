from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

router=APIRouter()
security=HTTPBearer()

JWT_SECRET=os.getenv("JWT_SECRET")
JWT_ALGORITHM=os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES=int(os.getenv("JWT_EXPIRE_MINUTES"))
API_USERNAME=os.getenv("API_USERNAME")
API_PASSWORD=os.getenv("API_PASSWORD")

class LoginRequest(BaseModel):
    username: str
    password: str

def create_access_token(data: dict) -> str:
    payload=data.copy()
    payload["exp"]=datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials=Depends(security)) -> dict:
    return verify_token(credentials.credentials)

@router.post("/auth/token")
def login(body: LoginRequest):
    if body.username != API_USERNAME or body.password != API_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token=create_access_token({"sub": body.username})
    return {"access_token": token, "token_type": "bearer"}
