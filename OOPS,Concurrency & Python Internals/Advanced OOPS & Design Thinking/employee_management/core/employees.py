from core.managers import Managers
from utils.json_handler import JSONHandler
from utils.validators import Validators

class Employees(Managers):
    def __init__(self, emp_id, name, username, password, dept, level, role='EMPLOYEE'):
        Validators.validate_level(level)
        super().__init__(emp_id, name, username, password, role, 0)
        self._dept=dept
        self._level=level
        self._leaves=0
        self._tasks=0
        self._diff_sum=0
        self._salary=self._calc_salary(level)

    @property
    def dept(self): return self._dept
    @property
    def level(self): return self._level
    @property
    def leaves(self): return self._leaves
    @property
    def tasks(self): return self._tasks
    @property
    def diff_sum(self): return self._diff_sum

    @level.setter
    def level(self, v):
        Validators.validate_level(v)
        self._level=v
        self._salary=self._calc_salary(v)

    def _calc_salary(self, l): return 30000 + (l * 15000)

    def add_task(self, d):
        self._tasks += 1
        self._diff_sum += d

    def to_dict(self):
        d=super().to_dict()
        d.update({'dept': self._dept, 'level': self._level, 'leaves': self._leaves,
                  'tasks': self._tasks, 'diff_sum': self._diff_sum})
        return d

    @classmethod
    def from_dict(cls, d):
        e=cls(d['id'], d['name'], d['username'], d['password'], d['dept'], d['level'], d.get('role', 'EMPLOYEE'))
        e._salary=d.get('salary', e._salary)
        e._leaves=d.get('leaves', 0)
        e._tasks=d.get('tasks', 0)
        e._diff_sum=d.get('diff_sum', 0)
        return e

    def create(self):
        m, e=JSONHandler.load('managers.json'), JSONHandler.load('employees.json')
        if self._id in m or self._id in e: raise ValueError("ID exists")
        e[self._id]=self.to_dict()
        JSONHandler.save('employees.json', e)
        

        from core.attendance import Attendance
        Attendance.mark_attendance_for_employee(self._id, status='Present')

    def read(self):
        e=JSONHandler.load('employees.json')
        return e.get(self._id)

    def update(self, **k):
        e=JSONHandler.load('employees.json')
        if self._id not in e: raise ValueError("Not found")
        if 'name' in k: self._name=k['name']
        if 'level' in k: self.level=k['level']
        if 'leaves' in k: self._leaves=k['leaves']
        if 'tasks' in k: self._tasks=k['tasks']
        if 'diff_sum' in k: self._diff_sum=k['diff_sum']
        if 'salary' in k: self._salary=k['salary']
        e[self._id]=self.to_dict()
        JSONHandler.save('employees.json', e)

    def delete(self):
        e=JSONHandler.load('employees.json')
        if self._id in e: del e[self._id]; JSONHandler.save('employees.json', e)
        else: raise ValueError("Not found")
