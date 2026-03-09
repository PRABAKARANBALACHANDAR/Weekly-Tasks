import json 
import os 

class JSONHandler :

    @staticmethod 
    def _get_path (filename ):
        base_dir =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))
        data_dir =os .path .join (base_dir ,'data')
        if not os .path .exists (data_dir ):
            os .makedirs (data_dir )
        return os .path .join (data_dir ,filename )

    @staticmethod 
    def load (filename ):
        path =JSONHandler ._get_path (filename )
        if not os .path .exists (path ):
            return {}
        try :
            with open (path ,'r')as f :
                return json .load (f )
        except (json .JSONDecodeError ,FileNotFoundError ):
            return {}

    @staticmethod 
    def save (filename ,data ):
        path =JSONHandler ._get_path (filename )
        try :
            with open (path ,'w')as f :
                json .dump (data ,f ,indent =4 )
        except IOError as e :
            print (f'Error saving to {filename }: {e }')

    @staticmethod 
    def load_by_field (filename ,field_name ,field_value ):
        data =JSONHandler .load (filename )
        return data .get (field_value )

    @staticmethod 
    def filter_by_field (filename ,field_name ,field_value ):
        data =JSONHandler .load (filename )
        return [v for k ,v in data .items ()if v .get (field_name )==field_value ]
