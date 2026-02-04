import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.admin import Admin
from core.managers import Managers
from core.employees import Employees
from utils.json_handler import JSONHandler

def initialize_system():
    """Initializes the system with a default Admin if none exists."""
    managers_data=JSONHandler.load('managers.json')
    admin_exists=False
    
    # Check if any manager has CEO role
    if managers_data:
        for mgr in managers_data.values():
            if mgr.get('role')=='CEO':
                admin_exists=True
                break
    
    if not admin_exists:
        print("Initializing system with default Admin...")
        # Default Admin Credentials
        admin=Admin('admin01', 'System Administrator', 'admin', 'admin123')
        try:
            admin.create()
            print("System initialized successfully.")
            print("Default Credentials - Username: 'admin', Password: 'admin123'")
        except Exception as e:
            print(f"Error initializing system: {e}")

def get_logged_in_user(username, password):
    """authenticate user and return the object."""
    # Check Managers
    managers_data=JSONHandler.load('managers.json')
    if managers_data:
        for m_id, m in managers_data.items():
            if m['username']==username and m['password']==password:
                # If CEO, return Admin object, else Managers object
                if m['role']=='CEO':
                    return Admin(m['id'], m['name'], m['username'], m['password'], m['salary'])
                else:
                    return Managers(m['id'], m['name'], m['username'], m['password'], m['role'], m['salary'])

    # Check Employees
    employees_data=JSONHandler.load('employees.json')
    if employees_data:
        for e_id, e in employees_data.items():
            if e['username']==username and e['password']==password:
                return Employees.from_dict(e)
    
    return None

def manage_managers_menu(admin_user):
    while True:
        print("\n--- Manage Managers (CEO Only) ---")
        print("1. Create Manager")
        print("2. Read Manager")
        print("3. Update Manager")
        print("4. Delete Manager")
        print("5. List All Managers")
        print("0. Back")
        
        choice=input("Enter choice: ")
        
        try:
            if choice=='1':
                e_id=input("Enter ID: ")
                name=input("Enter Name: ")
                uname=input("Enter Username: ")
                pwd=input("Enter Password: ")
                role=input("Enter Role (CTO, COO, CFO, HR): ")
                mgr=Managers(e_id, name, uname, pwd, role)
                admin_user.crud_managers('create', manager_obj=mgr)
                print("Manager created successfully.")
                
            elif choice=='2':
                e_id=input("Enter ID to read: ")
                # We need a dummy object to call read, or use static/class method if available.
                # The existing design requires an object with ID to read.
                dummy_mgr=Managers(e_id, '', '', '', 'HR') # Role doesn't matter for id lookup
                data=admin_user.crud_managers('read', manager_obj=dummy_mgr)
                if data:
                    print(f"Manager Details: {data}")
                else:
                    print("Manager not found.")

            elif choice=='3':
                e_id=input("Enter ID to update: ")
                dummy_mgr=Managers(e_id, '', '', '', 'HR')
                print("Leave fields blank to skip update")
                name=input("New Name: ")
                pwd=input("New Password: ")
                salary_str=input("New Salary: ")
                
                updates={}
                if name: updates['name']=name
                if pwd: updates['password']=pwd
                if salary_str: updates['salary']=float(salary_str)
                
                admin_user.crud_managers('update', manager_obj=dummy_mgr, **updates)
                print("Manager updated successfully.")

            elif choice=='4':
                e_id=input("Enter ID to delete: ")
                dummy_mgr=Managers(e_id, '', '', '', 'HR')
                admin_user.crud_managers('delete', manager_obj=dummy_mgr)
                print("Manager deleted successfully.")

            elif choice=='5':
                data=JSONHandler.load('managers.json')
                for m in data.values():
                    print(f"ID: {m['id']}, Name: {m['name']}, Role: {m['role']}")

            elif choice=='0':
                break
        except Exception as e:
            print(f"Error: {e}")

def manage_employees_menu(manager_user):
    while True:
        print("\n--- Manage Employees ---")
        print("1. Create Employee")
        print("2. Read Employee")
        print("3. Update Employee")
        print("4. Delete Employee")
        print("5. List All Employees")
        print("0. Back")
        
        choice=input("Enter choice: ")
        
        try:
            if choice=='1':
                if not manager_user.can_manage_employees() and manager_user.role != 'CEO':
                     print("Permission Denied (HR/CEO Only)")
                     continue
                     
                e_id=input("Enter ID: ")
                name=input("Enter Name: ")
                uname=input("Enter Username: ")
                pwd=input("Enter Password: ")
                dept=input("Enter Dept: ")
                level=int(input("Enter Level (1-3): "))
                
                emp=Employees(e_id, name, uname, pwd, dept, level)
                emp.create()
                print("Employee created successfully.")

            elif choice=='2':
                e_id=input("Enter ID to read: ")
                # Using a dummy employee for read
                dummy_emp=Employees(e_id, '', '', '', '', 1)
                data=dummy_emp.read()
                if data:
                    print(f"Employee Details: {data}")
                else:
                    print("Employee not found.")

            elif choice=='3':
                # Update
                e_id=input("Enter ID to update: ")
                dummy_emp=Employees(e_id, '', '', '', '', 1)
                
                print("Leave fields blank to skip")
                name=input("New Name: ")
                level_str=input("New Level: ")
                salary_str=input("New Salary: ") # Special permission usually but letting generic update for now
                
                updates={}
                if name: updates['name']=name
                if level_str: updates['level']=int(level_str)
                if salary_str and manager_user.can_manage_finances():
                     updates['salary']=float(salary_str)
                elif salary_str:
                     print("Warning: Only CFO/CEO can update salary directly per logic(implied).")

                dummy_emp.update(**updates)
                print("Employee updated.")

            elif choice=='4':
                e_id=input("Enter ID to delete: ")
                dummy_emp=Employees(e_id, '', '', '', '', 1)
                dummy_emp.delete()
                print("Employee deleted.")

            elif choice=='5':
                data=JSONHandler.load('employees.json')
                for e in data.values():
                    print(f"ID: {e['id']}, Name: {e['name']}, Dept: {e['dept']}")

            elif choice=='0':
                break
        except Exception as e:
            print(f"Error: {e}")

from core.leave_requests import LeaveRequests

def employee_portal(employee_user):
    while True:
        print(f"\n--- Employee Portal: {employee_user.name} ---")
        print("1. View Profile")
        print("2. Request Leave")
        print("3. View My Leave Requests")
        print("0. Logout")
        
        choice=input("Enter choice: ")
        
        if choice=='1':
            print(f"ID: {employee_user.id}")
            print(f"Name: {employee_user.name}")
            print(f"Role: {employee_user.role}")
            print(f"Dept: {employee_user.dept}")
            print(f"Level: {employee_user.level}")
            print(f"Salary: {employee_user.salary}")
            print(f"Leaves: {employee_user.leaves}")
            print(f"Tasks: {employee_user.tasks}")
            print(f"Performance Score (Diff Sum): {employee_user.diff_sum}")

        elif choice=='2':
            date_str=input("Enter Date (YYYY-MM-DD): ")
            reason=input("Enter Reason: ")
            req=LeaveRequests(employee_user.id, date_str, reason)
            req.create()
            print("Leave Request Submitted.")

        elif choice=='3':
            requests=LeaveRequests.get_all_requests()
            my_requests=[r for r in requests if r.emp_id==employee_user.id]
            if my_requests:
                for r in my_requests:
                    print(f"Date: {r.date}, Status: {r.status}, Reason: {r.reason}")
            else:
                print("No leave requests found.")

        elif choice=='0':
            break

from core.team import Team
from core.attendance import Attendance

def manage_teams_menu():
    while True:
        print("\n--- Manage Teams ---")
        print("1. Create Team")
        print("2. Add Member to Team")
        print("3. View Teams")
        print("0. Back")
        choice=input("Enter choice: ")
        
        try:
            if choice=='1':
                t_id=input("Team ID: ")
                leader_id=input("Leader ID: ")
                dept=input("Dept: ")
                level=int(input("Level (1-3): "))
                t=Team(t_id, leader_id, department=dept, level=level)
                t.create()
                
            elif choice=='2':
                t_id=input("Team ID: ")
                emp_id=input("Employee ID: ")
                teams=JSONHandler.load('teams.json')
                if t_id in teams:
                    t=Team.from_dict(teams[t_id])
                    t.add_member(emp_id)
                    t.update() # Save changes
                    print("Member added.")
                else:
                    print("Team not found.")

            elif choice=='3':
                teams=JSONHandler.load('teams.json')
                for t in teams.values():
                    print(f"ID: {t['team_id']}, Leader: {t['team_leader_id']}, Members: {len(t.get('members', []))}")
            
            elif choice=='0':
                break
        except Exception as e:
            print(f"Error: {e}")

def manage_attendance_menu():
    while True:
        print("\n--- Attendance Management ---")
        print("1. View All Attendance")
        print("2. View Employee Attendance")
        print("3. Calculate Attendance Percentage")
        print("0. Back")
        choice=input("Enter choice: ")
        
        if choice=='1':
            data=JSONHandler.load('attendance.json')
            for k, v in data.items():
                print(f"{v['date']} - {v['employee_id']}: {v['status']}")
        elif choice=='2':
            e_id=input("Employee ID: ")
            recs=Attendance.get_employee_attendance(e_id)
            for r in recs:
                print(f"{r.date}: {r.status}")
        elif choice=='3':
            e_id=input("Employee ID: ")
            pct=Attendance.calculate_attendance_percentage(e_id)
            print(f"Attendance Percentage: {pct:.2f}%")
        elif choice=='0':
            break

def view_employees_menu():
    data=JSONHandler.load('employees.json')
    emps=[Employees.from_dict(e) for e in data.values()]
    
    while True:
        print("\n--- View Employees ---")
        print("1. View All")
        print("2. Group by Team")
        print("3. By Performance (Descending)")
        print("0. Back")
        choice=input("Enter choice: ")
        
        if choice=='1':
            for e in emps: print(e)
        elif choice=='2':
            # Load teams 
            teams=JSONHandler.load('teams.json')
            for t_data in teams.values():
                print(f"\nTeam {t_data['team_id']} (Leader: {t_data['team_leader_id']})")
                for m_id in t_data.get('members', []):
                    e_data=data.get(m_id)
                    if e_data: print(f"  - {e_data['name']} ({e_data['role']})")
        elif choice=='3':
            sorted_emps=sorted(emps, key=lambda x: x.diff_sum, reverse=True)
            for e in sorted_emps:
                print(f"{e.name}: Score {e.diff_sum}")
        elif choice=='0':
            break

def manager_portal(manager_user):
    while True:
        print(f"\n--- Manager Portal: {manager_user.name} ({manager_user.role}) ---")
        print("1. View My Profile")
        
        if manager_user.can_manage_managers():
            print("2. Manage Managers (CEO)")
            
        if manager_user.can_manage_employees():
             # Strictly HR only for managing employees (create/update/delete) as per user request "except HR" for Admin
            print("3. Manage Employees (HR)")
            
        # Add more features as per existing methods in Managers class
        if manager_user.can_calculate_performance() or manager_user.role=='CEO':
             print("4. Calculate Employee Performance (COO)")
             print("5. Suggest Promotion (COO)")
             
        if manager_user.can_manage_finances() or manager_user.role=='CEO':
             print("6. Manage Finances/Salary (CFO)")
             print("7. Calculate Company Revenue (CFO)")

        if manager_user.can_manage_attendance() or manager_user.role in ['CEO', 'CTO', 'COO', 'CFO']:
             print("8. Manage Leave Requests (View: All, Action: HR Only)")

        if manager_user.role in ['CEO', 'CTO', 'COO']:
             print("9. Manage Teams")

        if manager_user.can_manage_attendance():
             print("10. Manage Attendance (HR)")
             
        print("11. View All Employees (Team/Performance)")

        print("0. Logout")
        
        choice=input("Enter choice: ")
        
        try:
            if choice=='1':
                print(manager_user.to_dict())
            elif choice=='2' and (manager_user.can_manage_managers()):
                manage_managers_menu(manager_user)
            elif choice=='3' and (manager_user.can_manage_employees()):
                manage_employees_menu(manager_user)
            elif choice=='4' and (manager_user.can_calculate_performance() or manager_user.role=='CEO'):
                emp_id=input("Enter Employee ID: ")
                data=JSONHandler.load('employees.json').get(emp_id)
                if data:
                    emp=Employees.from_dict(data)
                    score=manager_user.calculate_employee_performance(emp)
                    print(f"Performance Score: {score}")
                else:
                    print("Employee not found.")
            elif choice=='5' and (manager_user.can_calculate_performance() or manager_user.role=='CEO'):
                emp_id=input("Enter Employee ID: ")
                data=JSONHandler.load('employees.json').get(emp_id)
                if data:
                    emp=Employees.from_dict(data)
                    promote=manager_user.suggest_promotion(emp)
                    print(f"Promotion Suggested: {'Yes' if promote else 'No'}")
                else:
                    print("Employee not found.")
            elif choice=='6' and (manager_user.can_manage_finances() or manager_user.role=='CEO'):
                emp_id=input("Enter Employee ID: ")
                increment=float(input("Enter Salary Increment Amount: "))
                data=JSONHandler.load('employees.json').get(emp_id)
                if data:
                    emp=Employees.from_dict(data)
                    manager_user.manage_salary(emp, increment)
                    print("Salary updated.")
                else:
                    print("Employee not found.")
            elif choice=='7' and (manager_user.can_manage_finances() or manager_user.role=='CEO'):
                 revenue=manager_user.calculate_company_revenue()
                 print(f"Total Company Revenue: {revenue}")

            elif choice=='8' and (manager_user.can_manage_attendance() or manager_user.role in ['CEO', 'CTO', 'COO', 'CFO']):
                 print("\n--- Pending Leave Requests ---")
                 requests=LeaveRequests.get_all_requests()
                 pending_reqs=[r for r in requests if r.status=='Pending']
                 if not pending_reqs:
                     print("No pending requests.")
                 else:
                     for r in pending_reqs:
                         print(f"ID: {r.request_id}, EmpID: {r.emp_id}, Date: {r.date}, Reason: {r.reason}")
                     
                     if manager_user.can_manage_attendance():
                         req_id=input("Enter Request ID to action (or leave blank to cancel): ")
                         if req_id:
                             action=input("Approve or Reject? (a/r): ").lower()
                             status="Approved" if action=='a' else "Rejected" if action=='r' else None
                             if status:
                                 manager_user.manage_leave_requests(req_id, status)
                                 print(f"Request {status}.")
                             else:
                                 print("Invalid action.")
                     else:
                         print("\n[INFO] Only HR can approve/reject requests.")

            elif choice=='9' and (manager_user.role in ['CEO', 'CTO', 'COO']):
                manage_teams_menu()

            elif choice=='10' and manager_user.can_manage_attendance():
                manage_attendance_menu()

            elif choice=='11':
                view_employees_menu()

            elif choice=='0':
                break
        except Exception as e:
            print(f"Operation failed: {e}")

def main():
    print("Welcome to Employee Management System")
    initialize_system()
    
    while True:
        print("\n--- Login ---")
        username=input("Username: ")
        password=input("Password: ")
        
        user=get_logged_in_user(username, password)
        
        if user:
            print("Login Successful!")
            if isinstance(user, Managers) or isinstance(user, Admin):
                manager_portal(user)
            elif isinstance(user, Employees):
                employee_portal(user)
        else:
            print("Invalid credentials. Please try again.")
            retry=input("Try again? (y/n): ")
            if retry.lower() != 'y':
                break

if __name__=="__main__":
    main()
