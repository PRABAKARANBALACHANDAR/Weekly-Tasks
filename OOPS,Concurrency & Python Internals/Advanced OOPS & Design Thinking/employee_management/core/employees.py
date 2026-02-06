from core .managers import Managers 
from utils .json_handler import JSONHandler 
from utils .validators import Validators 

class Employees (Managers ):

    def __init__ (self ,emp_id ,name ,username ,password ,dept ,experience ,role ='EMPLOYEE'):
        self ._experience =float (experience )
        self ._level =self ._calculate_level (self ._experience )
        salary =self ._calc_salary (self ._level )
        super ().__init__ (emp_id ,name ,username ,password ,role ,salary )
        self ._dept =dept 
        self ._leaves =0 
        self ._tasks =0 
        self ._diff_sum =0 

    def _calculate_level (self ,exp ):
        if exp <2 :
            return 1 
        elif exp <5 :
            return 2 
        else :
            return 3 

    @property 
    def experience (self ):
        return self ._experience 

    @property 
    def dept (self ):
        return self ._dept 

    @property 
    def level (self ):
        return self ._level 

    @property 
    def leaves (self ):
        return self ._leaves 

    @property 
    def tasks (self ):
        return self ._tasks 

    @property 
    def diff_sum (self ):
        return self ._diff_sum 

    @level .setter 
    def level (self ,v ):
        Validators .validate_level (v )
        self ._level =v 
        self ._salary =self ._calc_salary (v )

    def _calc_salary (self ,l ):
        return 30000 +l *15000 

    def add_task (self ,d ):
        self ._tasks +=1 
        self ._diff_sum +=d 

    def to_dict (self ):
        d =super ().to_dict ()
        d .update ({'dept':self ._dept ,'level':self ._level ,'experience':self ._experience ,'leaves':self ._leaves ,'tasks':self ._tasks ,'diff_sum':self ._diff_sum })
        return d 

    @staticmethod 
    def get_next_employee_id ():

        employees =JSONHandler .load ('employees.json')
        if not employees :
            return 'E001'

        existing_ids =sorted ([int (k [1 :])for k in employees .keys ()if k .startswith ('E')and len (k )>1 and k [1 :].isdigit ()])

        if not existing_ids :
            return 'E001'

        for i in range (1 ,max (existing_ids )+1 ):
            if i not in existing_ids :
                return f'E{i :03d}'

        return f'E{max (existing_ids )+1 :03d}'

    @classmethod 
    def from_dict (cls ,d ):
        exp =d .get ('experience',0 )
        e =cls (d ['id'],d ['name'],d ['username'],d ['password'],d ['dept'],exp ,d .get ('role','EMPLOYEE'))
        e ._salary =d .get ('salary',e ._salary )
        e ._leaves =d .get ('leaves',0 )
        e ._tasks =d .get ('tasks',0 )
        e ._diff_sum =d .get ('diff_sum',0 )
        if 'level'in d :
            e ._level =d ['level']
        return e 

    def create (self ):
        m ,e =(JSONHandler .load ('managers.json'),JSONHandler .load ('employees.json'))
        if self ._id in m or self ._id in e :
            raise ValueError ('ID exists')
        e [self ._id ]=self .to_dict ()
        JSONHandler .save ('employees.json',e )
        from core .attendance import Attendance 
        try :
            Attendance .mark_attendance_for_employee (self ._id ,status ='Present')
            print (f'[System] Auto-marked attendance for {self ._name }')
        except Exception as ex :
            print (f'[Warning] Failed to auto-mark attendance: {ex }')

    def read (self ):
        e =JSONHandler .load ('employees.json')
        return e .get (self ._id )

    def update (self ,**k ):
        e =JSONHandler .load ('employees.json')
        if self ._id not in e :
            raise ValueError ('Not found')
        if 'name'in k :
            self ._name =k ['name']
        if 'level'in k :
            self .level =k ['level']
        if 'leaves'in k :
            self ._leaves =k ['leaves']
        if 'tasks'in k :
            self ._tasks =k ['tasks']
        if 'diff_sum'in k :
            self ._diff_sum =k ['diff_sum']
        if 'salary'in k :
            self ._salary =k ['salary']
        e [self ._id ]=self .to_dict ()
        JSONHandler .save ('employees.json',e )

    def delete (self ):
        e =JSONHandler .load ('employees.json')
        if self ._id in e :
            del e [self ._id ]
            JSONHandler .save ('employees.json',e )
        else :
            raise ValueError ('Not found')

    def update_project_log (self ,project_id ,status ,note ):
        from core .project import Project 
        from core .team import Team 
        projects_data =JSONHandler .load ('projects.json')
        if project_id not in projects_data :
            raise ValueError ('Project not found')
        project =Project .from_dict (projects_data [project_id ])
        team_id =project .assigned_team_id 
        if not team_id :
            raise PermissionError ('Project not assigned to any team')
        teams_data =JSONHandler .load ('teams.json')
        if team_id not in teams_data :
            raise ValueError ('Assigned team data missing')
        team_data =teams_data [team_id ]
        if team_data .get ('team_leader_id')!=self ._id :
            raise PermissionError (f'Only the Team Lead of {team_id } can update logs.')
        project .add_log (status ,note ,f'{self ._name } (TL)')
        project .update ()
        print (f'[Log] Project {project_id } updated: {status } - {note }')
