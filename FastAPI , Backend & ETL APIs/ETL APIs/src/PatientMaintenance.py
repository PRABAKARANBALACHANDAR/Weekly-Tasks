from fastapi import FastAPI,Depends,status,File,UploadFile,APIRouter,Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List,Optional,Annotated
import os
import io
import shutil
from pydantic import BaseModel,ConfigDict
from sqlalchemy import create_engine,Column, String,func,desc,Integer,ForeignKey,Date,cast
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError
import logging
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy.dialects.postgresql import UUID,TIMESTAMP,REAL
import pandas as pd
from DB_Management import models
from src import auth
from src.auth import get_current_user,User,get_admin,get_doctor
from src import limit_log
from Exceptions.CustomErrors import PatientManagementError,DatabaseOperationError,ValidationError as PatientValidationError
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio
from DB_Management.models import PG_Patient,PG_Procedures,PG_Encounters,PG_Payers

env_path=os.path.join(os.path.dirname(__file__),'..','env_variables','.env')
load_dotenv(env_path)

log_path=os.path.join(os.path.dirname(__file__),'..','Logs','system_activity.log')
logging.basicConfig(filename=log_path,level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger=logging.getLogger(__name__)

POSTGRES_USER=os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST=os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT=os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DATABASE=os.getenv("POSTGRES_DATABASE", "gh_db_pg")

PG_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
PG_engine=create_engine(PG_URL)
PGSessionLocal=sessionmaker(bind=PG_engine)
from DB_Management.models import PGBase
PGBase.metadata.create_all(bind=PG_engine)

UPLOAD_DIR=os.getenv("DATA_DIR","Data")
PROCESSED_DIR=os.getenv("PROCESSED_DIR","processed")

def get_pg_db():
    pg_db=PGSessionLocal()
    try:
        yield pg_db
    finally:
        pg_db.close()

def get_priority(file:str)->int:
            name=file.lower()
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

def update_patient_data(pg_db,result):
    for _,row in result.iterrows():
        obj=PG_Patient(id=row['id'],
        first_name=row['first_name'],
        last_name=row['last_name'],
        birth_date=row['birth_date'],
        death_date=row['death_date'],
        Marital=row['Marital'],
        gender=row['gender'],
        city=row['city'],
        updated_at=datetime.now())
        pg_db.merge(obj)
    pg_db.commit()
    
def update_procedure_data(pg_db,result):
    for _,row in result.iterrows():
        obj=PG_Procedures(procedure_id=row['procedure_id'],
        patient_id=row['patient_id'],
        start_date=row['start_date'],
        end_date=row['end_date'],
        description=row['description'],
        procedure_base_cost=row['procedure_base_cost'],
        updated_at=datetime.now())
        pg_db.merge(obj)
    pg_db.commit()
    
def update_encounter_data(pg_db,result):
    for _,row in result.iterrows():
        obj=PG_Encounters(encounter_id=row['encounter_id'],
        patient_id=row['patient_id'],
        start_date=row['start_date'],
        end_date=row['end_date'],
        encounter_type=row['encounter_type'],
        payer_id=row['payer_id'],
        encounter_description=row['encounter_description'],
        base_cost=row['base_cost'],
        total_claim_amount=row['total_claim_amount'],
        updated_at=datetime.now())
        pg_db.merge(obj)
    pg_db.commit()
    
def update_payer_data(pg_db,result):
    for _,row in result.iterrows():
        obj=PG_Payers(payer_id=row['payer_id'],
        payer_name=row['payer_name'],
        city=row['city'],
        phone=row['phone'],
        updated_at=datetime.now())
        pg_db.merge(obj)
    pg_db.commit()

def run_batch():
    import data_processor
    os.makedirs(UPLOAD_DIR,exist_ok=True)
    os.makedirs(PROCESSED_DIR,exist_ok=True)
    files=[f for f in os.listdir(UPLOAD_DIR)
        if f.lower().endswith('.csv') or f.lower().endswith('.xlsx') or f.lower().endswith('.xls')]
    if not files:
        logger.info("Batch ETL: no files found in Data folder, skipping.")
        return
    files.sort(key=get_priority)
    pg_db=PGSessionLocal()
    try:
        for filename in files:
            file_path=os.path.join(UPLOAD_DIR,filename)
            name=filename.lower()
            logger.info(f"Batch ETL processing: {filename}")
            if name.endswith('.xlsx') or name.endswith('.xls'):
                content=pd.read_excel(file_path)
            else:
                content=pd.read_csv(file_path)
            if 'patients' in name:
                result=data_processor.process_patients(content)
                if 'id' in result.columns:
                    update_patient_data(pg_db,result)
            elif 'payers' in name:
                result=data_processor.process_payers(content)
                if 'payer_id' in result.columns:
                    update_payer_data(pg_db,result)
            elif 'procedures' in name:
                result=data_processor.process_procedures(content)
                if 'procedure_id' in result.columns:
                    update_procedure_data(pg_db,result)
            elif 'encounters' in name:
                result=data_processor.process_encounters(content)
                if 'encounter_id' in result.columns:
                    update_encounter_data(pg_db,result)
            date_stamp=datetime.now().strftime("%Y-%m-%d")
            base,ext=os.path.splitext(filename)
            dest=os.path.join(PROCESSED_DIR,f"{base}_{date_stamp}{ext}")
            shutil.move(file_path,dest)
            logger.info(f"Archived: {filename} -> {dest}")
    except Exception as e:
        pg_db.rollback()
        logger.error(f"Batch ETL error: {e}")
    finally:
        pg_db.close()
async def batch_scheduler():
    while True:
        logger.info("Batch ETL scheduler triggered")
        try:
            await asyncio.to_thread(run_batch)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        await asyncio.sleep(86400)

@asynccontextmanager
async def lifespan(app:FastAPI):
    task=asyncio.create_task(batch_scheduler())
    logger.info("Batch ETL scheduler started")
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Batch ETL scheduler stopped")

app=FastAPI(title="Patient Maintenance API",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(limit_log.RequestLoggingMiddleware)
app.add_middleware(limit_log.RateLimitMiddleware)
router=APIRouter(prefix="/api/v1")


@app.exception_handler(PatientManagementError)
async def patient_management_error_handler(request:Request,exc:PatientManagementError):
    from fastapi.responses import JSONResponse
    logger.error(f"PatientManagementError [{exc.error_code}]: {exc.message}")
    return JSONResponse(status_code=400,content={"error_code":exc.error_code,"detail":exc.message})

@router.post("/upload",status_code=status.HTTP_201_CREATED)
async def file_upload(files:Annotated[List[UploadFile],File(...)],pg_db:Session=Depends(get_pg_db),current_user:User=Depends(get_admin)):
    import data_processor
    os.makedirs(UPLOAD_DIR,exist_ok=True)
    try:
        files.sort(key=lambda f:get_priority(f.filename))
        file_data=[]
        for file in files:
            file_bytes=await file.read()
            file_data.append((file.filename,file_bytes))
        def process_all():
            pg_db=PGSessionLocal()
            try:
                saved=[]
                for filename,file_bytes in file_data:
                    name=filename.lower()
                    save_path=os.path.join(UPLOAD_DIR,filename)
                    with open(save_path,"wb") as f:
                        f.write(file_bytes)
                    logger.info(f"Saved uploaded file: {save_path}")
                    saved.append(save_path)
                    if name.endswith('.xlsx') or name.endswith('.xls'):
                        content=pd.read_excel(io.BytesIO(file_bytes))
                    else:
                        content=pd.read_csv(io.BytesIO(file_bytes))
                    if 'patients' in name:
                        result=data_processor.process_patients(content)
                        if 'id' in result.columns:
                            update_patient_data(pg_db,result)
                    elif 'payers' in name:
                        result=data_processor.process_payers(content)
                        if 'payer_id' in result.columns:
                            update_payer_data(pg_db,result)
                    elif 'procedures' in name:
                        result=data_processor.process_procedures(content)
                        if 'procedure_id' in result.columns:
                            update_procedure_data(pg_db,result)
                    elif 'encounters' in name:
                        result=data_processor.process_encounters(content)
                        if 'encounter_id' in result.columns:
                            update_encounter_data(pg_db,result)
                return saved
            except Exception:
                pg_db.rollback()
                raise
            finally:
                pg_db.close()
        saved_files=await asyncio.to_thread(process_all)
        logger.info("File upload and ETL completed successfully")
        return {"message":"Files processed successfully","saved_paths":saved_files}
    except SQLAlchemyError as e:
        logger.error(f"Upload DB error: {e}")
        raise DatabaseOperationError("insert",str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise PatientValidationError("file",str(e))

@router.get("/patients/list",response_model=List[models.PatientResponse])
def get_patients(db: Session=Depends(get_pg_db),current_user:User=Depends(get_current_user)):
    return db.query(cast(PG_Patient.id,String).label("id"),PG_Patient.first_name,PG_Patient.last_name,PG_Patient.gender,PG_Patient.city,PG_Patient.created_at,PG_Patient.updated_at).all()
    
@router.get("/patients/list/{id}",response_model=models.PatientResponse)
def get_patients_by_id(id:str,db: Session=Depends(get_pg_db),current_user:User=Depends(get_current_user)):
    return db.query(cast(PG_Patient.id,String).label("id"),PG_Patient.first_name,PG_Patient.last_name,PG_Patient.gender,PG_Patient.city,PG_Patient.created_at,PG_Patient.updated_at).filter(PG_Patient.id==id).first()

@router.post("/patients/add",response_model=models.PatientResponse)
def add_patient(patient:models.PatientResponse,db: Session=Depends(get_pg_db),current_user:User=Depends(get_current_user)):
    obj=PG_Patient(**patient.model_dump(exclude_none=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/patients/update/{id}",response_model=models.PatientResponse)
def update_patient(id:str,patient:models.PatientResponse,db: Session=Depends(get_pg_db),current_user:User=Depends(get_current_user)):
    db.query(PG_Patient).filter(PG_Patient.id==id).update(patient.model_dump(exclude_none=True))
    db.commit()
    return db.query(PG_Patient).filter(PG_Patient.id==id).first()

@router.delete("/patients/delete/{id}",response_model=models.PatientResponse)
def delete_patient(id:str,db: Session=Depends(get_pg_db),current_user:User=Depends(get_current_user)):
    db.query(PG_Patient).filter(PG_Patient.id==id).delete()
    db.commit()
    return {"message":"Patient deleted successfully"}

@router.patch("/patients/update/{id}",response_model=models.PatientResponse)
def update_patient(id:str,patient:models.PatientResponse,db: Session=Depends(get_pg_db),current_user:User=Depends(get_current_user)):
    db.query(PG_Patient).filter(PG_Patient.id==id).update(patient.model_dump(exclude_none=True))
    db.commit()
    return db.query(PG_Patient).filter(PG_Patient.id==id).first()

@router.post("/encounters/add",response_model=models.EncountersResponse)
def add_encounter(encounter:models.EncountersResponse,db: Session=Depends(get_pg_db),current_user:User=Depends(get_current_user)):
    obj=PG_Encounters(**encounter.model_dump(exclude_none=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.post("/procedures/add",response_model=models.ProceduresResponse)
def add_procedure(procedure:models.ProceduresResponse,db: Session=Depends(get_pg_db),current_user:User=Depends(get_current_user)):
    obj=PG_Procedures(**procedure.model_dump(exclude_none=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.post("/payers/add",response_model=models.PayersResponse)
def add_payer(payer:models.PayersResponse,db: Session=Depends(get_pg_db),current_user:User=Depends(get_current_user)):
    obj=PG_Payers(**payer.model_dump(exclude_none=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/analytics/average-cost", response_model=models.AverageCostResponse)
def get_average_cost(db: Session=Depends(get_pg_db),current_user:User=Depends(get_admin)):
    result = db.query(func.avg(PG_Encounters.total_claim_amount)).scalar()
    return {"average_cost": round(result or 0, 2)}

@router.get("/analytics/procedure-coverage", response_model=models.ProcedureCoverageResponse)
def get_procedure_coverage(db: Session=Depends(get_pg_db),current_user:User=Depends(get_admin)):
    total = db.query(func.count(PG_Procedures.procedure_id)).scalar()
    covered = db.query(func.count(PG_Procedures.procedure_id)).join(PG_Patient, PG_Procedures.patient_id == PG_Patient.id).join(PG_Encounters, PG_Patient.id == PG_Encounters.patient_id).filter(PG_Encounters.payer_id.isnot(None)).distinct().scalar()
    return {"total_procedures": total, "covered_cost": covered}

@router.get("/analytics/high-revenue/encounters", response_model=List[models.RevenueReportResponse])
def get_high_revenue_encounters(db: Session=Depends(get_pg_db),current_user:User=Depends(get_admin)):
    results = db.query(func.cast(PG_Encounters.encounter_id,String).label('id'),PG_Encounters.encounter_description.label('description'),PG_Encounters.total_claim_amount.label('total_revenue')).order_by(desc(PG_Encounters.total_claim_amount)).limit(10)
    return results

@router.get("/analytics/high-revenue/procedures", response_model=List[models.RevenueReportResponse])
def get_high_revenue_procedures(db: Session=Depends(get_pg_db),current_user:User=Depends(get_admin)):
    results = db.query(func.cast(PG_Procedures.procedure_id,String).label('id'),PG_Procedures.description.label('description'),PG_Procedures.procedure_base_cost.label('total_revenue')).order_by(desc(PG_Procedures.procedure_base_cost)).limit(10)
    return results

@router.get("/analytics/payer-comparison", response_model=List[models.PayerCoverage])
def get_payer_comparison(db: Session=Depends(get_pg_db),current_user:User=Depends(get_admin)):
    results = db.query(PG_Payers.payer_name,func.count(PG_Encounters.encounter_id).label('encounter_count'),func.sum(PG_Encounters.total_claim_amount).label('total_covered_amount')).join(PG_Encounters, PG_Payers.payer_id == PG_Encounters.payer_id).group_by(PG_Payers.payer_name).order_by(desc('total_covered_amount')).all()
    return results

app.include_router(router)
app.include_router(auth.router,prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8000)