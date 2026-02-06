import json 
import os 
from datetime import datetime 

class LeaveManager :
    def __init__ (self ,storage_file =None ):
        self ._storage_file =storage_file or os .path .join (os .path .dirname (__file__ ),"..","Data","leaves.json")
        self ._leaves =[]
        self ._load ()

    def _load (self ):
        if os .path .exists (self ._storage_file ):
            try :
                with open (self ._storage_file ,"r")as f :
                    self ._leaves =json .load (f )
            except Exception :
                self ._leaves =[]
        else :
            self ._leaves =[]

    def _save (self ):
        with open (self ._storage_file ,"w")as f :
            json .dump (self ._leaves ,f ,indent =2 )

    def apply_leave (self ,applicant_name ,start_date ,days ,reason ,role ="Student"):
        if not applicant_name or not start_date or days <=0 :
            raise ValueError ("Invalid leave details.")

        leave_id =len (self ._leaves )+1 
        leave_request ={
        "id":leave_id ,
        "applicant_name":applicant_name ,
        "student_name":applicant_name ,
        "role":role ,
        "start_date":start_date ,
        "days":days ,
        "reason":reason ,
        "status":"Pending",
        "applied_on":datetime .now ().strftime ("%Y-%m-%d %H:%M:%S")
        }
        self ._leaves .append (leave_request )
        self ._save ()
        return leave_id 

    def approve_leave (self ,leave_id ):
        try :
            leave_id =int (leave_id )
        except ValueError :
            return False 

        for leave in self ._leaves :
            if leave ["id"]==leave_id :
                if leave ["status"]=="Pending":
                    leave ["status"]="Approved"
                    self ._save ()
                    return True 
                return False 
        return False 

    def reject_leave (self ,leave_id ):
        try :
            leave_id =int (leave_id )
        except ValueError :
            return False 

        for leave in self ._leaves :
            if leave ["id"]==leave_id :
                if leave ["status"]=="Pending":
                    leave ["status"]="Rejected"
                    self ._save ()
                    return True 
                return False 
        return False 

    def get_pending_leaves (self ):
        return [l for l in self ._leaves if l ["status"]=="Pending"]

    def get_student_leaves (self ,student_name ):
        return [l for l in self ._leaves if l .get ("student_name","").lower ()==student_name .lower ()]

    def get_applicant_leaves (self ,applicant_name ):

        return [l for l in self ._leaves if l .get ("applicant_name",l .get ("student_name","")).lower ()==applicant_name .lower ()]

    def is_leave_approved (self ,student_name ,date_str ):

        for leave in self ._leaves :
            if leave .get ("student_name","").lower ()==student_name .lower ()and leave ["status"]=="Approved":
                try :
                    start =datetime .strptime (leave ["start_date"],"%Y-%m-%d")
                    check =datetime .strptime (date_str ,"%Y-%m-%d")

                    days_diff =(check -start ).days 
                    if 0 <=days_diff <leave ["days"]:
                        return True 
                except ValueError :
                    continue 
                except ValueError :
                    continue 
        return False 

    def get_pending_count (self ):
        return len ([l for l in self ._leaves if l ["status"]=="Pending"])
