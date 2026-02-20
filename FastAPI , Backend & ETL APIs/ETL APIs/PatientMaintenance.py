from fastapi import FastAPI,Depends,status,HTTPException,File,UploadFile,APIRouter,Request
from pymysql import cursors
from pymysql.err import MySQLError
from typing import List,Optional,Annotated
import os
import io
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from datetime import datetime,date
from sqlalchemy import create_engine,Column, Integer, String, DateTime, ForeignKey,Date,Float,func,desc
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError
import logging
from dotenv import load_dotenv
from urllib.parse import quote_plus
import pandas as pd
import auth
import limit_log
from CustomErrors import PatientManagementError,DatabaseOperationError,ValidationError as PatientValidationError

load_dotenv()
app=FastAPI(title="Patient Maintenance API",version="1.0.0")
app.add_middleware(limit_log.RequestLoggingMiddleware)
app.add_middleware(limit_log.RateLimitMiddleware)
router=APIRouter(prefix="/api/v1")

@app.exception_handler(PatientManagementError)
async def patient_management_error_handler(request:Request,exc:PatientManagementError):
    from fastapi.responses import JSONResponse
    logger.error(f"PatientManagementError [{exc.error_code}]: {exc.message}")
    return JSONResponse(status_code=400,content={"error_code":exc.error_code,"detail":exc.message})

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s",handlers=[logging.FileHandler("system_activity.log"),logging.StreamHandler()])
logger=logging.getLogger(__name__)

MYSQL_USER=os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST=os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT=os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE=os.getenv("MYSQL_DATABASE", "gh_db")

DATABASE_CONFIG={"host": MYSQL_HOST,"user": MYSQL_USER,"password": MYSQL_PASSWORD,"db": MYSQL_DATABASE,"cursorclass": cursors.DictCursor}

DATABASE_URL=f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()

class Patient(Base):
    __tablename__="patients"
    id=Column(String(100),primary_key=True,index=True)
    first_name=Column(String(255),nullable=False)
    last_name=Column(String(255),nullable=False)
    birth_date=Column(Date,nullable=False)
    death_date=Column(Date,nullable=True)
    Marital=Column(String(20),nullable=True)
    gender=Column(String(20),nullable=False)
    city=Column(String(255),nullable=False)
    Procedures=relationship("Procedures",back_populates="patient")
    Encounters=relationship("Encounters",back_populates="patient")

class Procedures(Base):
    __tablename__="procedures"
    procedure_id=Column(String(100),primary_key=True)
    patient_id=Column(String(100),ForeignKey("patients.id"),nullable=False)
    start_date=Column(Date,nullable=False)
    end_date=Column(Date,nullable=False)
    description=Column(String(1000),nullable=False)
    procedure_base_cost=Column(Float,nullable=False)
    patient=relationship("Patient",back_populates="Procedures")

class Encounters(Base):
    __tablename__="encounters"
    encounter_id=Column(String(100),primary_key=True)
    patient_id=Column(String(100),ForeignKey("patients.id"),nullable=False)
    start_date=Column(Date,nullable=False)
    end_date=Column(Date,nullable=False)
    payer_id=Column(String(100),ForeignKey("payers.payer_id"),nullable=False)
    encounter_type=Column(String(100),nullable=False)
    encounter_description=Column(String(1000),nullable=False)
    base_cost=Column(Float,nullable=False)
    total_claim_amount=Column(Float,nullable=False)
    patient=relationship("Patient",back_populates="Encounters")
    payer=relationship("Payers",back_populates="Encounters")

class Payers(Base):
    __tablename__="payers"
    payer_id=Column(String(100),primary_key=True,index=True)
    payer_name=Column(String(255),nullable=False)
    city=Column(String(255),nullable=True)
    phone=Column(String(20),nullable=True) 
    Encounters=relationship("Encounters",back_populates="payer")  

Base.metadata.create_all(bind=engine)

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    birth_date: date
    death_date: Optional[date]=None
    Marital: Optional[str]=None
    gender: str
    city: str
    phone: Optional[int]=None

class PatientUpdate(BaseModel):
    first_name: Optional[str]=None
    last_name: Optional[str]=None
    birth_date: Optional[date]=None
    death_date: Optional[date]=None
    Marital: Optional[str]=None
    gender: Optional[str]=None
    city: Optional[str]=None
    phone: Optional[int]=None

class PatientProceduresCreate(BaseModel):
    procedure_id: str
    start_date: date
    end_date: date
    description: str
    base_cost: float

class PatientProceduresUpdate(BaseModel):
    procedure_id: Optional[str]=None
    start_date: Optional[date]=None
    end_date: Optional[date]=None
    description: Optional[str]=None
    base_cost: Optional[float]=None

class PatientProceduresResponse(BaseModel):
    procedure_id: str
    start_date: date
    end_date: date
    description: str
    base_cost: float

class PatientEncountersCreate(BaseModel):
    encounter_id: str
    start_date: date
    end_date: date
    payer_id: str
    encounter_type: str
    encounter_description: str
    base_cost: float
    total_claim_amount: float

class PatientEncountersUpdate(BaseModel):
    encounter_id: Optional[str]=None
    start_date: Optional[date]=None
    end_date: Optional[date]=None
    payer_id: Optional[str]=None
    encounter_type: Optional[str]=None
    encounter_description: Optional[str]=None
    base_cost: Optional[float]=None
    total_claim_amount: Optional[float]=None

class PatientEncountersResponse(BaseModel):
    patient_id: str
    encounter_id: str
    start_date: date
    end_date: date
    payer_id: str
    encounter_type: str
    encounter_description: str
    base_cost: float
    total_claim_amount: float

    class Config:
        from_attributes=True

class PatientEncountersAnalysisResponse(BaseModel):
    encounter_type: Optional[str]=None
    count: Optional[int]=None
    total_claim_amount: Optional[float]=None

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload",status_code=status.HTTP_201_CREATED)
async def file_upload(files:Annotated[List[UploadFile],File(...)],db:Session=Depends(get_db)):
    try:
        import data_processor
        def get_priority(file):
            name=file.filename.lower()
            if 'patients' in name:
                return 1
            elif 'payers' in name:
                return 2
            elif 'procedures' in name:
                return 3
            elif 'encounters' in name:
                return 4
            else:
                return 5
        files.sort(key=get_priority)
        for file in files:
            name=file.filename.lower()
            file_bytes=await file.read()
            if name.endswith('.xlsx') or name.endswith('.xls'):
                content=pd.read_excel(io.BytesIO(file_bytes))
            else:
                content=pd.read_csv(io.BytesIO(file_bytes))
            if 'patients' in name:
                result=data_processor.process_patients(content)
                if 'id' in result.columns:
                    for _,row in result.iterrows():
                        patient=Patient(id=row['id'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            birth_date=row['birth_date'],
                            death_date=row['death_date'],
                            Marital=row['Marital'],
                            gender=row['gender'],
                            city=row['city'])
                        if patient.id not in db.query(Patient.id).all():
                            db.add(patient)
                        else:
                            db.merge(patient)
                db.commit()
            elif 'procedures' in name:
                result=data_processor.process_procedures(content)
                if 'procedure_id' in result.columns:
                    for _,row in result.iterrows():
                        existing=db.query(Procedures).filter(Procedures.procedure_id==row['procedure_id']).first()
                        if not existing:
                            procedure=Procedures(procedure_id=row['procedure_id'],
                                patient_id=row['patient_id'],
                                start_date=row['start_date'],
                                end_date=row['end_date'],
                                description=row['description'],
                                procedure_base_cost=row['procedure_base_cost'])
                            db.add(procedure)
                        else:
                            existing.start_date=row['start_date']
                            existing.end_date=row['end_date']
                            existing.description=row['description']
                            existing.procedure_base_cost=row['procedure_base_cost']
                db.commit()
            elif 'encounters' in name:
                result=data_processor.process_encounters(content)
                if 'encounter_id' in result.columns:
                    valid_payer_ids={p[0] for p in db.query(Payers.payer_id).all()}
                    valid_patient_ids={p[0] for p in db.query(Patient.id).all()}
                    for _,row in result.iterrows():
                        if row['payer_id'] not in valid_payer_ids:
                            continue
                        existing=db.query(Encounters).filter(Encounters.encounter_id==row['encounter_id']).first()
                        if not existing:
                            encounter=Encounters(
                                encounter_id=row['encounter_id'],
                                patient_id=row['patient_id'],
                                start_date=row['start_date'],
                                end_date=row['end_date'],
                                payer_id=row['payer_id'],
                                encounter_type=row['encounter_type'],
                                encounter_description=row['encounter_description'],
                                base_cost=row['base_cost'],
                                total_claim_amount=row['total_claim_amount'])
                            db.add(encounter)
                        else:
                            existing.start_date=row['start_date']
                            existing.end_date=row['end_date']
                            existing.payer_id=row['payer_id']
                            existing.encounter_type=row['encounter_type']
                            existing.encounter_description=row['encounter_description']
                            existing.base_cost=row['base_cost']
                            existing.total_claim_amount=row['total_claim_amount']
                db.commit()
            elif 'payers' in name:
                result=data_processor.process_payers(content)
                if 'payer_id' in result.columns:
                    for _,row in result.iterrows():
                        payer=Payers(
                            payer_id=row['payer_id'],
                            payer_name=row['payer_name'],
                            city=row['city'],
                            phone=row['phone'])
                        if payer.payer_id not in db.query(Payers.payer_id).all():
                            db.add(payer)
                        else:
                            db.merge(payer)
                db.commit()
        logger.info("File upload completed successfully")
        return {"message":"File processed successfully"}
    except SQLAlchemyError as e:
        logger.error(f"File upload DB error: {e}")
        db.rollback()
        raise DatabaseOperationError("insert",str(e))
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        db.rollback()
        raise PatientValidationError("file",str(e))

@router.get("/analysis/encounters",response_model=List[PatientEncountersAnalysisResponse])
def encounter_analysis(db:Session=Depends(get_db),current_user:dict=Depends(auth.get_current_user)):
    try:
        import data_processor
        encounter_data=db.query(Encounters.encounter_type,
                                func.count(Encounters.encounter_type).label('count'),
                                func.sum(Encounters.total_claim_amount).label('total_claim_amount')).group_by(Encounters.encounter_type).all()
        result=[PatientEncountersAnalysisResponse(encounter_type=row.encounter_type,count=row.count,total_claim_amount=row.total_claim_amount) for row in encounter_data]
        logger.info(f"Encounter analysis fetched by user={current_user.get('sub')} records={len(result)}")
        return result
    except SQLAlchemyError as e:
        logger.error(f"Encounter analysis DB error: {e}")
        raise DatabaseOperationError("query",str(e))
    except Exception as e:
        logger.error(f"Encounter analysis failed: {e}")
        raise PatientValidationError("encounter_query",str(e))

app.include_router(router)
app.include_router(auth.router,prefix="/api/v1")
