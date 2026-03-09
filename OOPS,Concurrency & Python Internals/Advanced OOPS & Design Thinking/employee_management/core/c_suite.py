import sys 
import os 
from abc import ABC ,abstractmethod ,ABCMeta 
from typing import Dict ,Any 
sys .path .append (os .path .dirname (os .path .dirname (os .path .abspath (__file__ ))))
from core .managers import Managers 
from utils .json_handler import JSONHandler 

class SingletonMeta (ABCMeta ):
    _instances ={}

    def __call__ (cls ,*args ,**kwargs ):
        if cls not in cls ._instances :
            instance =super ().__call__ (*args ,**kwargs )
            cls ._instances [cls ]=instance 
        return cls ._instances [cls ]

class CEO (Managers ,metaclass =SingletonMeta ):

    def __init__ (self ,emp_id ,name ,username ,password ,salary =150000 ):
        if not hasattr (self ,'_initialized'):
            super ().__init__ (emp_id ,name ,username ,password ,'CEO',salary )
            self ._initialized =True 

    def can_manage_managers (self ):
        return True 

    def crud_managers (self ,action ,manager_obj =None ,**kwargs ):

        if action =='create':
            manager_obj .create ()
        elif action =='update':
            manager_obj .update (**kwargs )
        elif action =='delete':
            manager_obj .delete ()
        elif action =='read':
            return manager_obj .read ()

    def view_global_data (self ):
        print ('[CEO] Viewing Global Empire State...')

class CTO (Managers ,metaclass =SingletonMeta ):

    def __init__ (self ,emp_id ,name ,username ,password ,salary =120000 ):
        if not hasattr (self ,'_initialized'):
            super ().__init__ (emp_id ,name ,username ,password ,'CTO',salary )
            self ._initialized =True 
            self .calculate_performance_matrix ()

    def calculate_performance_matrix (self ):
        print ('\n[CTO | Algo Engine] Initializing Performance Matrix...')
        employees =JSONHandler .load ('employees.json')
        print (f'[CTO] Analyzing {len (employees )} employee records for optimization...')

    def calculate_employee_performance (self ,employee_obj ):
        from core .attendance import Attendance 
        attendance_percent =Attendance .calculate_attendance_percentage (employee_obj .id )
        score =employee_obj .tasks *10 +employee_obj .diff_sum *5 -employee_obj .leaves *2 +int (attendance_percent )
        return score 

    def check_promotion_eligibility (self ,employee_obj ):
        score =self .calculate_employee_performance (employee_obj )
        if score >150 and employee_obj .level <3 :
            print (f'[CTO] Employee {employee_obj .name } (Score {score }) eligible for promotion.')
            return True 
        return False 

    def suggest_promotion (self ,employee_obj ):
        return self .check_promotion_eligibility (employee_obj )

class COO (Managers ,metaclass =SingletonMeta ):

    def __init__ (self ,emp_id ,name ,username ,password ,salary =120000 ):
        if not hasattr (self ,'_initialized'):
            super ().__init__ (emp_id ,name ,username ,password ,'COO',salary )
            self ._initialized =True 
            self .check_incoming_vs_completion ()

    def check_incoming_vs_completion (self ):
        print ('\n[COO | Ops Monitor] Checking Project Throughput...')
        projects =JSONHandler .load ('projects.json')
        completed =sum ((1 for p in projects .values ()if p .get ('status')=='completed'))
        total =len (projects )
        if total >0 and total -completed >5 :
            print (f'[ALERT] High Incoming Rate! {total -completed } pending projects.')

    def assign_project (self ,project_id ,team_id ):
        pass 

class CFO (Managers ,metaclass =SingletonMeta ):

    def __init__ (self ,emp_id ,name ,username ,password ,salary =110000 ):
        if not hasattr (self ,'_initialized'):
            super ().__init__ (emp_id ,name ,username ,password ,'CFO',salary )
            self ._initialized =True 
            self .check_revenue_health ()

    def check_revenue_health (self ):
        print ('\n[CFO | Fiscal Watch] Analyzing Revenue Streams...')

    def manage_salary (self ,employee_obj ,increment ):
        new_salary =employee_obj .salary +increment 
        employee_obj .update (salary =new_salary )
        print (f'[CFO] Updated salary for {employee_obj .name } to {new_salary }')

    def calculate_company_revenue (self ):
        projects =JSONHandler .load ('projects.json')
        total =0 
        from datetime import datetime 
        import pytz 
        for p in projects .values ():
            if p .get ('status')=='completed':
                base_revenue =p ['difficulty']*1000 
                finish_time_str =p .get ('finish_time')
                deadline_str =p .get ('deadline')
                timezone_str =p .get ('timezone','UTC')
                if finish_time_str and deadline_str :
                    try :
                        ft =datetime .strptime (finish_time_str ,'%Y-%m-%d %H:%M:%S')
                        dl =datetime .strptime (deadline_str ,'%Y-%m-%d %H:%M:%S')
                        if ft >dl :
                            print (f'[CFO] Project {p ['project_id']} Late! Penalty applied.')
                            base_revenue *=0.8 
                    except Exception as e :
                        print (f'[CFO] Error checking lateness for {p ['project_id']}: {e }')
                total +=base_revenue 
        return total 

class HR (Managers ,metaclass =SingletonMeta ):

    def __init__ (self ,emp_id ,name ,username ,password ,salary =80000 ):
        if not hasattr (self ,'_initialized'):
            super ().__init__ (emp_id ,name ,username ,password ,'HR',salary )
            self ._initialized =True 

    def create_team_lead (self ,emp_data ,team_id ):
        from core .employees import Employees 
        tl =Employees (**emp_data )
        tl .create ()
        from core .team import Team 
        try :
            team =Team (team_id ,tl .id ,department =tl .dept ,level =tl .level )
            team .create ()
            print (f'[HR] Team {team_id } initialized with Lead {tl .name }')
        except Exception as e :
            print (f'[HR] Team Creation Failed: {e }')

    def manage_attendance (self ):
        pass 

    def manage_leave_requests (self ,request_id ,status ):
        print (f'[HR] Processing leave request {request_id } -> {status }')
        from core .leave_requests import LeaveRequests 
        requests =LeaveRequests .get_all_requests ()
        target_req =next ((r for r in requests if r .request_id ==request_id ),None )
        if not target_req :
            raise ValueError (f'Request {request_id } not found')
        target_req .update (status =status )
        if status =='Approved':
            from core .employees import Employees 
            from core .attendance import Attendance 
            emp_data =JSONHandler .load ('employees.json').get (target_req .emp_id )
            if emp_data :
                emp =Employees .from_dict (emp_data )
                emp .update (leaves =emp .leaves +1 )
        return True 
