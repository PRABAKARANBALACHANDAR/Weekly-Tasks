import sys 
import os 
import json 
import datetime 
import pytz 
import pwinput 
import logging 
current_dir =os .path .dirname (os .path .abspath (__file__ ))
parent_dir =os .path .dirname (current_dir )
target_path =os .path .join (parent_dir ,'Advanced OOPS & Design Thinking','employee_management')
if target_path not in sys .path :
    sys .path .append (target_path )
try :
    from core .project import Project 
    from core .task_allocator import TaskAllocator 
    from utils .json_handler import JSONHandler 
except ImportError as e :
    print (f'CRITICAL ERROR: Could not import core modules. Check path:\n{target_path }')
    print (f'Details: {e }')
    sys .exit (1 )
IST =pytz .timezone ('Asia/Kolkata')
HISTORY_FILE =os .path .join (current_dir ,'history_logs.json')
TL_LOG_FILE =os .path .join (current_dir ,'tl_narrative_logs.log')

def ist_converter (*args ):
    return datetime .datetime .now (IST ).timetuple ()

logger =logging .getLogger ('TL_Narrative')
logger .setLevel (logging .INFO )
if not logger .handlers :
    file_handler =logging .FileHandler (TL_LOG_FILE )
    formatter =logging .Formatter ('[%(asctime)s] [TL: %(tl_id)s] %(message)s',datefmt ='%Y-%m-%d %H:%M:%S')
    formatter .converter =ist_converter 
    file_handler .setFormatter (formatter )
    logger .addHandler (file_handler )

os .chdir (target_path )

class History :

    @staticmethod 
    def archive_project (project_obj ):
        history ={}
        if os .path .exists (HISTORY_FILE ):
            with open (HISTORY_FILE ,'r')as f :
                try :
                    history =json .load (f )
                except :
                    history ={}
        start_str =project_obj .allocation_time 
        end_str =project_obj .finish_time 
        duration_hours =0.0 
        if start_str and end_str :
            try :
                fmt ='%Y-%m-%d %H:%M:%S'
                t_start =pytz .utc .localize (datetime .datetime .strptime (start_str ,fmt ))
                t_end =pytz .utc .localize (datetime .datetime .strptime (end_str ,fmt ))
                t_start_ist =t_start .astimezone (IST )
                t_end_ist =t_end .astimezone (IST )
                delta =t_end -t_start 
                duration_hours =delta .total_seconds ()/3600.0 
            except Exception as e :
                print (f'[History] Error calculating duration: {e }')
        record =project_obj .to_dict ()
        record ['archived_at_ist']=datetime .datetime .now (IST ).strftime ('%Y-%m-%d %H:%M:%S')
        record ['duration_hours']=round (duration_hours ,2 )
        history [project_obj .project_id ]=record 
        with open (HISTORY_FILE ,'w')as f :
            json .dump (history ,f ,indent =4 )
        print (f'[History] Archived Project {project_obj .project_id } (Duration: {duration_hours :.2f} hrs)')

class Reminder :

    def __init__ (self ,user_role ,user_id ,team_id =None ):
        self ._user_role =user_role 
        self ._user_id =user_id 
        self ._team_id =team_id 
        self ._now_ist =datetime .datetime .now (IST )
        print (f'\n[Reminder System] Initialized at {self ._now_ist .strftime ('%Y-%m-%d %H:%M:%S %Z')}')
        self .check_alerts ()

    def check_alerts (self ):
        projects =JSONHandler .load ('projects.json')
        for pid ,p_data in projects .items ():
            proj =Project .from_dict (p_data )
            if proj .status in ['pending','in-progress']:
                try :
                    tz_str =proj .timezone if proj .timezone else 'UTC'
                    pz =pytz .timezone (tz_str )
                    deadline_dt =pz .localize (datetime .datetime .strptime (proj .deadline ,'%Y-%m-%d %H:%M:%S'))
                    deadline_ist =deadline_dt .astimezone (IST )
                    time_left =deadline_ist -self ._now_ist 
                    hours_left =time_left .total_seconds ()/3600 
                    if 0 <hours_left <24 :
                        print (f'  [ALERT] ⏳ Project {proj .title } ({pid }) is due in {hours_left :.1f} hours!')
                    elif hours_left <0 :
                        print (f'  [CRITICAL] 🚨 Project {proj .title } ({pid }) is OVERDUE by {abs (hours_left ):.1f} hours!')
                except Exception as e :
                    pass 
            if self ._team_id and proj .assigned_team_id ==self ._team_id :
                if proj .status =='pending':
                    print (f'  [NEW] 📥 New Project Assigned: {proj .title } (ID: {proj .project_id })')
                elif proj .status =='in-progress':
                    print (f"  [STATUS] '{proj .title }' is In Progress.")
        for pid ,p_data in projects .items ():
            if p_data .get ('status')=='completed':
                History .archive_project (Project .from_dict (p_data ))

def tl_narrative_log (tl_id ,message ):
    logger .info (message ,extra ={'tl_id':tl_id })
    print ('Narrative Log Saved.')

def main ():
    print ('--- Distributed Project Management Subsystem ---')
    print ('1. Login (Trigger Reminders)')
    print ('2. Exit')
    choice =input ('Select: ')
    if choice =='1':
        user_id =input ('User ID: ')
        password =pwinput .pwinput ('Password: ')
        managers =JSONHandler .load ('managers.json')
        employees =JSONHandler .load ('employees.json')
        user =None 
        role =None 
        team_id =None 
        if user_id in managers and managers [user_id ]['password']==password :
            user =managers [user_id ]
            role =user .get ('role','MANAGER')
        elif user_id in employees and employees [user_id ]['password']==password :
            user =employees [user_id ]
            role =user .get ('role','EMPLOYEE')
            teams =JSONHandler .load ('teams.json')
            for tid ,tdata in teams .items ():
                if user_id in tdata .get ('members',[])or tdata .get ('team_leader_id')==user_id :
                    team_id =tid 
                    break 
        if user :
            print (f'Welcome, {user ['name']}!')
            Reminder (role ,user_id ,team_id )
            if role =='TL':
                print ('\n[TL Options]')
                print ('1. Add Narrative Log')
                print ('2. Logout')
                tl_choice =input ('Action: ')
                if tl_choice =='1':
                    msg =input ('Log Message: ')
                    tl_narrative_log (user_id ,msg )
        else :
            print ('Invalid Credentials.')
if __name__ =='__main__':
    main ()
