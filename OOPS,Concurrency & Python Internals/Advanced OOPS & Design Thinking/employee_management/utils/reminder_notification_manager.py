import sys 
import os 
from datetime import datetime ,timedelta 
import pytz 
import logging 

sys .path .append (os .path .dirname (os .path .dirname (os .path .abspath (__file__ ))))
from utils .json_handler import JSONHandler 

class ReminderNotificationManager :

    def __init__ (self ,notification_file ='reminder_notifications.json',log_file ='reminder_logs.log'):

        self .notification_file =notification_file 
        self .log_file =log_file 
        self ._ensure_files_exist ()
        self ._setup_logger ()

    def _ensure_files_exist (self ):

        try :
            JSONHandler .load (self .notification_file )
        except :

            JSONHandler .save (self .notification_file ,{})

    def _setup_logger (self ):

        self .logger =logging .getLogger ('ReminderNotificationManager')
        self .logger .setLevel (logging .INFO )

        if self .logger .handlers :
            return 

        log_dir ='data'
        os .makedirs (log_dir ,exist_ok =True )

        log_path =os .path .join (log_dir ,self .log_file )
        file_handler =logging .FileHandler (log_path ,encoding ='utf-8')
        file_handler .setLevel (logging .INFO )

        formatter =logging .Formatter (
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt ='%Y-%m-%d %H:%M:%S'
        )
        file_handler .setFormatter (formatter )

        self .logger .addHandler (file_handler )

    def _log_event (self ,event_type ,project_id ,team_id ,employee_id ,message ):

        log_message =f"{event_type } | Project: {project_id } | Team: {team_id } | Employee: {employee_id } | Message: {message }"
        self .logger .info (log_message )

    def check_upcoming_deadlines (self ,hours_threshold =24 ):

        projects_data =JSONHandler .load ('projects.json')
        upcoming_deadlines =[]

        for proj_id ,proj_data in projects_data .items ():

            if proj_data .get ('status')!='in-progress':
                continue 

            if not proj_data .get ('assigned_team_id'):
                continue 

            try :

                deadline_str =proj_data .get ('deadline')
                tz_str =proj_data .get ('timezone','UTC')
                tz =pytz .timezone (tz_str )

                deadline_dt =datetime .strptime (deadline_str ,'%Y-%m-%d %H:%M:%S')
                deadline_dt =tz .localize (deadline_dt )

                current_time =datetime .now (tz )

                time_remaining =deadline_dt -current_time 
                hours_remaining =time_remaining .total_seconds ()/3600 

                if 0 <hours_remaining <=hours_threshold :

                    days =time_remaining .days 
                    hours =int (time_remaining .seconds /3600 )
                    minutes =int ((time_remaining .seconds %3600 )/60 )

                    if days >0 :
                        time_str =f"{days } day(s), {hours } hour(s)"
                    elif hours >0 :
                        time_str =f"{hours } hour(s), {minutes } minute(s)"
                    else :
                        time_str =f"{minutes } minute(s)"

                    upcoming_deadlines .append ({
                    'project_id':proj_id ,
                    'title':proj_data .get ('title'),
                    'deadline':deadline_str ,
                    'team_id':proj_data .get ('assigned_team_id'),
                    'hours_remaining':hours_remaining ,
                    'time_remaining_str':time_str ,
                    'timezone':tz_str 
                    })

            except Exception as e :

                print (f"Error checking deadline for project {proj_id }: {e }")
                continue 

        return upcoming_deadlines 

    def create_reminder_notification (self ,project_id ,team_id ,hours_remaining ,time_str ):

        notifications =JSONHandler .load (self .notification_file )

        notification_id =f"REMINDER_{project_id }_{datetime .now ().strftime ('%Y%m%d_%H%M%S')}"

        notification ={
        'notification_id':notification_id ,
        'project_id':project_id ,
        'team_id':team_id ,
        'hours_remaining':hours_remaining ,
        'time_remaining_str':time_str ,
        'created_at':datetime .now ().strftime ('%Y-%m-%d %H:%M:%S'),
        'acknowledged':False ,
        'acknowledged_at':None ,
        'acknowledged_by':None ,
        'notification_count':1 ,
        'last_notified_at':datetime .now ().strftime ('%Y-%m-%d %H:%M:%S')
        }

        notifications [notification_id ]=notification 
        JSONHandler .save (self .notification_file ,notifications )

        self ._log_event (
        'NOTIFICATION_CREATED',
        project_id ,
        team_id ,
        'SYSTEM',
        f"Reminder created - Project deadline in {time_str } ({hours_remaining :.1f} hours)"
        )

        return notification_id 

    def get_pending_notifications (self ,team_id =None ,employee_id =None ):

        notifications =JSONHandler .load (self .notification_file )
        pending =[]

        for notif_id ,notif_data in notifications .items ():

            if notif_data .get ('acknowledged'):
                continue 

            if team_id and notif_data .get ('team_id')!=team_id :
                continue 

            if employee_id :
                teams_data =JSONHandler .load ('teams.json')
                team_data =teams_data .get (notif_data .get ('team_id'),{})
                if team_data .get ('team_leader_id')!=employee_id :
                    continue 

            pending .append (notif_data )

        return pending 

    def acknowledge_notification (self ,notification_id ,employee_id ):

        notifications =JSONHandler .load (self .notification_file )

        if notification_id not in notifications :
            return False 

        notif =notifications [notification_id ]
        notif ['acknowledged']=True 
        notif ['acknowledged_at']=datetime .now ().strftime ('%Y-%m-%d %H:%M:%S')
        notif ['acknowledged_by']=employee_id 

        JSONHandler .save (self .notification_file ,notifications )

        self ._log_event (
        'ACKNOWLEDGMENT_RECEIVED',
        notif ['project_id'],
        notif ['team_id'],
        employee_id ,
        f"Notification acknowledged after {notif ['notification_count']} reminder(s)"
        )

        return True 

    def increment_notification_count (self ,notification_id ):

        notifications =JSONHandler .load (self .notification_file )

        if notification_id in notifications :
            notif =notifications [notification_id ]
            notif ['notification_count']=notif .get ('notification_count',0 )+1 
            notif ['last_notified_at']=datetime .now ().strftime ('%Y-%m-%d %H:%M:%S')

            JSONHandler .save (self .notification_file ,notifications )

            self ._log_event (
            'NOTIFICATION_SHOWN',
            notif ['project_id'],
            notif ['team_id'],
            'SYSTEM',
            f"Reminder shown again (count: {notif ['notification_count']})"
            )

            return notif ['notification_count']

        return 0 

    def get_notification_summary (self ,employee_id ):

        pending =self .get_pending_notifications (employee_id =employee_id )
        return {
        'count':len (pending ),
        'notifications':pending 
        }

    def display_pending_reminders (self ,employee_id ):

        pending =self .get_pending_notifications (employee_id =employee_id )

        if not pending :
            return []

        print ("\n"+"!"*80 )
        print ("TASK DEADLINE REMINDERS - ACTION REQUIRED!")
        print ("!"*80 )

        displayed_ids =[]

        for notif in pending :
            print (f"\n>> Project: {notif ['project_id']}")
            print (f"   Time Remaining: {notif ['time_remaining_str']}")
            print (f"   Team: {notif ['team_id']}")
            print (f"   Reminder Count: {notif ['notification_count']}")
            print (f"   First Notified: {notif ['created_at']}")

            self .increment_notification_count (notif ['notification_id'])
            displayed_ids .append (notif ['notification_id'])

        print ("\n"+"!"*80 )
        print (f"Total Pending Reminders: {len (pending )}")
        print ("!"*80 +"\n")

        return displayed_ids 

    def cleanup_old_notifications (self ,days_old =30 ):

        notifications =JSONHandler .load (self .notification_file )
        cutoff_date =datetime .now ()-timedelta (days =days_old )

        to_remove =[]

        for notif_id ,notif_data in notifications .items ():

            if not notif_data .get ('acknowledged'):
                continue 

            ack_time_str =notif_data .get ('acknowledged_at')
            if ack_time_str :
                ack_time =datetime .strptime (ack_time_str ,'%Y-%m-%d %H:%M:%S')
                if ack_time <cutoff_date :
                    to_remove .append (notif_id )

        for notif_id in to_remove :
            del notifications [notif_id ]

        if to_remove :
            JSONHandler .save (self .notification_file ,notifications )

        return len (to_remove )
