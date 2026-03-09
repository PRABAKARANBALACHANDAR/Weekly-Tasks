import sys 
import os 
from datetime import datetime 
import pytz 
sys .path .append (os .path .dirname (os .path .dirname (os .path .abspath (__file__ ))))
from core .data_base import Data 
from utils .json_handler import JSONHandler 
from utils .validators import Validators 

class Project (Data ):

    def __init__ (self ,project_id ,title ,department ,deadline ,difficulty ,status ='pending',timezone ='UTC',added_time =None ,allocation_time =None ,finish_time =None ,progress_logs =None ):
        Validators .validate_difficulty (difficulty )
        Validators .validate_project_status (status )
        self ._project_id =project_id 
        self ._title =title 
        self ._department =department 
        self ._deadline =deadline 
        self ._difficulty =difficulty 
        self ._status =status .lower ()
        self ._assigned_team_id =None 
        self ._timezone =timezone 
        self ._added_time =added_time if added_time else datetime .now (pytz .utc ).strftime ('%Y-%m-%d %H:%M:%S')
        self ._allocation_time =allocation_time 
        self ._finish_time =finish_time 
        self ._progress_logs =progress_logs if progress_logs else []

    @property 
    def id (self ):
        return self ._project_id 

    @property 
    def name (self ):
        return self ._title 

    @property 
    def project_id (self ):
        return self ._project_id 

    @property 
    def title (self ):
        return self ._title 

    @property 
    def department (self ):
        return self ._department 

    @property 
    def deadline (self ):
        return self ._deadline 

    @property 
    def timezone (self ):
        return self ._timezone 

    @property 
    def difficulty (self ):
        return self ._difficulty 

    @property 
    def status (self ):
        return self ._status 

    @property 
    def assigned_team_id (self ):
        return self ._assigned_team_id 

    @property 
    def added_time (self ):
        return self ._added_time 

    @property 
    def allocation_time (self ):
        return self ._allocation_time 

    @property 
    def finish_time (self ):
        return self ._finish_time 

    @property 
    def progress_logs (self ):
        return self ._progress_logs 

    @status .setter 
    def status (self ,value ):
        Validators .validate_project_status (value )
        self ._status =value .lower ()
        if self ._status =='completed'and (not self ._finish_time ):
            self ._finish_time =datetime .now (pytz .utc ).strftime ('%Y-%m-%d %H:%M:%S')

    @assigned_team_id .setter 
    def assigned_team_id (self ,value ):
        self ._assigned_team_id =value 
        if value and (not self ._allocation_time ):
            self ._allocation_time =datetime .now (pytz .utc ).strftime ('%Y-%m-%d %H:%M:%S')

    def add_log (self ,status ,note ,author ):
        log_entry ={'timestamp':datetime .now (pytz .utc ).strftime ('%Y-%m-%d %H:%M:%S'),'status':status ,'note':note ,'author':author }
        self ._progress_logs .append (log_entry )
        if status in ['pending','in-progress','completed']:
            self .status =status 

    def check_reminder (self ):
        try :
            tz =pytz .timezone (self ._timezone )
            current_time =datetime .now (tz )
            deadline_dt =datetime .strptime (self ._deadline ,'%Y-%m-%d %H:%M:%S')
            deadline_dt =tz .localize (deadline_dt )
            time_remaining =deadline_dt -current_time 
            return (time_remaining ,current_time )
        except Exception as e :
            return (f'Error checking reminder: {e }',None )

    def to_dict (self ):
        return {'project_id':self ._project_id ,'title':self ._title ,'department':self ._department ,'deadline':self ._deadline ,'difficulty':self ._difficulty ,'status':self ._status ,'assigned_team_id':self ._assigned_team_id ,'timezone':self ._timezone ,'added_time':self ._added_time ,'allocation_time':self ._allocation_time ,'finish_time':self ._finish_time ,'progress_logs':self ._progress_logs }

    @classmethod 
    def from_dict (cls ,data ):
        proj =cls (data ['project_id'],data ['title'],data ['department'],data ['deadline'],data ['difficulty'],data .get ('status','pending'),data .get ('timezone','UTC'),data .get ('added_time'),data .get ('allocation_time'),data .get ('finish_time'),data .get ('progress_logs'))
        proj ._assigned_team_id =data .get ('assigned_team_id')
        return proj 

    @classmethod 
    def get_next_id (cls ):
        projects =JSONHandler .load ('projects.json')
        if not projects :
            return 'P001'
        ids =[int (pid [1 :])for pid in projects .keys ()if pid .startswith ('P')and pid [1 :].isdigit ()]
        if not ids :
            return 'P001'
        return f'P{max (ids )+1 :03d}'

    def create (self ):
        projects =JSONHandler .load ('projects.json')
        if self ._project_id in projects :
            raise ValueError (f"Project ID '{self ._project_id }' already exists")
        projects [self ._project_id ]=self .to_dict ()
        JSONHandler .save ('projects.json',projects )

    def read (self ):
        projects =JSONHandler .load ('projects.json')
        if self ._project_id in projects :
            return Project .from_dict (projects [self ._project_id ])
        return None 

    def update (self ,**kwargs ):
        projects =JSONHandler .load ('projects.json')
        if self ._project_id not in projects :
            raise ValueError (f'Project {self ._project_id } not found')
        if 'status'in kwargs :
            self .status =kwargs ['status']
        if 'assigned_team_id'in kwargs :
            self .assigned_team_id =kwargs ['assigned_team_id']
        projects [self ._project_id ]=self .to_dict ()
        JSONHandler .save ('projects.json',projects )

    def delete (self ):
        projects =JSONHandler .load ('projects.json')
        if self ._project_id in projects :
            del projects [self ._project_id ]
            JSONHandler .save ('projects.json',projects )
        else :
            raise ValueError (f'Project {self ._project_id } not found')

    def __str__ (self ):
        team_info =f', Team: {self ._assigned_team_id }'if self ._assigned_team_id else ''
        return f"Project '{self ._title }' [{self ._status }] - Deadline: {self ._deadline } ({self ._timezone }){team_info }"
