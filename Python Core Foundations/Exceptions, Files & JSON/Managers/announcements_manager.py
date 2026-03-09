import json 
import os 
from datetime import datetime 

class AnnouncementManager :
    def __init__ (self ,storage_file =None ):
        self ._storage_file =storage_file or os .path .join (os .path .dirname (__file__ ),"..","Data","announcements.json")
        self ._announcements =[]
        self ._load ()

    def _load (self ):
        if os .path .exists (self ._storage_file ):
            try :
                with open (self ._storage_file ,"r")as f :
                    self ._announcements =json .load (f )
            except Exception :
                self ._announcements =[]
        else :
            self ._announcements =[]

    def _save (self ):
        with open (self ._storage_file ,"w")as f :
            json .dump (self ._announcements ,f ,indent =2 ,ensure_ascii =False )

    def post_announcement (self ,title ,content ,deadline =None ):
        if not title or not content :
            raise ValueError ("Title and content cannot be empty.")

        if deadline :
            try :
                from datetime import datetime 
                datetime .strptime (deadline ,"%Y-%m-%d")
            except ValueError :
                raise ValueError ("Invalid deadline format. Use YYYY-MM-DD.")

        announcement ={
        "id":len (self ._announcements )+1 ,
        "title":title ,
        "content":content ,
        "posted_at":datetime .now ().strftime ("%Y-%m-%d %H:%M:%S"),
        "deadline":deadline ,
        "visible":True 
        }
        self ._announcements .append (announcement )
        self ._save ()
        return announcement ["id"]

    def cleanup_expired_announcements (self ):

        from datetime import datetime 
        current_date =datetime .now ().strftime ("%Y-%m-%d")

        original_count =len (self ._announcements )
        self ._announcements =[
        a for a in self ._announcements 
        if not a .get ("deadline")or a ["deadline"]>=current_date 
        ]

        if len (self ._announcements )<original_count :
            self ._save ()
            return original_count -len (self ._announcements )
        return 0 

    def view_all_announcements (self ):

        self .cleanup_expired_announcements ()

        if not self ._announcements :
            print ("No announcements available.")
            return 

        print ("\n"+"="*60 )
        print ("ALL ANNOUNCEMENTS")
        print ("="*60 )
        for announcement in reversed (self ._announcements ):
            if announcement .get ("visible",True ):
                print (f"\nID: {announcement ['id']}")
                print (f"Title: {announcement ['title']}")
                print (f"Posted: {announcement ['posted_at']}")
                if announcement .get ('deadline'):
                    print (f"Deadline: {announcement ['deadline']}")
                print (f"Content: {announcement ['content']}")
                print ("-"*60 )

    def delete_announcement (self ,announcement_id ):
        try :
            announcement_id =int (announcement_id )
        except ValueError :
            raise ValueError ("Invalid ID format.")

        for i ,announcement in enumerate (self ._announcements ):
            if announcement ["id"]==announcement_id :
                self ._announcements .pop (i )
                self ._save ()
                return True 

        raise ValueError (f"Announcement with ID {announcement_id } not found.")

    def edit_announcement (self ,announcement_id ,title =None ,content =None ):
        try :
            announcement_id =int (announcement_id )
        except ValueError :
            raise ValueError ("Invalid ID format.")

        for announcement in self ._announcements :
            if announcement ["id"]==announcement_id :
                if title :
                    announcement ["title"]=title 
                if content :
                    announcement ["content"]=content 
                announcement ["updated_at"]=datetime .now ().strftime ("%Y-%m-%d %H:%M:%S")
                self ._save ()
                return True 

        raise ValueError (f"Announcement with ID {announcement_id } not found.")

    def get_announcements_count (self ):
        return len ([a for a in self ._announcements if a .get ("visible",True )])

    def get_active_announcements (self ):

        self .cleanup_expired_announcements ()
        return [a for a in self ._announcements if a .get ("visible",True )]

    def get_unread_count (self ,viewed_announcement_ids ):

        self .cleanup_expired_announcements ()
        active =self .get_active_announcements ()
        return len ([a for a in active if a ['id']not in viewed_announcement_ids ])

    def get_announcement_ids (self ):

        return [a ['id']for a in self .get_active_announcements ()]
