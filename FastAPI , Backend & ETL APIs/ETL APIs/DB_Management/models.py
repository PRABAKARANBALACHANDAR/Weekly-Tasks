from pydantic import BaseModel,ConfigDict
from typing import Optional
from datetime import datetime,date
from sqlalchemy import Column,String,ForeignKey,VARCHAR
from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy.dialects.postgresql import UUID,TIMESTAMP,REAL


PGBase=declarative_base()

class PG_Patient(PGBase):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    __tablename__="patients"
    id=Column(UUID(as_uuid=True),primary_key=True,index=True)
    first_name=Column(String(255),nullable=False)
    last_name=Column(String(255),nullable=False)
    birth_date=Column(TIMESTAMP(timezone=True),nullable=False)
    death_date=Column(TIMESTAMP(timezone=True),nullable=True)
    Marital=Column(String(20),nullable=True)
    gender=Column(String(20),nullable=False)
    city=Column(String(255),nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    updated_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)
    Procedures=relationship("PG_Procedures",back_populates="patient")
    Encounters=relationship("PG_Encounters",back_populates="patient")

class PG_Procedures(PGBase):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    __tablename__="procedures"
    procedure_id=Column(UUID(as_uuid=True),primary_key=True)
    patient_id=Column(UUID(as_uuid=True),ForeignKey("patients.id"),nullable=False)
    start_date=Column(TIMESTAMP(timezone=True),nullable=False)
    end_date=Column(TIMESTAMP(timezone=True),nullable=False)
    description=Column(String(1000),nullable=False)
    procedure_base_cost=Column(REAL,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    updated_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)
    patient=relationship("PG_Patient",back_populates="Procedures")

class PG_Encounters(PGBase):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    __tablename__="encounters"
    encounter_id=Column(UUID(as_uuid=True),primary_key=True)
    patient_id=Column(UUID(as_uuid=True),ForeignKey("patients.id"),nullable=False)
    start_date=Column(TIMESTAMP(timezone=True),nullable=False)
    end_date=Column(TIMESTAMP(timezone=True),nullable=False)
    payer_id=Column(UUID(as_uuid=True),ForeignKey("payers.payer_id"),nullable=False)
    encounter_type=Column(String(100),nullable=False)
    encounter_description=Column(String(1000),nullable=False)
    base_cost=Column(REAL,nullable=False)
    total_claim_amount=Column(REAL,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    updated_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)
    patient=relationship("PG_Patient",back_populates="Encounters")
    payer=relationship("PG_Payers",back_populates="Encounters")

class PG_Payers(PGBase):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    __tablename__="payers"
    payer_id=Column(UUID(as_uuid=True),primary_key=True,index=True)
    payer_name=Column(String(255),nullable=False)
    city=Column(String(255),nullable=True)
    phone=Column(String(20),nullable=True) 
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    updated_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)
    Encounters=relationship("PG_Encounters",back_populates="payer") 


class PatientUpdate(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: UUID(as_uuid=True)
    first_name: Optional[str]=None
    last_name: Optional[str]=None
    birth_date: Optional[TIMESTAMP(timezone=True)]=None
    death_date: Optional[TIMESTAMP(timezone=True)]=None
    Marital: Optional[str]=None
    gender: Optional[str]=None
    city: Optional[str]=None

class ProcedureUpdate(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: UUID(as_uuid=True)
    start_date: Optional[TIMESTAMP(timezone=True)]=None
    end_date: Optional[TIMESTAMP(timezone=True)]=None
    description: Optional[str]=None
    procedure_base_cost: Optional[REAL]=None

class EncounterUpdate(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: UUID(as_uuid=True)
    start_date: Optional[TIMESTAMP(timezone=True)]=None
    end_date: Optional[TIMESTAMP(timezone=True)]=None
    encounter_type: Optional[str]=None
    encounter_description: Optional[str]=None
    base_cost: Optional[REAL]=None
    total_claim_amount: Optional[REAL]=None

class PayerUpdate(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: UUID(as_uuid=True)
    payer_name: Optional[str]=None
    city: Optional[str]=None
    phone: Optional[str]=None

class PatientDelete(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: UUID(as_uuid=True)

class ProcedureDelete(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: UUID(as_uuid=True)

class EncounterDelete(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: UUID(as_uuid=True)

class PayerDelete(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: UUID(as_uuid=True)

class PatientResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    first_name: Optional[str]=None
    last_name: Optional[str]=None
    gender: Optional[str]=None
    city: Optional[str]=None
    created_at: Optional[datetime]=None
    updated_at: Optional[datetime]=None 

class EncountersResponse(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: str
    start_date: Optional[datetime]=None
    end_date: Optional[datetime]=None
    encounter_type: Optional[str]=None
    encounter_description: Optional[str]=None
    base_cost: Optional[float]=None
    total_claim_amount: Optional[float]=None
    created_at: Optional[datetime]=None
    updated_at: Optional[datetime]=None

class ProceduresResponse(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: str
    start_date: Optional[datetime]=None
    end_date: Optional[datetime]=None
    description: Optional[str]=None
    procedure_base_cost: Optional[float]=None
    created_at: Optional[datetime]=None
    updated_at: Optional[datetime]=None

class PayersResponse(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id: str
    payer_name: Optional[str]=None
    city: Optional[str]=None
    phone: Optional[str]=None
    created_at: Optional[datetime]=None
    updated_at: Optional[datetime]=None

class AverageCostResponse(BaseModel):
    average_cost: Optional[float]=None

class ProcedureCoverageResponse(BaseModel):
    total_procedures: Optional[int]=None
    covered_cost: Optional[int]=None

class RevenueReportResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    description: Optional[str]=None
    total_revenue: Optional[float]=None

class PayerCoverage(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    payer_name: str
    encounter_count: int
    total_covered_amount: float  

