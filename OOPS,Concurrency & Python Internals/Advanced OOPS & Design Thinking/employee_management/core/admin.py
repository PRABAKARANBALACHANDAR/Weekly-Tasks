from core.managers import Managers
from utils.json_handler import JSONHandler

class Admin(Managers):
    def __init__(self, emp_id, name, username, password, salary=150000):
        super().__init__(emp_id, name, username, password, 'CEO', salary)

    def crud_managers(self, action, manager_obj=None, **kwargs):
        if not self.can_manage_managers(): raise PermissionError("CEO access only")
        if action=='create': manager_obj.create()
        elif action=='update': manager_obj.update(**kwargs)
        elif action=='delete': manager_obj.delete()
        elif action=='read': return manager_obj.read()
