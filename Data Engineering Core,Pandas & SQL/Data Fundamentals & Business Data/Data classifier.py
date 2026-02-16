import time
import json
import shutil
import logging
import logging.handlers
import re
import sys
import math
import mimetypes
import csv
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import xml.etree.ElementTree as ET
from collections import Counter

data_dir=Path("incoming")
output_dir=Path("processed_data")
log_dir=Path("logs")

meta_log_file=log_dir / "processor.log"
system_log_file=log_dir / "system.log"

workers=4
stability_checks=3
stability_wait=1.0

for folder in [data_dir, output_dir, log_dir]:
    folder.mkdir(parents=True, exist_ok=True)

meta_logger=logging.getLogger("meta")
meta_logger.setLevel(logging.INFO)

meta_handler=logging.handlers.RotatingFileHandler(
    meta_log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
)
meta_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
meta_logger.addHandler(meta_handler)

system_logger=logging.getLogger("system")
system_logger.setLevel(logging.INFO)

system_handler=logging.handlers.RotatingFileHandler(
    system_log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
)
system_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
system_logger.addHandler(system_handler)

console=logging.StreamHandler()
console.setFormatter(logging.Formatter("%(message)s"))
system_logger.addHandler(console)

stopwords={
    "the", "is", "in", "at", "of", "on", "and", "a", "to",
    "for", "with", "as", "by", "an", "it", "this", "that"
}

def is_binary(path):
    try:
        with open(path, "rb") as f:
            chunk=f.read(1024)
            return b"\0" in chunk
    except Exception:
        return False

def is_structured(text):
    lines=[line for line in text.split("\n") if line.strip()]
    if len(lines) < 2:
        return False
    
    delimiters=[",", "\t", "|", ";"]
    for delim in delimiters:
        try:
            reader=csv.reader(lines, delimiter=delim)
            counts=[len(row) for row in reader if row] 
            if not counts:
                continue
            mode_data=Counter(counts).most_common(1)
            if not mode_data:
                continue                
            mode_count, frequency=mode_data[0]
            if mode_count > 1 and frequency / len(counts) >= 0.9:
                return True
        except Exception:
            continue
            
    return False

def is_semi_structured(text):
    try:
        json.loads(text)
        return True
    except (ValueError, json.JSONDecodeError):
        pass
    try:
        ET.fromstring(text)
        return True
    except ET.ParseError:
        pass
    return False

def entropy(text):
    freq=Counter(text)
    total=len(text)
    return -sum((c / total) * math.log2(c / total) for c in freq.values() if c)

def is_natural_language(text):
    words=re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    if len(words) < 5:
        return False
    stop_ratio=sum(1 for w in words if w in stopwords) / len(words)
    return stop_ratio > 0.1 and entropy(text) > 3.5

def classify(path):
    if is_binary(path):
        return "unstructured/bin"
    try:
        text=path.read_text(errors="ignore")
    except Exception:
        text=None
    if text:
        if is_structured(text):
            return "structured"
        if is_semi_structured(text):
            return "semi_structured"
        if is_natural_language(text):
            return "unstructured/text"
    mime_type, _=mimetypes.guess_type(str(path))
    if mime_type:
        main_type=mime_type.split("/")[0]
        return f"unstructured/{main_type}"
    return "unstructured/unknown"

def wait_until_stable(path):
    try:
        last_size=path.stat().st_size
    except FileNotFoundError:
        return False
    for _ in range(stability_checks):
        time.sleep(stability_wait)
        try:
            new_size=path.stat().st_size
        except FileNotFoundError:
            return False
        if new_size==last_size:
            return True
        last_size=new_size
    return False

def move_file(path, category):
    target=output_dir / category
    target.mkdir(parents=True, exist_ok=True)
    destination=target / path.name
    if destination.exists():
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        destination=target / f"{path.stem}_{timestamp}{path.suffix}"
    shutil.move(str(path), str(destination))
    return destination

def process_file(path):
    system_logger.info(f"detected: {path.name}")
    if not wait_until_stable(path):
        return
    start_time=time.perf_counter()
    category=classify(path)
    system_logger.info(f"classified as: {category}")
    try:
        new_location=move_file(path, category)
    except Exception:
        system_logger.exception("failed to move file")
        return
    elapsed=round(time.perf_counter() - start_time, 4)
    metadata={
        "event": "processed",
        "original_path": str(path),
        "moved_to": str(new_location),
        "category": category,
        "size": new_location.stat().st_size,
        "processing_time": elapsed
    }
    meta_logger.info(json.dumps(metadata))
    system_logger.info(f"done: {new_location.name}")

class FileWatcher(FileSystemEventHandler):
    def __init__(self, pool):
        self.pool=pool

    def on_created(self, event):
        if not event.is_directory:
            self.pool.submit(process_file, Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self.pool.submit(process_file, Path(event.dest_path))

def main():
    system_logger.info("file processor started (type 'exit' to stop)")
    observer=None
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for file in data_dir.iterdir():
                if file.is_file():
                    pool.submit(process_file, file)
            observer=Observer()
            observer.schedule(FileWatcher(pool), str(data_dir), recursive=False)
            observer.start()
            while True:
                user_input=sys.stdin.readline().strip().lower()
                if user_input=="exit":
                    break
            if observer:
                observer.stop()
                observer.join()
                observer=None
    except KeyboardInterrupt:
        pass
    finally:
        if observer:
            observer.stop()
            observer.join()
        system_logger.info("system stopped")

if __name__=="__main__":
    main()
