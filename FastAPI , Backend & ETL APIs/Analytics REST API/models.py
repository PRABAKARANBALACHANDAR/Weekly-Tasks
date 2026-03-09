import uuid
from sqlalchemy import Column,String,DateTime,Float
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

Base=declarative_base()

class FileMetaData(Base):
    __tablename__="file_metadata"
    id=Column(UUID(as_uuid=True),primary_key=True,index=True)
    file_name=Column(String(255),nullable=False)
    file_path=Column(String(1000),nullable=False)
    file_hash=Column(String(255),nullable=False)
    file_size=Column(Float,nullable=False)
    last_modified=Column(DateTime,nullable=False)
    last_processed=Column(DateTime,nullable=False)
    status=Column(String(255),nullable=False)
    uploaded_at=Column(DateTime,nullable=False)
    