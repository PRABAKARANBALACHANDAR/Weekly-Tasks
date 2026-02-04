import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from core.data_base import Data
from utils.json_handler import JSONHandler


class Attendance(Data):
    
    def __init__(self, employee_id, date=None, status='Absent'):
        self._employee_id=employee_id
        self._date=date if date else datetime.now().strftime('%Y-%m-%d')
        self._status=status

    @property
    def employee_id(self):
        return self._employee_id

    @property
    def date(self):
        return self._date

    @property
    def status(self):
        return self._status

    def to_dict(self):
        return {
            'employee_id': self._employee_id,
            'date': self._date,
            'status': self._status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['employee_id'], data['date'], data['status'])

    def create(self):
        attendance_data=JSONHandler.load('attendance.json')
        key=f"{self._employee_id}_{self._date}"
        
        if key in attendance_data:
            raise ValueError(f"Attendance for {self._employee_id} on {self._date} already exists")
        
        attendance_data[key]=self.to_dict()
        JSONHandler.save('attendance.json', attendance_data)

    def read(self):
        attendance_data=JSONHandler.load('attendance.json')
        key=f"{self._employee_id}_{self._date}"
        if key in attendance_data:
            return Attendance.from_dict(attendance_data[key])
        return None

    def update(self, requester_employee=None, **kwargs):
        if requester_employee and not requester_employee.can_manage_attendance():
            raise PermissionError("Only HR can update attendance")
        
        attendance_data=JSONHandler.load('attendance.json')
        
        if requester_employee:
            employee_records=[
                (k, v) for k, v in attendance_data.items() 
                if v['employee_id']==self._employee_id
            ]
            
            if not employee_records:
                raise ValueError(f"No attendance records found for {self._employee_id}")
            
            employee_records.sort(key=lambda x: x[1]['date'], reverse=True)
            latest_key, latest_record=employee_records[0]
            latest_date=latest_record['date']
            
            if self._date != latest_date:
                raise PermissionError(
                    f"HR can only update the LAST attendance record. "
                    f"Last record date: {latest_date}, Attempted: {self._date}"
                )
        
        key=f"{self._employee_id}_{self._date}"
        
        if key not in attendance_data:
            raise ValueError(f"Attendance record for {self._employee_id} on {self._date} not found")
        
        if 'status' in kwargs:
            self._status=kwargs['status']
        
        attendance_data[key]=self.to_dict()
        JSONHandler.save('attendance.json', attendance_data)

    def delete(self):
        attendance_data=JSONHandler.load('attendance.json')
        key=f"{self._employee_id}_{self._date}"
        
        if key in attendance_data:
            del attendance_data[key]
            JSONHandler.save('attendance.json', attendance_data)
        else:
            raise ValueError(f"Attendance record not found")

    @staticmethod
    def get_employee_attendance(employee_id):
        attendance_data=JSONHandler.load('attendance.json')
        records=[
            Attendance.from_dict(v) for v in attendance_data.values() 
            if v['employee_id']==employee_id
        ]
        return sorted(records, key=lambda x: x.date)

    @staticmethod
    def calculate_attendance_percentage(employee_id):
        records=Attendance.get_employee_attendance(employee_id)
        if not records:
            return 0.0
        
        present_count=sum(1 for r in records if r.status in ['Present', 'present'])
        return (present_count / len(records)) * 100

    @staticmethod
    def mark_attendance_for_employee(employee_id, status='Present', date=None):
        attendance=Attendance(employee_id, date, status)
        attendance.create()

    def __str__(self):
        return f"Attendance: {self._employee_id} - {self._date} [{self._status}]"
