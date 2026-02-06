from datetime import datetime ,timedelta 
import json 
import os 
import hashlib 

class NotificationManager :
    def __init__ (self ,attendance_manager ,leave_manager ):
        self .attendance_manager =attendance_manager 
        self .leave_manager =leave_manager 
        self ._notification_state_file =os .path .join (os .path .dirname (__file__ ),"..","Data","notification_state.json")
        self ._notification_state ={}
        self ._load_state ()

    def _load_state (self ):
        if os .path .exists (self ._notification_state_file ):
            try :
                with open (self ._notification_state_file ,"r")as f :
                    self ._notification_state =json .load (f )
            except Exception :
                self ._notification_state ={}
        else :
            self ._notification_state ={}

    def _save_state (self ):
        with open (self ._notification_state_file ,"w")as f :
            json .dump (self ._notification_state ,f ,indent =2 )

    def _generate_alert_id (self ,student_name ,dates ):

        data =f"{student_name }:{','.join (dates )}"
        return hashlib .md5 (data .encode ()).hexdigest ()[:8 ]

    def check_uninformed_absences (self ):

        alerts =[]
        students =self .attendance_manager .get_all_students ()

        for name ,student_obj in students .items ():
            dates =student_obj .get_all_dates ()
            if len (dates )<3 :
                continue 

            dates .sort ()

            for i in range (len (dates )-2 ):
                d1_str =dates [i ]
                d2_str =dates [i +1 ]
                d3_str =dates [i +2 ]

                s1 =student_obj ._attendance_records [d1_str ]
                s2 =student_obj ._attendance_records [d2_str ]
                s3 =student_obj ._attendance_records [d3_str ]

                if s1 =='A'and s2 =='A'and s3 =='A':
                    try :
                        date1 =datetime .strptime (d1_str ,"%Y-%m-%d")
                        date2 =datetime .strptime (d2_str ,"%Y-%m-%d")
                        date3 =datetime .strptime (d3_str ,"%Y-%m-%d")

                        if (date2 -date1 ).days ==1 and (date3 -date2 ).days ==1 :
                            is_excused =(
                            self .leave_manager .is_leave_approved (name ,d1_str )or 
                            self .leave_manager .is_leave_approved (name ,d2_str )or 
                            self .leave_manager .is_leave_approved (name ,d3_str )
                            )

                            if not is_excused :
                                alert_id =self ._generate_alert_id (name ,[d1_str ,d2_str ,d3_str ])

                                if not self ._is_alert_contacted (alert_id ):
                                    alerts .append ({
                                    "alert_id":alert_id ,
                                    "student_name":name ,
                                    "dates":[d1_str ,d2_str ,d3_str ],
                                    "message":f"ALERT: Student {name } has 3+ consecutive uninformed absences ({d1_str }, {d2_str }, {d3_str }). Please contact immediately."
                                    })
                    except ValueError :
                        continue 

        return alerts 

    def _is_alert_contacted (self ,alert_id ):

        return alert_id in self ._notification_state .get ("contacted_alerts",[])

    def mark_absence_contacted (self ,alert_id ):

        if "contacted_alerts"not in self ._notification_state :
            self ._notification_state ["contacted_alerts"]=[]

        if alert_id not in self ._notification_state ["contacted_alerts"]:
            self ._notification_state ["contacted_alerts"].append (alert_id )
            self ._save_state ()
            return True 
        return False 

    def clear_absence_alert (self ,student_name ,dates ):

        alert_id =self ._generate_alert_id (student_name ,dates )

        pass 

    def get_notification_summary (self ,role ,user_name ,query_manager ,leave_manager ):

        summary ={
        "announcements":0 ,
        "queries":0 ,
        "leaves":0 
        }

        if role =="Principal":
            summary ["queries"]=query_manager .get_pending_count (target_filter ="Principal")
            summary ["leaves"]=leave_manager .get_pending_count ()
        elif role =="Teacher":
            summary ["queries"]=query_manager .get_pending_count (target_filter =user_name )

            summary ["leaves"]=leave_manager .get_pending_count ()

        return summary 
        if alert_id in self ._notification_state .get ("contacted_alerts",[]):
            self ._notification_state ["contacted_alerts"].remove (alert_id )
            self ._save_state ()

    def mark_announcements_viewed (self ,user_id ,announcement_ids ):

        if "users"not in self ._notification_state :
            self ._notification_state ["users"]={}

        if user_id not in self ._notification_state ["users"]:
            self ._notification_state ["users"][user_id ]={"viewed_announcements":[]}

        if "viewed_announcements"not in self ._notification_state ["users"][user_id ]:
            self ._notification_state ["users"][user_id ]["viewed_announcements"]=[]

        for aid in announcement_ids :
            if aid not in self ._notification_state ["users"][user_id ]["viewed_announcements"]:
                self ._notification_state ["users"][user_id ]["viewed_announcements"].append (aid )

        self ._save_state ()

    def get_viewed_announcements (self ,user_id ):

        if "users"not in self ._notification_state :
            return []
        if user_id not in self ._notification_state ["users"]:
            return []
        return self ._notification_state ["users"][user_id ].get ("viewed_announcements",[])
