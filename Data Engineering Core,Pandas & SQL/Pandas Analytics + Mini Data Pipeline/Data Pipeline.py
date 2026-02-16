import os
import sys
import json
import logging
from pathlib import Path
from urllib.parse import quote_plus
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log")
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    CSV_PATH = Path(r"C:\Prabakaran Intern\Weekly-Tasks\Data Engineering Core,Pandas & SQL\Pandas Analytics + Mini Data Pipeline\student-dataset.csv")
    OUTPUT_DIR = Path("output")
    CLEANED_DATA_PATH = OUTPUT_DIR / "students_cleaned.json"
    KPI_PATH = OUTPUT_DIR / "kpis.json"
    VALIDATOR_SQL_PATH = Path("validator.sql")

    DB_NAME = os.getenv("MYSQL_DATABASE", "student_db")
    DB_USER = os.getenv("MYSQL_USER", "root")
    DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
    DB_HOST = os.getenv("MYSQL_HOST", "localhost")
    DB_PORT = os.getenv("MYSQL_PORT", "3306")

    @classmethod
    def get_db_connection_str(cls):
        if cls.DB_PASSWORD is None:
            logger.error("MYSQL_PASSWORD environment variable is not set.")
            sys.exit(1)
        pwd = quote_plus(cls.DB_PASSWORD)
        return f"mysql+mysqlconnector://{cls.DB_USER}:{pwd}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

class StudentDataPipeline:
    def __init__(self):
        self.config = Config()
        self.config.OUTPUT_DIR.mkdir(exist_ok=True)
        self.engine = None
        
    def load_data(self) -> pd.DataFrame:
        if not self.config.CSV_PATH.exists():
            logger.error(f"Input file not found: {self.config.CSV_PATH}")
            raise FileNotFoundError(f"Input file not found: {self.config.CSV_PATH}")
        
        logger.info(f"Loading data from {self.config.CSV_PATH}...")
        try:
            df = pd.read_csv(self.config.CSV_PATH, low_memory=False)
            logger.info(f"Loaded {len(df)} rows.")
            return df
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Cleaning data...")
        df = df.copy()
        
        df.columns = (df.columns.str.strip()
                                .str.lower()
                                .str.replace(" ", "_")
                                .str.replace(".", "_")
                                .str.replace(r"[^\w_]", "", regex=True))
        
        if "id" in df.columns:
            df = df.rename(columns={"id": "student_id"})

        initial_count = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        if len(df) < initial_count:
            logger.info(f"Removed {initial_count - len(df)} duplicate rows.")

        str_cols = df.select_dtypes(include="object").columns
        for c in str_cols:
            df[c] = df[c].astype(str).str.strip().replace({"nan": pd.NA})

        numeric_cols = [c for c in df.columns if "grade" in c or "rating" in c or c in ["age"]]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        score_cols = [c for c in df.columns if "grade" in c]
        if score_cols:
            before_drop = len(df)
            df = df.dropna(subset=score_cols, how="all").reset_index(drop=True)
            if len(df) < before_drop:
                logger.info(f"Dropped {before_drop - len(df)} rows with missing scores.")
                
        return df

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Transforming data...")
        df = df.copy()
        
        score_cols = [c for c in df.columns if "grade" in c]
        if score_cols:
            df["score_avg"] = df[score_cols].mean(axis=1)
            df["pass_flag"] = (df["score_avg"] >= 2.0).astype(int)
            df.loc[df["score_avg"].isna(), "pass_flag"] = 0
        else:
            logger.warning("No grade columns found for scoring.")

        if "age" in df.columns:
            bins = [0, 12, 15, 18, 30, 100]
            labels = ["child", "early_teen", "teen", "young_adult", "adult"]
            df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=False)
            
        return df

    def calculate_kpis(self, df: pd.DataFrame) -> dict:
        logger.info("Calculating KPIs...")
        total = len(df)
        avg_score = float(df["score_avg"].mean()) if "score_avg" in df.columns else None
        
        pass_rate = None
        if "pass_flag" in df.columns and total > 0:
            pass_rate = round((df["pass_flag"].sum() / total) * 100, 2)
            
        top5 = []
        if "student_id" in df.columns and "score_avg" in df.columns:
            top5 = df.sort_values("score_avg", ascending=False).head(5)[["student_id", "score_avg"]].to_dict(orient="records")

        kpis = {
            "total_students": total,
            "average_score": avg_score,
            "pass_rate_pct": pass_rate,
            "top_5_students": top5
        }
        
        try:
            with open(self.config.KPI_PATH, "w") as f:
                json.dump(kpis, f, indent=2)
            logger.info(f"KPIs saved to {self.config.KPI_PATH}")
        except Exception as e:
            logger.error(f"Failed to save KPIs: {e}")
            
        return kpis

    def export_json(self, df: pd.DataFrame):
        base_cols = ["student_id", "name", "age", "gender", "score_avg", "pass_flag", "age_group"]
        grade_cols = [c for c in df.columns if "grade" in c]
        export_cols = [c for c in base_cols + grade_cols if c in df.columns]
        
        logger.info(f"Exporting {len(df)} records to JSON...")
        df[export_cols].to_json(self.config.CLEANED_DATA_PATH, orient="records", indent=2)
        logger.info(f"Data exported to {self.config.CLEANED_DATA_PATH}")

    def export_mysql(self, df: pd.DataFrame):
        logger.info("Exporting data to MySQL...")
        conn_str = self.config.get_db_connection_str()
        try:
            self.engine = create_engine(conn_str)
            base_conn_str = f"mysql+mysqlconnector://{self.config.DB_USER}:{quote_plus(self.config.DB_PASSWORD)}@{self.config.DB_HOST}:{self.config.DB_PORT}"
            temp_engine = create_engine(base_conn_str)
            with temp_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {self.config.DB_NAME}"))
            
            df.to_sql("students", self.engine, if_exists="replace", index=False)
            logger.info("Data successfully exported to MySQL 'students' table.")
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")

    def validate_data(self, df: pd.DataFrame):
        logger.info("Validating final dataset...")
        logger.info(f"Stage count: {len(df)}")
        
        if "student_id" in df.columns:
            dupes = df.duplicated(subset=["student_id"]).sum()
            if dupes > 0:
                logger.warning(f"Found {dupes} duplicate student_ids!")
            else:
                logger.info("No duplicate student_ids found.")

    def run_sql_validation(self):
        if not self.config.VALIDATOR_SQL_PATH.exists():
            logger.warning(f"Validator SQL file not found at {self.config.VALIDATOR_SQL_PATH}. Skipping SQL validation.")
            return

        if not self.engine:
            logger.warning("No database connection available. Skipping SQL validation.")
            return

        logger.info("Running SQL validation queries...")
        try:
            with open(self.config.VALIDATOR_SQL_PATH, "r") as f:
                queries = f.read().split(";")
            
            with self.engine.connect() as conn:
                for i, query in enumerate(queries):
                    query = query.strip()
                    if not query:
                        continue
                    
                    logger.info(f"Executing Query {i+1}: {query[:50]}...")
                    result = conn.execute(text(query))
                    if result.returns_rows:
                        rows = result.fetchall()
                        logger.info(f"Query {i+1} Result: {rows}")
        except Exception as e:
            logger.error(f"SQL Validation failed: {e}")

    def run(self):
        try:
            df = self.load_data()
            df = self.clean_data(df)
            df = self.transform_data(df)
            self.calculate_kpis(df)
            self.export_json(df)
            self.export_mysql(df)
            self.validate_data(df)
            self.run_sql_validation()
            logger.info("Pipeline completed successfully.")
        except Exception as e:
            logger.critical(f"Pipeline failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    pipeline = StudentDataPipeline()
    pipeline.run()
