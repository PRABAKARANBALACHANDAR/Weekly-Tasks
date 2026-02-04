import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_base import Data
from utils.json_handler import JSONHandler
from utils.validators import Validators


class Project(Data):
    
    def __init__(self, project_id, title, department, duration, difficulty, status='pending'):
        Validators.validate_difficulty(difficulty)
        Validators.validate_project_status(status)
        
        self._project_id=project_id
        self._title=title
        self._department=department
        self._duration=duration
        self._difficulty=difficulty
        self._status=status.lower()
        self._assigned_team_id=None

    @property
    def project_id(self):
        return self._project_id

    @property
    def title(self):
        return self._title

    @property
    def department(self):
        return self._department

    @property
    def duration(self):
        return self._duration

    @property
    def difficulty(self):
        return self._difficulty

    @property
    def status(self):
        return self._status

    @property
    def assigned_team_id(self):
        return self._assigned_team_id

    @status.setter
    def status(self, value):
        Validators.validate_project_status(value)
        self._status=value.lower()

    @assigned_team_id.setter
    def assigned_team_id(self, value):
        self._assigned_team_id=value

    def to_dict(self):
        return {
            'project_id': self._project_id,
            'title': self._title,
            'department': self._department,
            'duration': self._duration,
            'difficulty': self._difficulty,
            'status': self._status,
            'assigned_team_id': self._assigned_team_id
        }

    @classmethod
    def from_dict(cls, data):
        proj=cls(
            data['project_id'],
            data['title'],
            data['department'],
            data['duration'],
            data['difficulty'],
            data.get('status', 'pending')
        )
        proj._assigned_team_id=data.get('assigned_team_id')
        return proj

    @classmethod
    def get_next_id(cls):
        projects=JSONHandler.load('projects.json')
        if not projects:
            return "P001"
        
        ids=[int(pid[1:]) for pid in projects.keys() if pid.startswith('P') and pid[1:].isdigit()]
        if not ids:
            return "P001"
        
        return f"P{max(ids) + 1:03d}"

    def create(self):
        projects=JSONHandler.load('projects.json')
        
        if self._project_id in projects:
            raise ValueError(f"Project ID '{self._project_id}' already exists")
        
        projects[self._project_id]=self.to_dict()
        JSONHandler.save('projects.json', projects)

    def read(self):
        projects=JSONHandler.load('projects.json')
        if self._project_id in projects:
            return Project.from_dict(projects[self._project_id])
        return None

    def update(self, **kwargs):
        projects=JSONHandler.load('projects.json')
        
        if self._project_id not in projects:
            raise ValueError(f"Project {self._project_id} not found")
        
        if 'status' in kwargs:
            self.status=kwargs['status']
        if 'assigned_team_id' in kwargs:
            self._assigned_team_id=kwargs['assigned_team_id']
        
        projects[self._project_id]=self.to_dict()
        JSONHandler.save('projects.json', projects)

    def delete(self):
        projects=JSONHandler.load('projects.json')
        
        if self._project_id in projects:
            del projects[self._project_id]
            JSONHandler.save('projects.json', projects)
        else:
            raise ValueError(f"Project {self._project_id} not found")

    def __str__(self):
        team_info=f", Team: {self._assigned_team_id}" if self._assigned_team_id else ""
        return f"Project '{self._title}' [{self._status}] - ID: {self._project_id}, Dept: {self._department}, Difficulty: {self._difficulty}{team_info}"
