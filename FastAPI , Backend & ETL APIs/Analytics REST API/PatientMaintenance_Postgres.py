from fastapi import FastAPI,Depends,status,HTTPException,File,UploadFile,APIRouter,Request
from typing import List,Optional,Annotated
import os
import io
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime,date
from sqlalchemy import create_engine,Column, Integer, String, DateTime, ForeignKey,Date,Float,func,desc,case,extract
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import UUID
import logging
from dotenv import load_dotenv
from urllib.parse import quote_plus
import pandas as pd
import auth
import uuid
from auth import get_current_user,get_admin,get_doctor,User
import limit_log
from CustomErrors import PatientManagementError,DatabaseOperationError,ValidationError as PatientValidationError
from contextlib import asynccontextmanager
from models import FileMetaData, Base as ETLBase
import file_detector

load_dotenv()

UPLOAD_DIR=os.getenv("UPLOAD_DIR","./Data")
os.makedirs(UPLOAD_DIR,exist_ok=True)

@asynccontextmanager
async def lifespan(app:FastAPI):
    file_changes=asyncio.create_task(file_detector.detect_changes(SessionLocal,UPLOAD_DIR))
    logger.info("Starting background tasks")
    yield
    logger.info("Stopping background tasks")
    file_changes.cancel()
    try:
        await file_changes
    except asyncio.CancelledError:
        logger.info("Background tasks cancelled")

app=FastAPI(title="Patient Maintenance API(PostgreSQL)",version="1.0.0",lifespan=lifespan)
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

POSTGRES_USER=os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST=os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT=os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DATABASE=os.getenv("POSTGRES_DATABASE", "gh_db1")

DATABASE_URL=f"postgresql+psycopg2://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()

class Patient(Base):
    __tablename__="patients"
    id=Column(UUID(as_uuid=True),primary_key=True,index=True)
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
    procedure_id=Column(UUID(as_uuid=True),primary_key=True)
    patient_id=Column(UUID(as_uuid=True),ForeignKey("patients.id"),nullable=False)
    start_date=Column(Date,nullable=False)
    end_date=Column(Date,nullable=False)
    description=Column(String(1000),nullable=False)
    procedure_base_cost=Column(Float,nullable=False)
    patient=relationship("Patient",back_populates="Procedures")

class Encounters(Base):
    __tablename__="encounters"
    encounter_id=Column(UUID(as_uuid=True),primary_key=True)
    patient_id=Column(UUID(as_uuid=True),ForeignKey("patients.id"),nullable=False)
    start_date=Column(Date,nullable=False)
    end_date=Column(Date,nullable=False)
    payer_id=Column(UUID(as_uuid=True),ForeignKey("payers.payer_id"),nullable=False)
    encounter_type=Column(String(100),nullable=False)
    encounter_description=Column(String(1000),nullable=False)
    base_cost=Column(Float,nullable=False)
    total_claim_amount=Column(Float,nullable=False)
    patient=relationship("Patient",back_populates="Encounters")
    payer=relationship("Payers",back_populates="Encounters")

class Payers(Base):
    __tablename__="payers"
    payer_id=Column(UUID(as_uuid=True),primary_key=True,index=True)
    payer_name=Column(String(255),nullable=False)
    city=Column(String(255),nullable=True)
    phone=Column(String(20),nullable=True) 
    Encounters=relationship("Encounters",back_populates="payer")  

Base.metadata.create_all(bind=engine)
ETLBase.metadata.create_all(bind=engine)

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    birth_date: date
    death_date: Optional[date]=None
    Marital: Optional[str]=None
    gender: str
    city: str

class PatientUpdate(BaseModel):
    first_name: Optional[str]=None
    last_name: Optional[str]=None
    birth_date: Optional[date]=None
    death_date: Optional[date]=None
    Marital: Optional[str]=None
    gender: Optional[str]=None
    city: Optional[str]=None

class FileMetaDataResponse(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: Optional[UUID(as_uuid=True)]=None
    file_name: Optional[str]=None
    file_path: Optional[str]=None
    file_hash: Optional[str]=None
    file_size: Optional[int]=None
    last_modified: Optional[datetime]=None
    last_processed: Optional[datetime]=None
    status: Optional[str]=None
    updated_at: Optional[datetime]=None

class AverageCostResponse(BaseModel):
    average_cost: Optional[float]=None

class ProcedureCoverageResponse(BaseModel):
    total_procedures: Optional[int]=None
    covered_procedures: Optional[int]=None

class RevenueReportResponse(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: Optional[UUID(as_uuid=True)]=None
    description: Optional[str]=None
    total_revenue: Optional[float]=None

class PayerCoverage(BaseModel):
    payer_name: str
    encounter_count: int
    total_covered_amount: float

class PatientResponse(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: Optional[UUID(as_uuid=True)]=None
    first_name: Optional[str]=None
    last_name: Optional[str]=None
    gender: Optional[str]=None
    city: Optional[str]=None
    Marital: Optional[str]=None
    birth_date: Optional[date]=None
    death_date: Optional[date]=None

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload",status_code=status.HTTP_201_CREATED)
async def file_upload(files:Annotated[List[UploadFile],File(...)],db:Session=Depends(get_db),current_user:User=Depends(get_admin)):
    try:
        import data_processor
        import hashlib
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
        file_metadata_list=[]
        
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
                    existing_ids = {str(pid[0]) for pid in db.query(Patient.id).all()}
                    for _,row in result.iterrows():
                        patient=Patient(id=row['id'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            birth_date=row['birth_date'],
                            death_date=row['death_date'],
                            Marital=row['Marital'],
                            gender=row['gender'],
                            city=row['city'])
                        exists=db.query(Patient.id).filter(Patient.id==row['id']).first() is not None
                        if not exists:
                            db.add(patient)
                            existing_ids.add(row['id'])
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
                    valid_payer_ids = {str(p[0]) for p in db.query(Payers.payer_id).all()}
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
                    existing_payer_ids = {str(pid[0]) for pid in db.query(Payers.payer_id).all()}
                    for _,row in result.iterrows():
                        payer=Payers(
                            payer_id=row['payer_id'],
                            payer_name=row['payer_name'],
                            city=row['city'],
                            phone=row['phone'])
                        exists=db.query(Payers.payer_id).filter(Payers.payer_id==row['payer_id']).first() is not None
                        if not exists:
                            db.add(payer)
                            existing_payer_ids.add(row['payer_id'])
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

@router.get("/analytics/average-cost", response_model=AverageCostResponse)
def get_average_cost(db: Session = Depends(get_db),current_user:User=Depends(get_admin)):
    result = db.query(func.avg(Encounters.total_claim_amount)).scalar()
    return {"average_cost": round(result or 0, 2)}

@router.get("/analytics/procedure-coverage", response_model=ProcedureCoverageResponse)
def get_procedure_coverage(db: Session = Depends(get_db),current_user:User=Depends(get_admin)):
    total = db.query(func.count(Procedures.procedure_id)).scalar()
    covered = db.query(func.count(Procedures.procedure_id)).join(Patient, Procedures.patient_id == Patient.id).join(Encounters, Patient.id == Encounters.patient_id).filter(Encounters.payer_id.isnot(None)).distinct().scalar()
    return {"total_procedures": total, "covered_procedures": covered}

@router.get("/analytics/high-revenue/encounters", response_model=List[RevenueReportResponse])
def get_high_revenue_encounters(db: Session = Depends(get_db),current_user:User=Depends(get_admin)):
    results = db.query(Encounters.encounter_id.label('id'),Encounters.encounter_description.label('description'),Encounters.total_claim_amount.label('total_revenue')).order_by(desc(Encounters.total_claim_amount)).limit(10).all()
    return results

@router.get("/analytics/high-revenue/procedures", response_model=List[RevenueReportResponse])
def get_high_revenue_procedures(db: Session = Depends(get_db),current_user:User=Depends(get_admin)):
    results = db.query(Procedures.procedure_id.label('id'),Procedures.description.label('description'),Procedures.procedure_base_cost.label('total_revenue')).order_by(desc(Procedures.procedure_base_cost)).limit(10).all()
    return results

@router.get("/analytics/payer-comparison", response_model=List[PayerCoverage])
def get_payer_comparison(db: Session = Depends(get_db),current_user:User=Depends(get_admin)):
    results = db.query(Payers.payer_name,func.count(Encounters.encounter_id).label('encounter_count'),func.sum(Encounters.total_claim_amount).label('total_covered_amount')).join(Encounters, Payers.payer_id == Encounters.payer_id).group_by(Payers.payer_name).order_by(desc('total_covered_amount')).all()
    return results

@router.get("/patients/list",response_model=List[PatientResponse])
def get_patients(db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    return db.query(Patient).all()
    
@router.get("/patients/list/{id}",response_model=PatientResponse)
def get_patients_by_id(id:str,db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    return db.query(Patient).filter(Patient.id==id).first()

app.include_router(router)
app.include_router(auth.router,prefix="/api/v1")
