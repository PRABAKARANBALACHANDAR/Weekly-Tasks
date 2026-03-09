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
    BASE_DIR   = Path(r"C:\Prabakaran Intern\Weekly-Tasks\Data Engineering Core,Pandas & SQL\Pandas Analytics + Mini Data Pipeline")
    CSV_PATH   = BASE_DIR / "automobile_dataset.csv"
    OUTPUT_DIR = BASE_DIR / "output"
    CLEANED_DATA_PATH = OUTPUT_DIR / "automobiles_cleaned.json"
    KPI_PATH          = OUTPUT_DIR / "automobile_kpis.json"
    DB_NAME     = os.getenv("MYSQL_DATABASE", "automobile_db")
    DB_USER     = os.getenv("MYSQL_USER",     "root")
    DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
    DB_HOST     = os.getenv("MYSQL_HOST",     "localhost")
    DB_PORT     = os.getenv("MYSQL_PORT",     "3306")
    @classmethod
    def get_db_url(cls):
        if cls.DB_PASSWORD is None:
            logger.error("MYSQL_PASSWORD environment variable is not set.")
            sys.exit(1)
        pwd = quote_plus(cls.DB_PASSWORD)
        return f"mysql+pymysql://{cls.DB_USER}:{pwd}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    @classmethod
    def get_base_db_url(cls):
        pwd = quote_plus(cls.DB_PASSWORD or "")
        return f"mysql+pymysql://{cls.DB_USER}:{pwd}@{cls.DB_HOST}:{cls.DB_PORT}"
class AutomobilePipeline:
    def __init__(self):
        self.config = Config()
        self.config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.engine = None
    def ingest(self) -> pd.DataFrame:
        if not self.config.CSV_PATH.exists():
            logger.error(f"CSV not found: {self.config.CSV_PATH}")
            raise FileNotFoundError(f"CSV not found: {self.config.CSV_PATH}")
        logger.info(f"[INGEST] Loading data from {self.config.CSV_PATH}")
        try:
            df = pd.read_csv(self.config.CSV_PATH, low_memory=False)
            logger.info(f"[INGEST] Loaded {len(df)} rows, {len(df.columns)} columns.")
            logger.info(f"[INGEST] Columns: {list(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"[INGEST] Failed: {e}")
            raise
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("[CLEAN] Starting data cleaning...")
        df = df.copy()
        df.columns = (df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("-", "_").str.replace(r"[^\w_]", "", regex=True))
        logger.info(f"[CLEAN] Normalised columns: {list(df.columns)}")
        df.replace("?", pd.NA, inplace=True)
        before = len(df)
        df.dropna(how="all", inplace=True)
        df.reset_index(drop=True, inplace=True)
        if len(df) < before:
            logger.info(f"[CLEAN] Dropped {before - len(df)} fully-empty rows.")
        before = len(df)
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        if len(df) < before:
            logger.info(f"[CLEAN] Removed {before - len(df)} duplicate rows.")
        numeric_cols = [
            "price", "horsepower", "peak_rpm", "normalized_losses",
            "bore", "stroke", "compression_ratio", "engine_size",
            "curb_weight", "height", "width", "length", "wheel_base",
            "city_mpg", "highway_mpg", "num_of_doors"
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        str_cols = df.select_dtypes(include="object").columns
        for c in str_cols:
            df[c] = df[c].astype(str).str.strip().replace({"nan": pd.NA, "<NA>": pd.NA})
        before = len(df)
        df.dropna(subset=["price"], inplace=True)
        df.reset_index(drop=True, inplace=True)
        logger.info(f"[CLEAN] Dropped {before - len(df)} rows with missing price.")
        logger.info(f"[CLEAN] Final shape after cleaning: {df.shape}")
        return df
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("[TRANSFORM] Deriving new features...")
        df = df.copy()
        if "city_mpg" in df.columns and "highway_mpg" in df.columns:
            df["avg_mpg"] = ((df["city_mpg"] + df["highway_mpg"]) / 2).round(2)
        if "horsepower" in df.columns and "curb_weight" in df.columns:
            df["power_to_weight"] = (df["horsepower"] / df["curb_weight"] * 100).round(4)
        if "price" in df.columns:
            bins   = [0, 8000, 15000, 25000, float("inf")]
            labels = ["budget", "mid_range", "premium", "luxury"]
            df["price_segment"] = pd.cut(df["price"], bins=bins, labels=labels, right=False)
        if "aspiration" in df.columns:
            df["is_turbo"] = (df["aspiration"].str.lower() == "turbo").astype(int)
        logger.info("[TRANSFORM] Derived columns: avg_mpg, power_to_weight, price_segment, is_turbo")
        return df
    def compute_kpis(self, df: pd.DataFrame) -> dict:
        logger.info("[KPIs] Computing KPIs...")
        kpis = {}
        kpis["total_records"] = len(df)
        if "price" in df.columns:
            kpis["price_stats"] = {
                "min":    round(float(df["price"].min()), 2),
                "max":    round(float(df["price"].max()), 2),
                "mean":   round(float(df["price"].mean()), 2),
                "median": round(float(df["price"].median()), 2),
                "std":    round(float(df["price"].std()), 2),
            }
            logger.info(f"[KPIs] Price stats: {kpis['price_stats']}")
        if {"make", "price"}.issubset(df.columns):
            top5 = (
                df[["make", "engine_type", "fuel_type", "horsepower", "price"]]
                .dropna(subset=["price"])
                .sort_values("price", ascending=False)
                .head(5)
                .to_dict(orient="records")
            )
            kpis["top_5_most_expensive"] = top5
            logger.info(f"[KPIs] Top 5 most expensive: {[r.get('make') for r in top5]}")
        if "engine_type" in df.columns:
            eng_dist = df["engine_type"].value_counts().to_dict()
            kpis["engine_type_distribution"] = eng_dist
            if "price" in df.columns:
                eng_price = (df.groupby("engine_type")["price"].agg(avg_price="mean", count="count").round(2).reset_index().sort_values("avg_price", ascending=False).to_dict(orient="records"))
                kpis["avg_price_by_engine_type"] = eng_price
                logger.info(f"[KPIs] Engine types found: {list(eng_dist.keys())}")
            if "horsepower" in df.columns:
                kpis["avg_hp_by_engine_type"] = (df.groupby("engine_type")["horsepower"].mean().round(2).sort_values(ascending=False).to_dict())
        if "fuel_system" in df.columns:
            fs_dist = df["fuel_system"].value_counts().to_dict()
            kpis["fuel_system_distribution"] = fs_dist
            if "horsepower" in df.columns:
                kpis["avg_hp_by_fuel_system"] = (df.groupby("fuel_system")["horsepower"].agg(avg_hp="mean", count="count").round(2).reset_index().sort_values("avg_hp", ascending=False).to_dict(orient="records"))
                logger.info(f"[KPIs] Fuel systems found: {list(fs_dist.keys())}")
            if "price" in df.columns:
                kpis["avg_price_by_fuel_system"] = (df.groupby("fuel_system")["price"].mean().round(2).sort_values(ascending=False).to_dict())
        if "horsepower" in df.columns:
            kpis["horsepower_stats"] = {
                "min":    round(float(df["horsepower"].min()), 2),
                "max":    round(float(df["horsepower"].max()), 2),
                "mean":   round(float(df["horsepower"].mean()), 2),
                "median": round(float(df["horsepower"].median()), 2),
            }
            logger.info(f"[KPIs] Horsepower stats: {kpis['horsepower_stats']}")
        if "fuel_type" in df.columns:
            kpis["fuel_type_breakdown"] = df["fuel_type"].value_counts().to_dict()
            if "price" in df.columns:
                kpis["avg_price_by_fuel_type"] = (df.groupby("fuel_type")["price"].mean().round(2).to_dict())
        if "aspiration" in df.columns:
            kpis["aspiration_breakdown"] = df["aspiration"].value_counts().to_dict()
            if "price" in df.columns:
                kpis["avg_price_by_aspiration"] = (df.groupby("aspiration")["price"].mean().round(2).to_dict())
            if "horsepower" in df.columns:
                kpis["avg_hp_by_aspiration"] = (df.groupby("aspiration")["horsepower"].mean().round(2).to_dict())
        if "make" in df.columns and "price" in df.columns:
            make_price = (df.groupby("make")["price"].agg(avg_price="mean", num_models="count").round(2).reset_index().sort_values("avg_price", ascending=False).to_dict(orient="records"))
            kpis["make_avg_price_ranking"] = make_price
            logger.info(f"[KPIs] Makes analysed: {[r['make'] for r in make_price]}")
        if "body_style" in df.columns and "price" in df.columns:
            kpis["avg_price_by_body_style"] = (df.groupby("body_style")["price"].mean().round(2).sort_values(ascending=False).to_dict())
        if "drive_wheels" in df.columns and "price" in df.columns:
            kpis["avg_price_by_drive_wheels"] = (df.groupby("drive_wheels")["price"].mean().round(2).sort_values(ascending=False).to_dict())
        if "price_segment" in df.columns:
            kpis["price_segment_distribution"] = (df["price_segment"].value_counts().to_dict())
        if "is_turbo" in df.columns and "price" in df.columns:
            kpis["turbo_vs_non_turbo"] = {
                "turbo_count":         int(df["is_turbo"].sum()),
                "non_turbo_count":     int((df["is_turbo"] == 0).sum()),
                "avg_price_turbo":     round(float(df[df["is_turbo"] == 1]["price"].mean()), 2),
                "avg_price_non_turbo": round(float(df[df["is_turbo"] == 0]["price"].mean()), 2),
            }
        if "avg_mpg" in df.columns and "fuel_type" in df.columns:
            kpis["avg_mpg_by_fuel_type"] = (df.groupby("fuel_type")["avg_mpg"].mean().round(2).to_dict())
        try:
            with open(self.config.KPI_PATH, "w") as f:
                json.dump(kpis, f, indent=2, default=str)
            logger.info(f"[KPIs] Saved to {self.config.KPI_PATH}")
        except Exception as e:
            logger.error(f"[KPIs] Failed to save KPI JSON: {e}")
        return kpis
    def export_json(self, df: pd.DataFrame):
        logger.info("[EXPORT JSON] Exporting cleaned data...")
        try:
            export_df = df.copy()
            for col in export_df.select_dtypes(include="category").columns:
                export_df[col] = export_df[col].astype(str)
            export_df.to_json(
                self.config.CLEANED_DATA_PATH,
                orient="records",
                indent=2,
                default_handler=str
            )
            logger.info(f"[EXPORT JSON] {len(df)} records saved to {self.config.CLEANED_DATA_PATH}")
        except Exception as e:
            logger.error(f"[EXPORT JSON] Failed: {e}")
    def export_mysql(self, df: pd.DataFrame, kpis: dict):
        logger.info("[EXPORT MySQL] Connecting to MySQL...")
        try:
            base_engine = create_engine(self.config.get_base_db_url())
            with base_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{self.config.DB_NAME}`"))
                conn.commit()
            logger.info(f"[EXPORT MySQL] Database '{self.config.DB_NAME}' ready.")
            self.engine = create_engine(self.config.get_db_url())
            export_df = df.copy()
            for col in export_df.select_dtypes(include="category").columns:
                export_df[col] = export_df[col].astype(str)
            export_df.to_sql("automobiles", self.engine, if_exists="replace", index=False)
            logger.info(f"[EXPORT MySQL] {len(df)} rows written to 'automobiles' table.")
            kpi_rows = [
                {"kpi_key": k, "kpi_value": json.dumps(v, default=str)}
                for k, v in kpis.items()
            ]
            kpi_df = pd.DataFrame(kpi_rows)
            kpi_df.to_sql("automobile_kpis", self.engine, if_exists="replace", index=False)
            logger.info(f"[EXPORT MySQL] {len(kpi_df)} KPI rows written to 'automobile_kpis' table.")
        except SQLAlchemyError as e:
            logger.error(f"[EXPORT MySQL] Database error: {e}")
    def validate(self, df: pd.DataFrame):
        logger.info("[VALIDATE] Running validation checks...")
        logger.info(f"[VALIDATE] Total records: {len(df)}")
        key_cols = ["price", "horsepower", "engine_type", "fuel_system", "make"]
        for col in key_cols:
            if col in df.columns:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    logger.warning(f"[VALIDATE] '{col}' has {null_count} null values.")
                else:
                    logger.info(f"[VALIDATE] '{col}' -- no nulls. OK")
        if "price" in df.columns:
            if df["price"].min() < 0:
                logger.warning("[VALIDATE] Negative prices detected!")
            else:
                logger.info("[VALIDATE] All prices are non-negative. OK")
        if "horsepower" in df.columns:
            if df["horsepower"].min() <= 0:
                logger.warning("[VALIDATE] Zero or negative horsepower detected!")
            else:
                logger.info("[VALIDATE] All horsepower values are positive. OK")
    def print_insights(self, kpis: dict):
        sep = "=" * 60
        print(f"\n{sep}")
        print("  AUTOMOBILE DATASET - KEY INSIGHTS")
        print(sep)
        print(f"\n[*] Total Records: {kpis.get('total_records', 'N/A')}")
        if ps := kpis.get("price_stats"):
            print(f"\n[PRICE] Price Statistics:")
            print(f"   Min:    ${ps['min']:,.2f}")
            print(f"   Max:    ${ps['max']:,.2f}")
            print(f"   Mean:   ${ps['mean']:,.2f}")
            print(f"   Median: ${ps['median']:,.2f}")
            print(f"   Std:    ${ps['std']:,.2f}")
        if hs := kpis.get("horsepower_stats"):
            print(f"\n[HP] Horsepower Statistics:")
            print(f"   Min:    {hs['min']} hp")
            print(f"   Max:    {hs['max']} hp")
            print(f"   Mean:   {hs['mean']} hp")
            print(f"   Median: {hs['median']} hp")
        if et := kpis.get("engine_type_distribution"):
            print(f"\n[ENGINE] Engine Type Distribution:")
            for k, v in sorted(et.items(), key=lambda x: -x[1]):
                print(f"   {k:<10}: {v} cars")
        if fs := kpis.get("fuel_system_distribution"):
            print(f"\n[FUEL SYS] Fuel System Distribution:")
            for k, v in sorted(fs.items(), key=lambda x: -x[1]):
                print(f"   {k:<10}: {v} cars")
        if ft := kpis.get("fuel_type_breakdown"):
            print(f"\n[FUEL TYPE] Fuel Type Breakdown:")
            for k, v in ft.items():
                print(f"   {k}: {v} cars")
        if asp := kpis.get("aspiration_breakdown"):
            print(f"\n[ASPIRATION] Aspiration (std vs turbo):")
            for k, v in asp.items():
                print(f"   {k}: {v} cars")
            if ap := kpis.get("avg_price_by_aspiration"):
                for k, v in ap.items():
                    print(f"   Avg price ({k}): ${v:,.2f}")
        if tv := kpis.get("turbo_vs_non_turbo"):
            print(f"\n[TURBO] Turbo vs Non-Turbo:")
            print(f"   Turbo:     {tv['turbo_count']} cars  | Avg price: ${tv['avg_price_turbo']:,.2f}")
            print(f"   Non-Turbo: {tv['non_turbo_count']} cars | Avg price: ${tv['avg_price_non_turbo']:,.2f}")
        if mp := kpis.get("make_avg_price_ranking"):
            print(f"\n[RANKING] Make Avg Price Ranking (Top 10):")
            for row in mp[:10]:
                print(f"   {row['make']:<20}: ${row['avg_price']:>10,.2f}  ({int(row['num_models'])} models)")
        if t5 := kpis.get("top_5_most_expensive"):
            print(f"\n[TOP 5] Most Expensive Cars:")
            for i, row in enumerate(t5, 1):
                print(f"   {i}. {row.get('make','?'):<15} | {row.get('engine_type','?'):<8} | "
                      f"{row.get('fuel_type','?'):<6} | {row.get('horsepower','?')} hp | ${row.get('price','?'):,.2f}")
        if ps_dist := kpis.get("price_segment_distribution"):
            print(f"\n[SEGMENTS] Price Segment Distribution:")
            for k, v in ps_dist.items():
                print(f"   {k:<12}: {v} cars")
        if mpg := kpis.get("avg_mpg_by_fuel_type"):
            print(f"\n[MPG] Avg MPG by Fuel Type:")
            for k, v in mpg.items():
                print(f"   {k}: {v} mpg")
        print(f"\n{sep}\n")
    def run(self):
        logger.info("  AUTOMOBILE DATA PIPELINE -- STARTING")
        try:
            df = self.ingest()
            df = self.clean(df)
            df = self.transform(df)
            kpis = self.compute_kpis(df)
            self.print_insights(kpis)
            self.export_json(df)
            self.export_mysql(df, kpis)
            self.validate(df)

            logger.info("  PIPELINE COMPLETED SUCCESSFULLY")

        except Exception as e:
            logger.critical(f"Pipeline failed: {e}")
            sys.exit(1)
if __name__ == "__main__":
    pipeline = AutomobilePipeline()
    pipeline.run()
