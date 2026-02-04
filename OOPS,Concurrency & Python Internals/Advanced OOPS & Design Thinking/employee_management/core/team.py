import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.data_base import Data
from utils.json_handler import JSONHandler
from utils.validators import Validators
class Team(Data):
    def __init__(self, team_id, team_leader_id, members=None, department='', level=2):
        if members is None:
            members=[]
        total_size=1 + len(members)
        if total_size > 6:
            raise ValueError(f"Team size cannot exceed 6 (Leader + 5 members). Current: {total_size}")
        self._team_id=team_id
        self._team_leader_id=team_leader_id
        self._members=members
        self._department=department
        self._level=level
    @property
    def team_id(self):
        return self._team_id
    @property
    def team_leader_id(self):
        return self._team_leader_id
    @property
    def members(self):
        return self._members
    @property
    def department(self):
        return self._department
    @property
    def level(self):
        return self._level
    @level.setter
    def level(self, value):
        Validators.validate_level(value)
        self._level=value
    def add_member(self, employee_id):
        if 1 + len(self._members)>=6:
            raise ValueError("Team is full (max 6 including leader)")
        if employee_id in self._members:
            raise ValueError(f"Employee {employee_id} already in team")
        self._members.append(employee_id)
    def remove_member(self, employee_id):
        if employee_id in self._members:
            self._members.remove(employee_id)
        else:
            raise ValueError(f"Employee {employee_id} not in team")
    def get_average_level(self):
        employees_data=JSONHandler.load('employees.json')
        leader_data=employees_data.get(self._team_leader_id)
        if not leader_data:
            return self._level
        total_level=leader_data.get('level', 2)
        count=1
        for member_id in self._members:
            member_data=employees_data.get(member_id)
            if member_data:
                total_level += member_data.get('level', 2)
                count += 1
        return total_level / count if count > 0 else self._level
    def to_dict(self):
        return {
            'team_id': self._team_id,
            'team_leader_id': self._team_leader_id,
            'members': self._members,
            'department': self._department,
            'level': self._level
        }
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['team_id'],
            data['team_leader_id'],
            data.get('members', []),
            data.get('department', ''),
            data.get('level', 2)
        )
    def create(self):
        teams=JSONHandler.load('teams.json')
        if self._team_id in teams:
            raise ValueError(f"Team ID '{self._team_id}' already exists")
        employees=JSONHandler.load('employees.json')
        managers=JSONHandler.load('managers.json')
        all_staff={**employees, **managers}
        if self._team_leader_id not in all_staff:
            raise ValueError(f"Team leader '{self._team_leader_id}' does not exist")
        for member_id in self._members:
            if member_id not in all_staff:
                raise ValueError(f"Team member '{member_id}' does not exist")
        total_size=1 + len(self._members)
        if total_size > 6:
            raise ValueError(f"Team size exceeds maximum of 6 (Current: {total_size})")
        teams[self._team_id]=self.to_dict()
        JSONHandler.save('teams.json', teams)
        print(f"Team '{self._team_id}' created [Leader: {self._team_leader_id}, Members: {len(self._members)}, Dept: {self._department}]")
    def read(self):
        teams=JSONHandler.load('teams.json')
        if self._team_id in teams:
            return Team.from_dict(teams[self._team_id])
        return None
    def update(self, **kwargs):
        teams=JSONHandler.load('teams.json')
        if self._team_id not in teams:
            raise ValueError(f"Team {self._team_id} not found")
        if 'level' in kwargs:
            self.level=kwargs['level']
        if 'department' in kwargs:
            self._department=kwargs['department']
        if 'members' in kwargs:
            new_members=kwargs['members']
            if 1 + len(new_members) > 6:
                raise ValueError("Team size would exceed maximum of 6")
            self._members=new_members
        teams[self._team_id]=self.to_dict()
        JSONHandler.save('teams.json', teams)
        print(f"Team '{self._team_id}' updated")
    def delete(self):
        teams=JSONHandler.load('teams.json')
        if self._team_id in teams:
            del teams[self._team_id]
            JSONHandler.save('teams.json', teams)
            print(f"Team '{self._team_id}' deleted")
        else:
            raise ValueError(f"Team {self._team_id} not found")
    def __str__(self):
        return f"Team {self._team_id} [Leader: {self._team_leader_id}, Members: {len(self._members)}, Level: {self._level}, Dept: {self._department}]"
