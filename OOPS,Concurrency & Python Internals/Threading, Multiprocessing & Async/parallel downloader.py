import asyncio 
import concurrent .futures 
import urllib .request 
import urllib .error 
import logging 
import time 
import os 
import sys 

logging .basicConfig (
filename ='downloader.log',
level =logging .INFO ,
format ='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
)

console_handler =logging .StreamHandler (sys .stdout )
console_handler .setLevel (logging .INFO )
formatter =logging .Formatter ('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
console_handler .setFormatter (formatter )
logging .getLogger ().addHandler (console_handler )

def download_file (url ,filename ):

    logging .info (f"Starting download: {url } -> {filename }")
    start_time =time .time ()
    try :
        urllib .request .urlretrieve (url ,filename )
        duration =time .time ()-start_time 
        logging .info (f"Finished download: {filename } in {duration :.2f}s")
        return filename 
    except urllib .error .URLError as e :
        logging .error (f"Download error for {url }: {e }")
        return None 
    except Exception as e :
        logging .error (f"Unexpected error downloading {url }: {e }")
        return None 

def process_file (filename ):

    if not filename :
        return 

    logging .info (f"Starting processing: {filename }")
    start_time =time .time ()

    count =0 
    try :
        if os .path .exists (filename ):
            file_size =os .path .getsize (filename )

            for _ in range (min (file_size ,1000000 )):
                count +=1 

        time .sleep (1 )
        duration =time .time ()-start_time 
        logging .info (f"Finished processing: {filename }. Processed {count } items in {duration :.2f}s")
    except Exception as e :
        logging .error (f"Error processing {filename }: {e }")

async def main ():
    loop =asyncio .get_running_loop ()

    urls_to_download =[]

    print ("Enter URLs and filenames to download.")
    print ("Type 'done' when you are finished adding files.")

    while True :
        url =input ("Enter URL (or 'done'): ").strip ()
        if url .lower ()=='done':
            break 

        if not url :
            print ("URL cannot be empty.")
            continue 

        filename =input ("Enter filename to save as: ").strip ()
        if not filename :
            print ("Filename cannot be empty.")
            continue 

        urls_to_download .append ((url ,filename ))

    if not urls_to_download :
        logging .info ("No files to download.")
        return 

    logging .info (f"Starting parallel execution for {len (urls_to_download )} files...")
    start_total =time .time ()

    with concurrent .futures .ThreadPoolExecutor (max_workers =5 )as executor :

        download_tasks =[]
        for url ,fname in urls_to_download :

            task =loop .run_in_executor (executor ,download_file ,url ,fname )
            download_tasks .append (task )

        downloaded_files =await asyncio .gather (*download_tasks )

        logging .info ("Downloads completed. Starting processing...")

        process_tasks =[]
        for fname in downloaded_files :
            if fname :
                task =loop .run_in_executor (executor ,process_file ,fname )
                process_tasks .append (task )

        await asyncio .gather (*process_tasks )

    duration_total =time .time ()-start_total 
    logging .info (f"All operations completed in {duration_total :.2f}s")

if __name__ =="__main__":
    if sys .platform =='win32':

        asyncio .set_event_loop_policy (asyncio .WindowsSelectorEventLoopPolicy ())

    try :
        asyncio .run (main ())
    except KeyboardInterrupt :
        pass 
