from fastapi import FastAPI,Depends,status,HTTPException,File,UploadFile
from pymysql import cursors
from pymysql.err import MySQLError
from typing import List,Optional
import os
import io
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import create_engine,Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy.types import BLOB
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

app=FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("system_activity.log"),
        logging.StreamHandler()
    ]
)
logger=logging.getLogger(__name__)

MYSQL_USER=os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST=os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT=os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE=os.getenv("MYSQL_DATABASE", "patient_db")

DATABASE_CONFIG={
    "host": MYSQL_HOST,
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "db": MYSQL_DATABASE,
    "charset": "utf8mb4",
    "cursorclass": cursors.DictCursor
}

DATABASE_URL=f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()

class Patient(Base):
    __tablename__="patients"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(255),nullable=False)
    age=Column(Integer,nullable=False)
    gender=Column(String(20),nullable=False)
    address=Column(String(500),nullable=False)
    phone=Column(String(20),nullable=False)
    created_at=Column(DateTime,default=datetime.now)
    updated_at=Column(DateTime,default=datetime.now,onupdate=datetime.now)
    health_records=relationship("PatientHealth",back_populates="patient")
    records=relationship("PatientRecords",back_populates="patient")

class PatientHealth(Base):
    __tablename__="PatientHealth"
    id=Column(Integer,primary_key=True,index=True)
    patient_id=Column(Integer,ForeignKey("patients.id"),nullable=False)
    height=Column(Integer,nullable=False)
    weight=Column(Integer,nullable=False)
    blood_pressure=Column(Integer,nullable=False)
    created_at=Column(DateTime,default=datetime.now)
    updated_at=Column(DateTime,default=datetime.now,onupdate=datetime.now)
    patient=relationship("Patient",back_populates="health_records")

class PatientRecords(Base):
    __tablename__="PatientRecords"
    id=Column(Integer,primary_key=True,index=True)
    patient_id=Column(Integer,ForeignKey("patients.id"),nullable=False)
    record_type=Column(String(100),nullable=False)
    record_data=Column(String(5000),nullable=False)
    file_name=Column(String(255))
    file_data=Column(BLOB)
    created_at=Column(DateTime,default=datetime.now)
    updated_at=Column(DateTime,default=datetime.now,onupdate=datetime.now)
    patient=relationship("Patient",back_populates="records")

Base.metadata.create_all(bind=engine)

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    address: str
    phone: str

class PatientUpdate(BaseModel):
    name: Optional[str]=None
    age: Optional[int]=None
    gender: Optional[str]=None
    address: Optional[str]=None
    phone: Optional[str]=None

class PatientHealthCreate(BaseModel):
    height: int
    weight: int
    blood_pressure: int

class PatientHealthUpdate(BaseModel):
    height: Optional[int]=None
    weight: Optional[int]=None
    blood_pressure: Optional[int]=None

class PatientRecordsCreate(BaseModel):
    record_type: str
    record_data: str

class PatientRecordsUpdate(BaseModel):
    record_type: Optional[str]=None
    record_data: Optional[str]=None
    file_name: Optional[str]=None
    file_data: Optional[bytes]=None

class PatientRecordsResponse(BaseModel):
    id: int
    patient_id: int
    record_type: str
    record_data: str
    file_name: Optional[str]=None
    created_at: Optional[datetime]=None
    updated_at: Optional[datetime]=None

    class Config:
        from_attributes=True

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/patients/", status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, db: Session=Depends(get_db)):
    try:
        db_patient=Patient(name=patient.name, age=patient.age, gender=patient.gender, address=patient.address, phone=patient.phone)
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        logger.info(f"Patient added: ID={db_patient.id}, Name={db_patient.name}")
        return db_patient
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@app.post("/patients/{patient_id}/health", status_code=status.HTTP_201_CREATED)
def create_PatientHealth(patient_id: int, health: PatientHealthCreate, db: Session=Depends(get_db)):
    try:
        patient=db.query(Patient).filter(Patient.id==patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")
        db_health=PatientHealth(patient_id=patient_id, height=health.height, weight=health.weight, blood_pressure=health.blood_pressure)
        db.add(db_health)
        db.commit()
        db.refresh(db_health)
        logger.info(f"Health record created for Patient ID={patient_id}")
        return db_health
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating health record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/patients/{patient_id}/records",status_code=status.HTTP_201_CREATED)
async def create_patient_record(patient_id: int, records: PatientRecordsCreate, db: Session=Depends(get_db)):
    try:
        patient=db.query(Patient).filter(Patient.id==patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient with ID {patient_id} not found")
        file_name=f"{records.record_type}.log"
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        audit_content=f"[{timestamp}] Patient ID: {patient_id}\n{records.record_data}"
        file_data_bytes=audit_content.encode('utf-8')
        db_records=PatientRecords(patient_id=patient_id, record_type=records.record_type, record_data=records.record_data, file_name=file_name, file_data=file_data_bytes)
        db.add(db_records)
        db.commit()
        db.refresh(db_records)
        logger.info(f"Record created: Type={records.record_type}, Patient ID={patient_id}, File={file_name}")
        return db_records
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating patient record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/patients/{patient_id}/records", response_model=List[PatientRecordsResponse])
def get_patient_records(patient_id: int, db: Session=Depends(get_db)):
    try:
        records=db.query(PatientRecords).filter(PatientRecords.patient_id==patient_id).all()
        if not records:
            raise HTTPException(status_code=404, detail=f"No records found for Patient ID {patient_id}")
        logger.info(f"Retrieved records for Patient ID={patient_id}")
        return records
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving records: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
