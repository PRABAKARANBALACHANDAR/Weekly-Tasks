import sys 
import os 
sys .path .append (os .path .dirname (os .path .dirname (os .path .abspath (__file__ ))))
from core .data_base import Data 
from utils .json_handler import JSONHandler 
import uuid 

class LeaveRequests (Data ):

    def __init__ (self ,emp_id ,date ,reason ,status ='Pending',request_id =None ):
        self ._request_id =request_id if request_id else str (uuid .uuid4 ())[:8 ]
        self ._emp_id =emp_id 
        self ._date =date 
        self ._reason =reason 
        self ._status =status 

    @property 
    def id (self ):
        return self ._request_id 

    @property 
    def name (self ):
        return f'LeaveRequest {self ._request_id }'

    @property 
    def request_id (self ):
        return self ._request_id 

    @property 
    def emp_id (self ):
        return self ._emp_id 

    @property 
    def date (self ):
        return self ._date 

    @property 
    def reason (self ):
        return self ._reason 

    @property 
    def status (self ):
        return self ._status 

    @status .setter 
    def status (self ,val ):
        self ._status =val 

    def to_dict (self ):
        return {'request_id':self ._request_id ,'emp_id':self ._emp_id ,'date':self ._date ,'reason':self ._reason ,'status':self ._status }

    def create (self ):
        data =JSONHandler .load ('leave_requests.json')
        data [self ._request_id ]=self .to_dict ()
        JSONHandler .save ('leave_requests.json',data )

    def read (self ):
        data =JSONHandler .load ('leave_requests.json')
        return data .get (self ._request_id )

    def update (self ,**kwargs ):
        data =JSONHandler .load ('leave_requests.json')
        if self ._request_id not in data :
            raise ValueError ('Request not found')
        if 'status'in kwargs :
            self ._status =kwargs ['status']
        data [self ._request_id ]=self .to_dict ()
        JSONHandler .save ('leave_requests.json',data )

    def delete (self ):
        data =JSONHandler .load ('leave_requests.json')
        if self ._request_id in data :
            del data [self ._request_id ]
            JSONHandler .save ('leave_requests.json',data )

    @staticmethod 
    def get_all_requests ():
        data =JSONHandler .load ('leave_requests.json')
        return [LeaveRequests (v ['emp_id'],v ['date'],v ['reason'],v ['status'],k )for k ,v in data .items ()]
