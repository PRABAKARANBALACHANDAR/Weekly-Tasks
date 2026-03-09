import sys 
import os 
import datetime 
import pytz 
import pwinput 

sys .path .append (os .path .dirname (os .path .abspath (__file__ )))

from core .employees import Employees 
from core .team import Team 
from core .project import Project 
from core .task_allocator import TaskAllocator 
from utils .json_handler import JSONHandler 

def setup_data ():
    print ('--- Interactive Setup for Reminder Data ---')
    print ('1. Create Team Lead')
    print ('2. Create Team')
    print ('3. Create & Assign Project')
    print ('0. Exit')

    while True :
        choice =input ('\nSelect Action: ')

        if choice =='1':
            print ('\n[Create Team Lead]')
            eid =input ('Employee ID: ')
            name =input ('Name: ')
            uname =input ('Username: ')
            pwd =pwinput .pwinput ('Password: ')
            dept =input ('Department: ')
            try :
                exp =int (input ('Experience (Years): '))
                tl =Employees (eid ,name ,uname ,pwd ,dept ,exp ,'TL')
                tl .create ()
            except Exception as e :
                print (f'Error: {e }')

        elif choice =='2':
            print ('\n[Create Team]')
            tid =input ('Team ID: ')
            lid =input ('Leader ID: ')
            dept =input ('Department: ')
            try :
                t =Team (tid ,lid ,department =dept )
                t .create ()
            except Exception as e :
                print (f'Error: {e }')

        elif choice =='3':
            print ('\n[Create Project]')
            pid =input ('Project ID: ')
            title =input ('Title: ')
            dept =input ('Department: ')

            print ('Deadline (UTC):')
            d_str =input ('YYYY-MM-DD HH:MM:SS: ')

            try :
                diff =int (input ('Difficulty (1-3): '))
                proj =Project (pid ,title ,dept ,d_str ,diff ,status ='pending')
                proj .create ()

                assign =input ('Assign to Team? (y/n): ').lower ()
                if assign =='y':
                    tid =input ('Team ID: ')
                    proj .assigned_team_id =tid 
                    proj .status ='in-progress'
                    proj .update ()
                    print ('Project assigned and status set to in-progress.')
            except Exception as e :
                print (f'Error: {e }')

        elif choice =='0':
            break 

if __name__ =='__main__':
    setup_data ()
