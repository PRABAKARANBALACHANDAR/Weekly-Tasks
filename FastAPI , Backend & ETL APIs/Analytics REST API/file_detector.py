import asyncio
import logging
import os
from datetime import datetime
from sqlalchemy.orm import Session
from models import FileMetadata
from data_processor import compute_file_hash, load_patients,load_procedures,load_encounters,load_payers
logger = logging.getLogger(__name__)
INTERVAL_MINUTES=10

async def detect_changes(session_factory,dir:str):
    logger.info(f"Starting file change detection in {dir}")
    while True:
        try:
            await asyncio.sleep(INTERVAL_MINUTES*60)
            db:Session=session_factory()
            try:
                if not os.path.isdir(dir):
                    logger.warning(f"Directory {dir} does not exist")
                    continue
                for fname in os.listdir(dir):
                    if fname.endswith(".csv") or fname.endswith(".xlsx") or fname.endswith(".xls"):
                        continue
                    file_path=os.path.join(dir,fname)
                    file_hash=compute_file_hash(file_path)
                    status=os.stat(file_path)
                    last_modified=datetime.utcfromtimestamp(status.st_mtime)
                    metadata=db.query(FileMetadata).filter(FileMetadata.file_path==file_path).first()
                    if metadata and metadata.file_hash==file_hash:
                        continue
                    if not metadata:
                        metadata=FileMetadata(
                            file_name=fname,
                            file_path=file_path,
                            file_hash=file_hash,
                            file_size=status.st_size,
                            last_modified=last_modified,
                            last_processed=datetime.now(),
                            status="pending"
                        )
                        db.add(metadata)
                        db.commit()
                        db.refresh(metadata)
                    metadata.status-"processing"
                    matadata.file_hash=file_hash
                    matadata.last_modified=last_modified
                    db.commit()
                    try:
                        data_processor.process_file(file_path,db)
                        metadata.status="processed"
                        metadata.last_processed=datetime.now()
                        metadata.error_message=None
                        logger.info(f"Successfully processed file {file_path}")
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")
                        metadata.status="failed"
                        metadata.error_message=str(e)
                    finally:
                        db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in file change detection: {e}")
        finally:
            db.close()
    except asyncio.CancelledError:
        logger.info("File change detection stopped")
        break