from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(filename="system_activity.log",level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger=logging.getLogger(__name__)


load_dotenv()

router=APIRouter()
security=HTTPBearer()

JWT_SECRET=os.getenv("JWT_SECRET")
JWT_ALGORITHM=os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES=int(os.getenv("JWT_EXPIRE_MINUTES"))
API_ADMIN_USERNAME=os.getenv("API_ADMIN_USERNAME")
API_ADMIN_PASSWORD=os.getenv("API_ADMIN_PASSWORD")
DOCTOR_USERNAME=os.getenv("DOCTOR_USERNAME")
DOCTOR_PASSWORD=os.getenv("DOCTOR_PASSWORD")

class LoginRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    password: str
    role: str

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

def get_admin(current_user: dict=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user

def get_doctor(current_user: dict=Depends(get_current_user)):
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin and Doctor only")
    return current_user

@router.post("/auth/token")
def login(body: LoginRequest):
    if (body.username != API_ADMIN_USERNAME and body.password != API_ADMIN_PASSWORD) and (body.username != DOCTOR_USERNAME and body.password != DOCTOR_PASSWORD):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if body.username == API_ADMIN_USERNAME and body.password == API_ADMIN_PASSWORD:
        token=create_access_token({"sub": body.username, "role": "admin"})
        logger.info(f"Admin logged in: {body.username}")
        return {"access_token": token, "token_type": "bearer", "role": "admin"}
    if body.username == DOCTOR_USERNAME and body.password == DOCTOR_PASSWORD:
        token=create_access_token({"sub": body.username, "role": "doctor"})
        logger.info(f"Doctor logged in: {body.username}")
        return {"access_token": token, "token_type": "bearer", "role": "doctor"}
