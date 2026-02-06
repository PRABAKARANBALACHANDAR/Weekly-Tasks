import os 
import sys 
sys .path .append (os .path .dirname (os .path .dirname (os .path .abspath (__file__ ))))
from core .data_base import Data 
from utils .json_handler import JSONHandler 
from utils .validators import Validators 

class Managers (Data ):

    def __init__ (self ,emp_id ,name ,username ,password ,role ,salary =0 ):
        Validators .validate_role (role )
        self ._id =emp_id 
        self ._name =name 
        self ._username =username 
        self ._password =password 
        self ._role =role .upper ()
        self ._salary =salary if salary >0 else self ._get_default_salary (role )

    @property 
    def id (self ):
        return self ._id 

    @property 
    def name (self ):
        return self ._name 

    @property 
    def username (self ):
        return self ._username 

    @property 
    def role (self ):
        return self ._role 

    @property 
    def salary (self ):
        return self ._salary 

    @salary .setter 
    def salary (self ,v ):
        self ._salary =v 

    def _get_default_salary (self ,r ):
        salaries ={'CEO':150000 ,'CTO':120000 ,'COO':120000 ,'CFO':110000 ,'HR':80000 }
        return salaries .get (r .upper (),60000 )

    def verify_password (self ,p ):
        return self ._password ==p 

    def can_manage_managers (self ):
        return self ._role =='CEO'

    def can_manage_projects (self ):
        return self ._role in ['CTO','COO','CEO']

    def can_allocate_tasks (self ):
        return self ._role in ['CTO','COO']

    def can_calculate_performance (self ):
        return self ._role =='COO'

    def can_manage_finances (self ):
        return self ._role =='CFO'

    def can_manage_employees (self ):
        return self ._role =='HR'

    def can_manage_attendance (self ):
        return self ._role =='HR'

    @staticmethod 
    def get_next_manager_id ():

        managers =JSONHandler .load ('managers.json')
        if not managers :
            return 'M001'

        existing_ids =sorted ([int (k [1 :])for k in managers .keys ()if k .startswith ('M')and len (k )>1 and k [1 :].isdigit ()])

        if not existing_ids :
            return 'M001'

        for i in range (1 ,max (existing_ids )+1 ):
            if i not in existing_ids :
                return f'M{i :03d}'

        return f'M{max (existing_ids )+1 :03d}'

    def to_dict (self ):
        return {'id':self ._id ,'name':self ._name ,'username':self ._username ,'password':self ._password ,'role':self ._role ,'salary':self ._salary }

    def create (self ):
        m ,e =(JSONHandler .load ('managers.json'),JSONHandler .load ('employees.json'))
        if self ._id in m or self ._id in e :
            raise ValueError (f'ID {self ._id } exists')
        if self ._role in ['CEO','CTO','COO','CFO','HR']:
            if any ((x .get ('role')==self ._role for x in m .values ())):
                raise ValueError (f'{self ._role } already exists. Only one {self ._role } is allowed.')
        m [self ._id ]=self .to_dict ()
        JSONHandler .save ('managers.json',m )

    def read (self ):
        m =JSONHandler .load ('managers.json')
        return m .get (self ._id )

    def update (self ,**k ):
        m =JSONHandler .load ('managers.json')
        if self ._id not in m :
            raise ValueError ('Not found')
        if 'name'in k :
            self ._name =k ['name']
        if 'salary'in k :
            self ._salary =k ['salary']
        if 'password'in k :
            self ._password =k ['password']
        m [self ._id ]=self .to_dict ()
        JSONHandler .save ('managers.json',m )

    def delete (self ):
        m =JSONHandler .load ('managers.json')
        if self ._id in m :
            del m [self ._id ]
            JSONHandler .save ('managers.json',m )
        else :
            raise ValueError ('Not found')

    def can_manage_managers (self ):
        return self ._role =='CEO'

    def can_manage_projects (self ):
        return self ._role in ['CTO','COO','CEO']

    def can_allocate_tasks (self ):
        return self ._role in ['CTO','COO']

    def can_calculate_performance (self ):
        return self ._role =='COO'

    def can_manage_finances (self ):
        return self ._role =='CFO'

    def can_manage_employees (self ):
        return self ._role =='HR'

    def can_manage_attendance (self ):
        return self ._role =='HR'

    def __str__ (self ):
        return f'[MGR] {self ._name } ({self ._role }) - ID: {self ._id }'
