from abc import ABC ,abstractmethod 

class Data (ABC ):

    @property 
    @abstractmethod 
    def id (self ):
        pass 

    @property 
    @abstractmethod 
    def name (self ):
        pass 

    @abstractmethod 
    def create (self ):
        pass 

    @abstractmethod 
    def read (self ):
        pass 

    @abstractmethod 
    def update (self ,**kwargs ):
        pass 

    @abstractmethod 
    def delete (self ):
        pass 

    @abstractmethod 
    def to_dict (self ):
        pass 
