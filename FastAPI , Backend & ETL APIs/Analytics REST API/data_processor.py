import io
import logging
from typing import List, Optional,Dict,Tuple
from datetime import datetime,date
import pandas as pd
from sqlalchemy.orm import Session
from PatientMaintenance_Postgres import Patient,Procedures,Encounters,Payers
import hashlib
import os

logger=logging.getLogger(__name__)

PATIENT_COLUMNS=["id","first","last","birthdate","deathdate","marital","gender","city"]
PROCEDURE_COLUMNS=["patient","encounter","start","stop","description","base_cost"]
ENCOUNTER_COLUMNS=["patient","id","start","stop","payer","encounterclass","description","base_encounter_cost","total_claim_cost"]
PAYER_COLUMNS=["id","name","city","phone"]

PATIENT_COL_MAP={"id":"id","first":"first_name","last":"last_name","birthdate":"birth_date","deathdate":"death_date","marital":"Marital","gender":"gender","city":"city"}
PROCEDURE_COL_MAP={"patient":"patient_id","encounter":"procedure_id","start":"start_date","stop":"end_date","description":"description","base_cost":"procedure_base_cost"}
ENCOUNTER_COL_MAP={"patient":"patient_id","id":"encounter_id","start":"start_date","stop":"end_date","payer":"payer_id","encounterclass":"encounter_type","description":"encounter_description","base_encounter_cost":"base_cost","total_claim_cost":"total_claim_amount"}
PAYER_COL_MAP={"id":"payer_id","name":"payer_name","city":"city","phone":"phone"}

def clean_column_name(col:str)->str:
    col=str(col.strip().lower().replace(" ","_").replace("-","_"))
    return col

def filter_columns(df:pd.DataFrame,columns:List[str])->pd.DataFrame:
    return df[[col for col in columns if col in df.columns]]

def rename_columns(df:pd.DataFrame,col_map:Dict[str,str])->pd.DataFrame:
    return df.rename(columns=col_map)

def clean_data(df:pd.DataFrame)->pd.DataFrame:
    df=df.replace('NA',pd.NA).replace('N/A',pd.NA).replace('',pd.NA)
    for col in ['birth_date','death_date','start_date','end_date']:
        if col in df.columns:
            df[col]=pd.to_datetime(df[col],errors='coerce')
    df=df.astype(object)
    df=df.where(pd.notnull(df), None)
    return df

def transform_gender(df:pd.DataFrame)->pd.DataFrame:
    df['gender']=df['gender'].replace({'M':'Male','F':'Female'})
    return df

def transform_marital(df:pd.DataFrame)->pd.DataFrame:
    df['Marital']=df['Marital'].replace({'M':'Married','S':'Single'})
    return df

def compute_file_hash(file_path:str)->str:
    h=hashlib.sha256()
    with open(file_path,'rb') as f:
        for chunk in iter(lambda:f.read(4096),b''):
            h.update(chunk)
    return h.hexdigest()

def load_patients

def process_patients(df:pd.DataFrame)->pd.DataFrame:
    df.columns=[clean_column_name(col) for col in df.columns]
    df=filter_columns(df,PATIENT_COLUMNS)
    df=rename_columns(df,PATIENT_COL_MAP)
    df=transform_gender(df)
    df=transform_marital(df)
    df=clean_data(df)
    return df

def process_procedures(df:pd.DataFrame)->pd.DataFrame:
    df.columns=[clean_column_name(col) for col in df.columns]
    df=filter_columns(df,PROCEDURE_COLUMNS)
    df=rename_columns(df,PROCEDURE_COL_MAP)
    df=clean_data(df)
    return df

def process_encounters(df:pd.DataFrame)->pd.DataFrame:
    df.columns=[clean_column_name(col) for col in df.columns]
    df=filter_columns(df,ENCOUNTER_COLUMNS)
    df=rename_columns(df,ENCOUNTER_COL_MAP)
    df=clean_data(df)
    return df

def process_payers(df:pd.DataFrame)->pd.DataFrame:
    df.columns=[clean_column_name(col) for col in df.columns]
    df=filter_columns(df,PAYER_COLUMNS)
    df=rename_columns(df,PAYER_COL_MAP)
    df=clean_data(df)
    return df

