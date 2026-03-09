import json 
import os 
from datetime import datetime 

class QueryManager :
    def __init__ (self ,storage_file =None ):
        self ._storage_file =storage_file or os .path .join (os .path .dirname (__file__ ),"..","Data","student_queries.json")
        self ._queries =[]
        self ._load ()

    def _load (self ):
        if os .path .exists (self ._storage_file ):
            try :
                with open (self ._storage_file ,"r")as f :
                    self ._queries =json .load (f )
            except Exception :
                self ._queries =[]
        else :
            self ._queries =[]

    def _save (self ):
        with open (self ._storage_file ,"w")as f :
            json .dump (self ._queries ,f ,indent =2 )

    def submit_query (self ,student_name ,query_text ,target ="Principal"):
        if not query_text :
            raise ValueError ("Query text cannot be empty.")

        query_id =len (self ._queries )+1 
        query ={
        "id":query_id ,
        "student_name":student_name ,
        "target":target ,
        "query":query_text ,
        "status":"Pending",
        "reply":None ,
        "date":datetime .now ().strftime ("%Y-%m-%d %H:%M:%S")
        }
        self ._queries .append (query )
        self ._save ()
        return query_id 

    def view_pending_queries (self ,target_filter =None ):
        if target_filter :
            pending =[q for q in self ._queries if q ["status"]=="Pending"and q .get ("target")==target_filter ]
        else :
            pending =[q for q in self ._queries if q ["status"]=="Pending"]

        if not pending :
            print ("No pending queries.")
            return 

        print ("\n--- Pending Queries ---")
        for q in pending :
            print (f"ID: {q ['id']} | Student: {q ['student_name']} | Date: {q ['date']}")
            print (f"Query: {q ['query']}")
            print ("-"*30 )

    def reply_to_query (self ,query_id ,reply_text ):
        try :
            query_id =int (query_id )
        except ValueError :
            raise ValueError ("Invalid Query ID.")

        for query in self ._queries :
            if query ["id"]==query_id :
                query ["reply"]=reply_text 
                query ["status"]="Resolved"
                query ["reply_date"]=datetime .now ().strftime ("%Y-%m-%d %H:%M:%S")
                self ._save ()
                return True 

        raise ValueError (f"Query with ID {query_id } not found.")

    def view_student_queries (self ,student_name ):
        student_queries =[q for q in self ._queries if q ["student_name"].lower ()==student_name .lower ()]
        if not student_queries :
            print (f"No queries found for {student_name }.")
            return 

        print (f"\n--- Queries for {student_name } ---")
        for q in student_queries :
            print (f"ID: {q ['id']} | Date: {q ['date']} | Status: {q ['status']}")
            print (f"Query: {q ['query']}")
            if q ["reply"]:
                print (f"Reply: {q ['reply']}")
            print ("-"*30 )

    def get_pending_count (self ,target_filter =None ):
        if target_filter :
            return len ([q for q in self ._queries if q ["status"]=="Pending"and q .get ("target")==target_filter ])
        return len ([q for q in self ._queries if q ["status"]=="Pending"])
