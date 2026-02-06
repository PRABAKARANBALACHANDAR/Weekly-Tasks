import os 
import sys 
import pwinput 
sys .path .append (os .path .dirname (os .path .abspath (__file__ )))
from core .admin import Admin 
from core .managers import Managers 
from core .employees import Employees 
from core .c_suite import CEO ,CTO ,COO ,CFO ,HR 
from utils .json_handler import JSONHandler 
from core .leave_requests import LeaveRequests 
from core .team import Team 
from core .attendance import Attendance 
from core .project import Project 

class EmployeeManagementSystem :

    def __init__ (self ):
        self .initialize_system ()

    def initialize_system (self ):
        managers_data =JSONHandler .load ('managers.json')
        admin_exists =any ((mgr .get ('role')=='ADMIN'for mgr in managers_data .values ()))
        if not admin_exists :
            print ('Initializing system with default Admin...')
            admin =Admin ('admin01','System Administrator','admin','admin123')
            try :
                admin .create ()
                print ('System initialized successfully.')
                print ("Default Credentials - Username: 'admin', Password: 'admin123'")
            except Exception as e :
                print (f'Error initializing system: {e }')

    def get_logged_in_user (self ,username ,password ):
        managers_data =JSONHandler .load ('managers.json')
        if managers_data :
            for m_id ,m in managers_data .items ():
                if m ['username']==username and m ['password']==password :
                    role =m ['role'].upper ()
                    if role =='CEO':
                        return CEO (m ['id'],m ['name'],m ['username'],m ['password'],m ['salary'])
                    elif role =='CTO':
                        return CTO (m ['id'],m ['name'],m ['username'],m ['password'],m ['salary'])
                    elif role =='COO':
                        return COO (m ['id'],m ['name'],m ['username'],m ['password'],m ['salary'])
                    elif role =='CFO':
                        return CFO (m ['id'],m ['name'],m ['username'],m ['password'],m ['salary'])
                    elif role =='HR':
                        return HR (m ['id'],m ['name'],m ['username'],m ['password'],m ['salary'])
                    elif role =='ADMIN':
                        return Admin (m ['id'],m ['name'],m ['username'],m ['password'],m ['salary'])
                    else :
                        return Managers (m ['id'],m ['name'],m ['username'],m ['password'],role ,m ['salary'])
        employees_data =JSONHandler .load ('employees.json')
        if employees_data :
            for e_id ,e in employees_data .items ():
                if e ['username']==username and e ['password']==password :
                    return Employees .from_dict (e )
        return None 

    def manage_managers_menu (self ,admin_user ):
        while True :
            print ('\n--- User Management (Admin Only) ---')
            print ('1. Create User (Manager/C-Suite)')
            print ('2. Read User')
            print ('3. Update User')
            print ('4. Delete User')
            print ('5. List All Managers')
            print ('0. Back')
            choice =input ('Enter choice: ')
            try :
                if choice =='1':
                    auto_id =Managers .get_next_manager_id ()
                    print (f'Auto-generated ID: {auto_id }')
                    custom_id =input (f'Press Enter to use {auto_id } or enter custom ID: ').strip ()
                    e_id =custom_id if custom_id else auto_id 

                    name =input ('Enter Name: ')
                    uname =input ('Enter Username: ')
                    pwd =input ('Enter Password: ')
                    role =input ('Enter Role (CEO, CTO, COO, CFO, HR, MANAGER): ').upper ()
                    if role =='CEO':
                        mgr =CEO (e_id ,name ,uname ,pwd )
                    elif role =='CTO':
                        mgr =CTO (e_id ,name ,uname ,pwd )
                    elif role =='COO':
                        mgr =COO (e_id ,name ,uname ,pwd )
                    elif role =='CFO':
                        mgr =CFO (e_id ,name ,uname ,pwd )
                    elif role =='HR':
                        mgr =HR (e_id ,name ,uname ,pwd )
                    else :
                        mgr =Managers (e_id ,name ,uname ,pwd ,role )
                    admin_user .crud_managers ('create',manager_obj =mgr )
                    print (f'{role } created successfully with ID: {e_id }')
                elif choice =='2':
                    e_id =input ('Enter ID to read: ')
                    dummy_mgr =Managers (e_id ,'','','','HR')
                    data =admin_user .crud_managers ('read',manager_obj =dummy_mgr )
                    if data :
                        print (f'Details: {data }')
                    else :
                        print ('not found.')
                elif choice =='3':
                    e_id =input ('Enter ID to update: ')
                    dummy_mgr =Managers (e_id ,'','','','HR')
                    print ('Leave fields blank to skip update')
                    name =input ('New Name: ')
                    pwd =input ('New Password: ')
                    salary_str =input ('New Salary: ')
                    updates ={}
                    if name :
                        updates ['name']=name 
                    if pwd :
                        updates ['password']=pwd 
                    if salary_str :
                        updates ['salary']=float (salary_str )
                    admin_user .crud_managers ('update',manager_obj =dummy_mgr ,**updates )
                    print ('Updated successfully.')
                elif choice =='4':
                    e_id =input ('Enter ID to delete: ')
                    dummy_mgr =Managers (e_id ,'','','','HR')
                    admin_user .crud_managers ('delete',manager_obj =dummy_mgr )
                    print ('Deleted successfully.')
                elif choice =='5':
                    data =JSONHandler .load ('managers.json')
                    if not data :
                        print ('No managers found in the system.')
                    else :
                        for m in data .values ():
                            print (f'ID: {m ['id']}, Name: {m ['name']}, Role: {m ['role']}')
                elif choice =='0':
                    break 
            except Exception as e :
                print (f'Error: {e }')

    def run (self ):
        print ('Welcome to Employee Management System')
        while True :
            print ('\n1. Login')
            print ('2. Exit')
            choice =input ('Enter choice: ')
            if choice =='2':
                break 
            elif choice =='1':
                print ('\n--- Login ---')
                username =input ('Username: ')
                password =pwinput .pwinput (prompt ='Password: ')
                user =self .get_logged_in_user (username ,password )
                if user :
                    print (f'Login Successful! Role: {user .role }')
                    if isinstance (user ,Employees ):
                        self .employee_portal (user )
                    else :
                        self .manager_portal (user )
                else :
                    print ('Invalid credentials.')

    def manage_employees_menu (self ,manager_user ):
        while True :
            print ('\n--- Manage Employees ---')
            print ('1. Create Employee')
            print ('2. Read Employee')
            print ('3. Update Employee')
            print ('4. Delete Employee')
            print ('5. List All Employees')
            print ('0. Back')
            choice =input ('Enter choice: ')
            try :
                if choice =='1':
                    if not manager_user .can_manage_employees ()and manager_user .role !='CEO':
                        print ('Permission Denied (HR/CEO Only)')
                        continue 

                    auto_id =Employees .get_next_employee_id ()
                    print (f'Auto-generated ID: {auto_id }')
                    custom_id =input (f'Press Enter to use {auto_id } or enter custom ID: ').strip ()
                    e_id =custom_id if custom_id else auto_id 

                    name =input ('Enter Name: ')
                    uname =input ('Enter Username: ')
                    pwd =input ('Enter Password: ')
                    dept =input ('Enter Dept: ')
                    exp =input ('Enter Experience (years): ')
                    emp =Employees (e_id ,name ,uname ,pwd ,dept ,exp )
                    emp .create ()
                    print (f'Employee created successfully with ID: {e_id }')
                elif choice =='2':
                    e_id =input ('Enter ID to read: ')
                    dummy_emp =Employees (e_id ,'','','','',1 )
                    data =dummy_emp .read ()
                    if data :
                        print (f'Employee Details: {data }')
                    else :
                        print ('Employee not found.')
                elif choice =='3':
                    e_id =input ('Enter ID to update: ')
                    dummy_emp =Employees (e_id ,'','','','',1 )
                    print ('Leave fields blank to skip')
                    name =input ('New Name: ')
                    level_str =input ('New Level: ')
                    salary_str =input ('New Salary: ')
                    updates ={}
                    if name :
                        updates ['name']=name 
                    if level_str :
                        updates ['level']=int (level_str )
                    if salary_str and manager_user .can_manage_finances ():
                        updates ['salary']=float (salary_str )
                    elif salary_str :
                        print ('Warning: Only CFO/CEO can update salary directly per logic(implied).')
                    dummy_emp .update (**updates )
                    print ('Employee updated.')
                elif choice =='4':
                    e_id =input ('Enter ID to delete: ')
                    dummy_emp =Employees (e_id ,'','','','',1 )
                    dummy_emp .delete ()
                    print ('Employee deleted.')
                elif choice =='5':
                    data =JSONHandler .load ('employees.json')
                    if not data :
                        print ('No employees found in the system.')
                    else :
                        for e in data .values ():
                            print (f'ID: {e ['id']}, Name: {e ['name']}, Dept: {e ['dept']}')
                elif choice =='0':
                    break 
            except Exception as e :
                print (f'Error: {e }')

    def manage_teams_menu (self ):
        while True :
            print ('\n--- Manage Teams ---')
            print ('1. Create Team (with new Team Lead)')
            print ('2. Create Team (with existing employee as Lead)')
            print ('3. Add Member to Team')
            print ('4. View Teams')
            print ('0. Back')
            choice =input ('Enter choice: ')
            try :
                if choice =='1':

                    auto_team_id =Team .get_next_team_id ()
                    print (f'Auto-generated Team ID: {auto_team_id }')
                    custom_team_id =input (f'Press Enter to use {auto_team_id } or enter custom ID: ').strip ()
                    t_id =custom_team_id if custom_team_id else auto_team_id 

                    print ('\n--- Create Team Lead Employee ---')
                    auto_emp_id =Employees .get_next_employee_id ()
                    print (f'Auto-generated Employee ID: {auto_emp_id }')
                    custom_emp_id =input (f'Press Enter to use {auto_emp_id } or enter custom ID: ').strip ()
                    leader_id =custom_emp_id if custom_emp_id else auto_emp_id 

                    name =input ('Team Lead Name: ')
                    username =input ('Team Lead Username: ')
                    password =input ('Team Lead Password: ')
                    dept =input ('Department: ')
                    exp =input ('Team Lead Experience (years): ')

                    tl_emp =Employees (leader_id ,name ,username ,password ,dept ,exp ,role ='TL')
                    tl_emp .create ()
                    print (f'Team Lead {name } created with ID: {leader_id }')

                    level =tl_emp .level 

                    t =Team (t_id ,leader_id ,department =dept ,level =level )
                    t .create ()

                elif choice =='2':

                    auto_team_id =Team .get_next_team_id ()
                    print (f'Auto-generated Team ID: {auto_team_id }')
                    custom_team_id =input (f'Press Enter to use {auto_team_id } or enter custom ID: ').strip ()
                    t_id =custom_team_id if custom_team_id else auto_team_id 

                    leader_id =input ('Existing Employee ID (to be Team Lead): ')
                    dept =input ('Department: ')
                    level =int (input ('Team Level (1-3): '))

                    t =Team (t_id ,leader_id ,department =dept ,level =level )
                    t .create ()

                elif choice =='3':
                    t_id =input ('Team ID: ')
                    emp_id =input ('Employee ID: ')
                    teams =JSONHandler .load ('teams.json')
                    if t_id in teams :
                        t =Team .from_dict (teams [t_id ])
                        t .add_member (emp_id )
                        t .update ()
                        print ('Member added.')
                    else :
                        print ('Team not found.')
                elif choice =='4':
                    teams =JSONHandler .load ('teams.json')
                    if not teams :
                        print ('No teams found in the system.')
                    else :
                        for t in teams .values ():
                            print (f'ID: {t ['team_id']}, Leader: {t ['team_leader_id']}, Members: {len (t .get ('members',[]))}')
                elif choice =='0':
                    break 
            except Exception as e :
                print (f'Error: {e }')

    def manage_projects_menu (self ):
        while True :
            print ('\n--- Manage Projects ---')
            print ('1. Create Project')
            print ('2. View All Projects')
            print ('3. Check Project Reminders')
            print ('0. Back')
            choice =input ('Enter choice: ')
            try :
                if choice =='1':
                    p_id =Project .get_next_id ()
                    print (f'Auto-generated Project ID: {p_id }')
                    custom_id =input (f'Press Enter to use {p_id } or enter custom ID: ').strip ()
                    p_id =custom_id if custom_id else p_id 

                    title =input ('Title: ')
                    dept =input ('Department: ')
                    deadline =input ('Deadline (YYYY-MM-DD HH:MM:SS): ')
                    difficulty =int (input ('Difficulty (1-3): '))
                    timezone =input ('Timezone (e.g., UTC, Asia/Kolkata): ')
                    proj =Project (p_id ,title ,dept ,deadline ,difficulty ,timezone =timezone )
                    proj .create ()
                    print (f'Project {p_id } created successfully.')
                elif choice =='2':
                    projects =JSONHandler .load ('projects.json')
                    if not projects :
                        print ('No projects found.')
                    else :
                        for p in projects .values ():
                            print (f'{p ['project_id']}: {p ['title']} (Due: {p ['deadline']} {p .get ('timezone','')})')
                elif choice =='3':
                    projects =JSONHandler .load ('projects.json')
                    if not projects :
                        print ('No projects found.')
                    else :
                        for p_data in projects .values ():
                            proj =Project .from_dict (p_data )
                            rem ,curr =proj .check_reminder ()
                            print (f'Project {proj .project_id }: Time Remaining: {rem } (Current Time in {proj .timezone }: {curr })')
                elif choice =='0':
                    break 
            except Exception as e :
                print (f'Error: {e }')

    def manage_attendance_menu (self ):
        while True :
            print ('\n--- Attendance Management ---')
            print ('1. View All Attendance')
            print ('2. View Employee Attendance')
            print ('3. Calculate Attendance Percentage')
            print ('0. Back')
            choice =input ('Enter choice: ')
            if choice =='1':
                data =JSONHandler .load ('attendance.json')
                if not data :
                    print ('No attendance records found.')
                else :
                    for k ,v in data .items ():
                        print (f'{v ['date']} - {v ['employee_id']}: {v ['status']}')
            elif choice =='2':
                e_id =input ('Employee ID: ')
                recs =Attendance .get_employee_attendance (e_id )
                if not recs :
                    print (f'No attendance records found for employee {e_id }.')
                else :
                    for r in recs :
                        print (f'{r .date }: {r .status }')
            elif choice =='3':
                e_id =input ('Employee ID: ')
                pct =Attendance .calculate_attendance_percentage (e_id )
                print (f'Attendance Percentage: {pct :.2f}%')
            elif choice =='0':
                break 

    def view_employees_menu (self ):
        data =JSONHandler .load ('employees.json')
        if not data :
            print ('No employees found in the system.')
            return 

        emps =[Employees .from_dict (e )for e in data .values ()]
        while True :
            print ('\n--- View Employees ---')
            print ('1. View All')
            print ('2. Group by Team')
            print ('3. By Performance (Descending)')
            print ('0. Back')
            choice =input ('Enter choice: ')
            if choice =='1':
                if not emps :
                    print ('No employees to display.')
                else :
                    for e in emps :
                        print (e )
            elif choice =='2':
                teams =JSONHandler .load ('teams.json')
                if not teams :
                    print ('No teams found in the system.')
                else :
                    for t_data in teams .values ():
                        print (f'\nTeam {t_data ['team_id']} (Leader: {t_data ['team_leader_id']})')
                        for m_id in t_data .get ('members',[]):
                            e_data =data .get (m_id )
                            if e_data :
                                print (f'  - {e_data ['name']} ({e_data ['role']})')
            elif choice =='3':
                if not emps :
                    print ('No employees to display.')
                else :
                    sorted_emps =sorted (emps ,key =lambda x :x .diff_sum ,reverse =True )
                    for e in sorted_emps :
                        print (f'{e .name }: Score {e .diff_sum }')
            elif choice =='0':
                break 

    def employee_portal (self ,employee_user ):
        try :
            while True :
                print (f'\n--- Employee Portal: {employee_user .name } ---')
                menu_options =['View Profile','Request Leave','View My Leave Requests']

                if employee_user .role =='TL':
                    menu_options .append ('Update Project Log (Team Lead)')

                menu_options .append ('Logout')

                for i ,option in enumerate (menu_options ,1 ):
                    print (f'{i }. {option }')

                choice =input ('Enter choice: ')

                if choice =='1':
                    print (f'ID: {employee_user .id }')
                    print (f'Name: {employee_user .name }')
                    print (f'Role: {employee_user .role }')
                    print (f'Dept: {employee_user .dept }')
                    print (f'Level: {employee_user .level }')
                    print (f'Salary: {employee_user .salary }')
                    print (f'Leaves: {employee_user .leaves }')
                    print (f'Tasks: {employee_user .tasks }')
                    print (f'Performance Score (Diff Sum): {employee_user .diff_sum }')
                elif choice =='2':
                    date_str =input ('Enter Date (YYYY-MM-DD): ')
                    reason =input ('Enter Reason: ')
                    req =LeaveRequests (employee_user .id ,date_str ,reason )
                    req .create ()
                    print ('Leave Request Submitted.')
                elif choice =='3':
                    requests =LeaveRequests .get_all_requests ()
                    my_requests =[r for r in requests if r .emp_id ==employee_user .id ]
                    if my_requests :
                        for r in my_requests :
                            print (f'Date: {r .date }, Status: {r .status }, Reason: {r .reason }')
                    else :
                        print ('No leave requests found.')
                elif choice =='4'and employee_user .role =='TL':
                    p_id =input ('Enter Project ID: ')
                    status =input ('New Status (in-progress/completed/failed): ')
                    note =input ('Progress Log Note: ')
                    try :
                        employee_user .update_project_log (p_id ,status ,note )
                    except Exception as e :
                        print (f'Update Failed: {e }')
                elif (choice =='4'and employee_user .role !='TL')or choice =='5':

                    break 
                else :
                    print ('Invalid choice.')
        except KeyboardInterrupt :
            print ('\n\nLogging out...')

    def manager_portal (self ,manager_user ):
        try :
            while True :

                menu_options =[]
                menu_map ={}

                menu_options .append ('View My Profile')
                menu_map ['1']='profile'

                counter =2 

                if manager_user .can_manage_managers ():
                    menu_options .append ('Manage Managers (CEO)')
                    menu_map [str (counter )]='manage_managers'
                    counter +=1 

                if manager_user .can_manage_employees ():
                    menu_options .append ('Manage Employees (HR)')
                    menu_map [str (counter )]='manage_employees'
                    counter +=1 

                if manager_user .can_calculate_performance ()or manager_user .role =='CEO':
                    menu_options .append ('Calculate Employee Performance (COO)')
                    menu_map [str (counter )]='calc_performance'
                    counter +=1 

                    menu_options .append ('Suggest Promotion (COO)')
                    menu_map [str (counter )]='suggest_promotion'
                    counter +=1 

                if manager_user .can_manage_finances ()or manager_user .role =='CEO':
                    menu_options .append ('Manage Finances/Salary (CFO)')
                    menu_map [str (counter )]='manage_salary'
                    counter +=1 

                    menu_options .append ('Calculate Company Revenue (CFO)')
                    menu_map [str (counter )]='calc_revenue'
                    counter +=1 

                if manager_user .can_manage_attendance ()or manager_user .role in ['CEO','CTO','COO','CFO']:
                    menu_options .append ('Manage Leave Requests (View: All, Action: HR Only)')
                    menu_map [str (counter )]='leave_requests'
                    counter +=1 

                if manager_user .role in ['CEO','CTO','COO']:
                    menu_options .append ('Manage Teams')
                    menu_map [str (counter )]='manage_teams'
                    counter +=1 

                if manager_user .can_manage_attendance ():
                    menu_options .append ('Manage Attendance (HR)')
                    menu_map [str (counter )]='manage_attendance'
                    counter +=1 

                menu_options .append ('View All Employees (Team/Performance)')
                menu_map [str (counter )]='view_employees'
                counter +=1 

                if manager_user .can_manage_projects ():
                    menu_options .append ('Manage Projects')
                    menu_map [str (counter )]='manage_projects'
                    counter +=1 

                if manager_user .role =='ADMIN':
                    menu_options .append ('Navigate to User Portal')
                    menu_map [str (counter )]='navigate_user'
                    counter +=1 
                elif manager_user .role =='CEO':
                    menu_options .append ('Navigate to C-Suite/HR Portal')
                    menu_map [str (counter )]='navigate_csuite'
                    counter +=1 

                menu_options .append ('Logout')
                menu_map [str (counter )]='logout'

                print (f'\n--- Manager Portal: {manager_user .name } ({manager_user .role }) ---')
                for i ,option in enumerate (menu_options ,1 ):
                    print (f'{i }. {option }')

                choice =input ('Enter choice: ')

                try :
                    action =menu_map .get (choice )

                    if action =='logout':
                        break 
                    elif action =='profile':
                        print (manager_user .to_dict ())
                    elif action =='manage_managers':
                        self .manage_managers_menu (manager_user )
                    elif action =='manage_employees':
                        self .manage_employees_menu (manager_user )
                    elif action =='calc_performance':
                        emp_id =input ('Enter Employee ID: ')
                        data =JSONHandler .load ('employees.json').get (emp_id )
                        if data :
                            emp =Employees .from_dict (data )
                            score =manager_user .calculate_employee_performance (emp )
                            print (f'Performance Score: {score }')
                        else :
                            print ('Employee not found.')
                    elif action =='suggest_promotion':
                        emp_id =input ('Enter Employee ID: ')
                        data =JSONHandler .load ('employees.json').get (emp_id )
                        if data :
                            emp =Employees .from_dict (data )
                            promote =manager_user .suggest_promotion (emp )
                            print (f'Promotion Suggested: {('Yes'if promote else 'No')}')
                        else :
                            print ('Employee not found.')
                    elif action =='manage_salary':
                        emp_id =input ('Enter Employee ID: ')
                        increment =float (input ('Enter Salary Increment Amount: '))
                        data =JSONHandler .load ('employees.json').get (emp_id )
                        if data :
                            emp =Employees .from_dict (data )
                            manager_user .manage_salary (emp ,increment )
                            print ('Salary updated.')
                        else :
                            print ('Employee not found.')
                    elif action =='calc_revenue':
                        revenue =manager_user .calculate_company_revenue ()
                        print (f'Total Company Revenue: {revenue }')
                    elif action =='leave_requests':
                        print ('\n--- Pending Leave Requests ---')
                        requests =LeaveRequests .get_all_requests ()
                        pending_reqs =[r for r in requests if r .status =='Pending']
                        if not pending_reqs :
                            print ('No pending requests.')
                        else :
                            for r in pending_reqs :
                                print (f'ID: {r .request_id }, EmpID: {r .emp_id }, Date: {r .date }, Reason: {r .reason }')
                            if manager_user .can_manage_attendance ():
                                req_id =input ('Enter Request ID to action (or leave blank to cancel): ')
                                if req_id :
                                    action_input =input ('Approve or Reject? (a/r): ').lower ()
                                    status ='Approved'if action_input =='a'else 'Rejected'if action_input =='r'else None 
                                    if status :
                                        manager_user .manage_leave_requests (req_id ,status )
                                        print (f'Request {status }.')
                                    else :
                                        print ('Invalid action.')
                            else :
                                print ('\n[INFO] Only HR can approve/reject requests.')
                    elif action =='manage_teams':
                        self .manage_teams_menu ()
                    elif action =='manage_attendance':
                        self .manage_attendance_menu ()
                    elif action =='view_employees':
                        self .view_employees_menu ()
                    elif action =='manage_projects':
                        self .manage_projects_menu ()
                    elif action =='navigate_user':

                        print ('\n--- Navigate to User Portal ---')
                        username =input ('Enter username to navigate to: ')
                        password =input ('Enter their password: ')
                        target_user =self .get_logged_in_user (username ,password )
                        if target_user :
                            print (f'Navigating to {target_user .name }\'s portal...')
                            if isinstance (target_user ,Employees ):
                                self .employee_portal (target_user )
                            else :
                                self .manager_portal (target_user )
                        else :
                            print ('User not found or invalid credentials.')
                    elif action =='navigate_csuite':

                        print ('\n--- Navigate to C-Suite/HR Portal ---')
                        print ('1. CTO')
                        print ('2. COO')
                        print ('3. CFO')
                        print ('4. HR')
                        print ('0. Cancel')
                        nav_choice =input ('Select portal: ')

                        target_user =None 
                        if nav_choice =='1':
                            username =input ('CTO Username: ')
                            password =input ('CTO Password: ')
                        elif nav_choice =='2':
                            username =input ('COO Username: ')
                            password =input ('COO Password: ')
                        elif nav_choice =='3':
                            username =input ('CFO Username: ')
                            password =input ('CFO Password: ')
                        elif nav_choice =='4':
                            username =input ('HR Username: ')
                            password =input ('HR Password: ')
                        elif nav_choice =='0':
                            continue 
                        else :
                            print ('Invalid choice.')
                            continue 

                        if nav_choice in ['1','2','3','4']:
                            target_user =self .get_logged_in_user (username ,password )
                            if target_user :
                                print (f'Navigating to {target_user .name }\'s portal...')
                                self .manager_portal (target_user )
                            else :
                                print ('User not found or invalid credentials.')
                    else :
                        print ('Invalid choice.')
                except Exception as e :
                    print (f'Operation failed: {e }')
        except KeyboardInterrupt :
            print ('\n\nLogging out...')

    def run (self ):
        try :
            print ('Welcome to Employee Management System')
            while True :
                print ('\n1. Login')
                print ('2. Exit')
                choice =input ('Enter choice: ')
                if choice =='2':
                    break 
                elif choice =='1':
                    print ('\n--- Login ---')
                    username =input ('Username: ')
                    password =pwinput .pwinput (prompt ='Password: ')
                    user =self .get_logged_in_user (username ,password )
                    if user :
                        print ('Login Successful!')
                        if isinstance (user ,Managers )or isinstance (user ,Admin ):
                            self .manager_portal (user )
                        elif isinstance (user ,Employees ):
                            self .employee_portal (user )
                    else :
                        print ('Invalid credentials.')
        except KeyboardInterrupt :
            print ('\n\nExiting system. Goodbye!')
if __name__ =='__main__':
    system =EmployeeManagementSystem ()
    system .run ()
