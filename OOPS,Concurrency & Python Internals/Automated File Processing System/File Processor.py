import time
import json
import shutil
import logging
import logging.handlers
import threading
import re
import sys
import mimetypes
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
DATA_DIR=Path("Incoming")
OUT_DIR=Path("processed_data")
LOG_DIR=Path("logs")
SUMMARIES_DIR=Path("summaries")
META_LOG=LOG_DIR / "processor.log"
SYS_LOG=LOG_DIR / "system_logs.log"
WORKERS=4
STABILITY_CHECKS=3
STABILITY_WAIT=1.0
for d in (DATA_DIR, OUT_DIR, LOG_DIR, SUMMARIES_DIR):
    d.mkdir(parents=True, exist_ok=True)
meta_logger=logging.getLogger("metadata")
meta_logger.setLevel(logging.INFO)
meta_handler=logging.handlers.RotatingFileHandler(META_LOG, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
meta_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
meta_logger.addHandler(meta_handler)
sys_logger=logging.getLogger("system")
sys_logger.setLevel(logging.INFO)
sys_handler=logging.handlers.RotatingFileHandler(SYS_LOG, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
sys_fmt=logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
sys_handler.setFormatter(sys_fmt)
sys_logger.addHandler(sys_handler)
console_handler=logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
sys_logger.addHandler(console_handler)
def wait_for_file(path: Path) -> bool:
    try:
        last=path.stat().st_size
    except FileNotFoundError:
        return False
    for _ in range(STABILITY_CHECKS):
        time.sleep(STABILITY_WAIT)
        try:
            size=path.stat().st_size
        except FileNotFoundError:
            return False
        if size==last:
            return True
        last=size
    return False
def move_file(path: Path, target: Path) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    dest=target / path.name
    if dest.exists():
        stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        dest=target / f"{path.stem}_{stamp}{path.suffix}"
    shutil.move(str(path), str(dest))
    return dest
def extract_numbers(text: str):
    return [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", text)]
def summarize(series: pd.Series):
    series=series.dropna()
    try:
        series=series.astype(float)
    except:
        return None
    if series.empty:
        return None
    return {"count": int(series.count()),"sum": float(series.sum()),"mean": float(series.mean()),"median": float(series.median())}
def handle_tabular(path):
    try:
        if path.suffix.lower()==".csv":
            df=pd.read_csv(path)
        else:
            df=pd.read_excel(path)
    except Exception as e:
        sys_logger.error(f"Error reading {path.name}: {e}")
        return {}
    result={"stats": {}, "column_count": len(df.columns)}
    sales_col=next((c for c in df.columns if 'sales' in str(c).lower()), None)
    if sales_col:
        stat=summarize(df[sales_col])
        if stat:
            result["stats"]["sales"]=stat
    return result
def handle_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data=json.load(f)
        if isinstance(data, list):
            df=pd.DataFrame(data)
            return {c: summarize(df[c]) for c in df.select_dtypes(include="number").columns}
        if isinstance(data, dict):
            nums={k: v for k, v in data.items() if isinstance(v, (int, float))}
            return {k: summarize(pd.Series([v])) for k, v in nums.items()}
    except Exception:
        pass
    return {}
def handle_txt(path):
    try:
        text=path.read_text(errors="ignore")
        lines=[line.strip() for line in text.splitlines() if line.strip()]
        if lines and ',' in lines[0]:
            import io
            df=pd.read_csv(io.StringIO(text))
            sales_col=next((c for c in df.columns if 'sales' in str(c).lower()), None)
            if sales_col:
                stat=summarize(df[sales_col])
                if stat:
                    return {"stats": {"sales": stat}, "column_count": len(df.columns)}
        nums=extract_numbers(text)
        if nums:
            return {"numbers": summarize(pd.Series(nums))}
    except Exception:
        pass
    return {}
def process_file(path: Path):
    sys_logger.info(f"Detected file: {path.name}")
    start=time.perf_counter()
    if not wait_for_file(path):
        return
    suffix=path.suffix.lower()
    mime_type, _=mimetypes.guess_type(str(path))
    category=mime_type.split('/')[0] if mime_type else (suffix.lstrip('.') if suffix else "others")
    sys_logger.info(f"Categorized: {path.name} -> {category}")
    summary={}
    try:
        if suffix in [".csv", ".xlsx", ".xls"]:
            summary=handle_tabular(path)
        elif suffix==".json":
            summary=handle_json(path)
        elif suffix==".txt":
            summary=handle_txt(path)
    except Exception as e:
        sys_logger.exception(f"Failed processing {path}")
        return
    dest=move_file(path, OUT_DIR / category)
    if summary and "stats" in summary and "sales" in summary["stats"]:
        summary_file=SUMMARIES_DIR / f"{dest.stem}_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
    elapsed=round(time.perf_counter() - start, 4)
    meta={"event": "processed","original_path": str(path),"moved_to": str(dest),"mime_type": mime_type,"size": dest.stat().st_size,"processing_time": elapsed,"summary": summary}
    meta_logger.info(f"METADATA: {json.dumps(meta)}")
    sys_logger.info(f"Log added: metadata for {dest.name} saved to log file.")
class Watcher(FileSystemEventHandler):
    def __init__(self, pool):
        self.pool=pool
    def on_created(self, event):
        if not event.is_directory:
            path=Path(event.src_path)
            self.pool.submit(process_file, path)
    def on_moved(self, event):
        if not event.is_directory:
            path=Path(event.dest_path)
            if path.parent==DATA_DIR:
                self.pool.submit(process_file, path)
def main():
    sys_logger.info("File processor started. Type 'exit' to stop.")
    observer=None
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            for f in DATA_DIR.iterdir():
                if f.is_file():
                    pool.submit(process_file, f)
            observer=Observer()
            observer.schedule(Watcher(pool), str(DATA_DIR), recursive=False)
            observer.start()
            while True:
                user_input=sys.stdin.readline().strip().lower()
                if user_input=='exit':
                    break
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if observer:
            observer.stop()
            observer.join()
        sys_logger.info("System execution stopped.")
if __name__=="__main__":
    main()
