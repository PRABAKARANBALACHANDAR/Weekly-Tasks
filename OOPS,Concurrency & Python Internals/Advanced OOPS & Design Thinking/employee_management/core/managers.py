import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_base import Data
from utils.json_handler import JSONHandler
from utils.validators import Validators

class Managers(Data):
    def __init__(self, emp_id, name, username, password, role, salary=0):
        Validators.validate_role(role)
        self._id=emp_id
        self._name=name
        self._username=username
        self._password=password
        self._role=role.upper()
        self._salary=salary if salary > 0 else self._get_default_salary(role)

    @property
    def id(self): return self._id
    @property
    def name(self): return self._name
    @property
    def username(self): return self._username
    @property
    def role(self): return self._role
    @property
    def salary(self): return self._salary
    @salary.setter
    def salary(self, v): self._salary=v

    def _get_default_salary(self, r):
        salaries={'CEO': 150000, 'CTO': 120000, 'COO': 120000, 'CFO': 110000, 'HR': 80000}
        return salaries.get(r.upper(), 60000)

    def verify_password(self, p): return self._password==p

    def can_manage_managers(self): return self._role=='CEO'
    def can_manage_projects(self): return self._role in ['CTO', 'COO', 'CEO']
    def can_allocate_tasks(self): return self._role in ['CTO', 'COO']
    def can_calculate_performance(self): return self._role=='COO'
    def can_manage_finances(self): return self._role=='CFO'
    def can_manage_employees(self): return self._role=='HR'
    def can_manage_attendance(self): return self._role=='HR'

    def to_dict(self):
        return {'id': self._id, 'name': self._name, 'username': self._username, 
                'password': self._password, 'role': self._role, 'salary': self._salary}

    def create(self):
        m, e=JSONHandler.load('managers.json'), JSONHandler.load('employees.json')
        if self._id in m or self._id in e: raise ValueError(f"ID {self._id} exists")
        if self._role in ['CEO', 'CTO', 'COO', 'CFO', 'HR']:
            if any(x.get('role')==self._role for x in m.values()):
                raise ValueError(f"{self._role} already exists. Only one {self._role} is allowed.")
        m[self._id]=self.to_dict()
        JSONHandler.save('managers.json', m)

    def read(self):
        m=JSONHandler.load('managers.json')
        return m.get(self._id)

    def update(self, **k):
        m=JSONHandler.load('managers.json')
        if self._id not in m: raise ValueError("Not found")
        if 'name' in k: self._name=k['name']
        if 'salary' in k: self._salary=k['salary']
        if 'password' in k: self._password=k['password']
        m[self._id]=self.to_dict()
        JSONHandler.save('managers.json', m)

    def delete(self):
        m=JSONHandler.load('managers.json')
        if self._id in m: del m[self._id]; JSONHandler.save('managers.json', m)
        else: raise ValueError("Not found")

    def calculate_employee_performance(self, employee_obj):
        if not self.can_calculate_performance(): raise PermissionError("COO Access Only")
        from core.attendance import Attendance
        attendance_percent=Attendance.calculate_attendance_percentage(employee_obj.id)
        score=(employee_obj.tasks * 10) + (employee_obj.diff_sum * 5) - (employee_obj.leaves * 2) + int(attendance_percent)
        return score

    def suggest_promotion(self, employee_obj):
        if not self.can_calculate_performance(): raise PermissionError("COO Access Only")
        score=self.calculate_employee_performance(employee_obj)
        return score > 150 and employee_obj.level < 3  

    def manage_salary(self, employee_obj, increment):
        if not self.can_manage_finances(): raise PermissionError("CFO Access Only")
        new_salary=employee_obj.salary + increment
        employee_obj.update(salary=new_salary)

    def calculate_company_revenue(self):
        if not self.can_manage_finances(): raise PermissionError("CFO Access Only")
        projects=JSONHandler.load('projects.json')
        total=sum(p['difficulty'] * p['duration'] * 1000 for p in projects.values() if p.get('status')=='completed')
        revenue_data=JSONHandler.load('revenue.json')
        from datetime import datetime
        revenue_data[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]={'total_revenue': total}
        JSONHandler.save('revenue.json', revenue_data)
        return total

    def manage_leave_requests(self, request_id, status):

        if not (self.can_manage_attendance() or self.role in ['CEO', 'CTO', 'COO', 'CFO']):
             raise PermissionError("Access Denied")
        

        if status and not self.can_manage_attendance():
            raise PermissionError("Only HR can Approve/Reject leave requests")

        from core.leave_requests import LeaveRequests
        requests=LeaveRequests.get_all_requests()
        target_req=next((r for r in requests if r.request_id==request_id), None)
        
        if not target_req:
            raise ValueError("Request not found")
        

        target_req.update(status=status)
        

        if status=='Approved':
            from core.employees import Employees
            emp_data=JSONHandler.load('employees.json').get(target_req.emp_id)
            if emp_data:
                emp=Employees.from_dict(emp_data)
                emp.update(leaves=emp.leaves + 1)
        
        return True

    def __str__(self): return f"[MGR] {self._name} ({self._role}) - ID: {self._id}"
