import json 
import os 
import sys 

sys .path .append (os .path .abspath (os .path .join (os .path .dirname (__file__ ),'..')))

from Exceptions .custom_exceptions import RecordExistsError ,RecordNotFoundError ,InvalidInputError 

class StudentRecord :
    def __init__ (self ,name :str ,course :str ,age :int ,grade :str ,marks :dict =None ,assigned_teacher :str =None ):
        self .name =name 
        self .course =course 
        self .age =age 
        self .grade =grade 
        self .marks =marks or {}
        self .assigned_teacher =assigned_teacher 

    def to_dict (self ):
        return {
        "name":self .name ,
        "course":self .course ,
        "age":self .age ,
        "grade":self .grade ,
        "marks":self .marks ,
        "assigned_teacher":self .assigned_teacher 
        }

    @classmethod 
    def from_dict (cls ,d ):
        return cls (d ["name"],d ["course"],d ["age"],d ["grade"],d .get ("marks",{}),d .get ("assigned_teacher"))

class TeacherRecord :
    def __init__ (self ,name :str ,department :str ,assigned_students :list =None ):
        self .name =name 
        self .department =department 
        self .assigned_students =assigned_students or []

    def to_dict (self ):
        return {
        "name":self .name ,
        "department":self .department ,
        "assigned_students":self .assigned_students 
        }

    @classmethod 
    def from_dict (cls ,d ):
        return cls (d ["name"],d ["department"],d .get ("assigned_students",[]))

from abc import ABC ,abstractmethod 

class RecordManagerABC (ABC ):
    @abstractmethod 
    def create_record (self ,*args ,**kwargs ):
        pass 

    @abstractmethod 
    def display_record (self ):
        pass 

    @abstractmethod 
    def update_record (self ,*args ,**kwargs ):
        pass 

    @abstractmethod 
    def delete_record (self ,*args ,**kwargs ):
        pass 

class RecordManager (RecordManagerABC ):
    def __init__ (self ):
        self ._storage_file =os .path .join (os .path .dirname (__file__ ),"..","Data","students_records.json")
        self ._teacher_storage_file =os .path .join (os .path .dirname (__file__ ),"..","Data","teachers_records.json")
        self ._records ={}
        self ._teacher_records ={}
        self ._load ()
        self ._load_teachers ()

    def _load (self ):
        if os .path .exists (self ._storage_file ):
            try :
                with open (self ._storage_file ,"r")as f :
                    self ._records =json .load (f )
            except Exception :
                self ._records ={}

    def _load_teachers (self ):
        if os .path .exists (self ._teacher_storage_file ):
            try :
                with open (self ._teacher_storage_file ,"r")as f :
                    self ._teacher_records =json .load (f )
            except Exception :
                self ._teacher_records ={}

    def _save (self ):
        with open (self ._storage_file ,"w")as f :
            json .dump (self ._records ,f ,indent =2 )

    def _save_teachers (self ):
        with open (self ._teacher_storage_file ,"w")as f :
            json .dump (self ._teacher_records ,f ,indent =2 )

    def _generate_id (self ,records ):
        if not records :
            return 1 
        ids =sorted (int (k )for k in records .keys ())
        return ids [-1 ]+1 

    def create_record (self ,name ,age ,grade ,course ,assigned_teacher =None ,student_type ="Regular"):
        name =name .strip ().capitalize ()

        for sid ,details in self ._records .items ():
            if details ["name"]==name :
                raise RecordExistsError (f"Record already exists for {name } with ID {sid }.")

        try :
            age =int (age )
        except ValueError :
            raise InvalidInputError ("Invalid numeric input for age.")

        id_num =self ._generate_id (self ._records )

        rec =StudentRecord (name ,course ,int (age ),grade ,assigned_teacher =assigned_teacher )
        rec_dict =rec .to_dict ()
        rec_dict ["student_type"]=student_type 
        self ._records [str (id_num )]=rec_dict 
        self ._save ()
        return id_num 

    def create_teacher_record (self ,name ,department ):
        name =name .strip ().capitalize ()
        for tid ,details in self ._teacher_records .items ():
            if details ["name"]==name :
                raise RecordExistsError (f"Teacher record already exists for {name }.")

        id_num =self ._generate_id (self ._teacher_records )
        rec =TeacherRecord (name ,department )
        self ._teacher_records [str (id_num )]=rec .to_dict ()
        self ._save_teachers ()
        return id_num 

    def get_teacher_by_name (self ,name ):
        name =name .strip ().capitalize ()
        for tid ,details in self ._teacher_records .items ():
            if details ["name"]==name :
                return TeacherRecord .from_dict (details )
        return None 

    def list_teachers (self ):
        return {k :TeacherRecord .from_dict (v )for k ,v in self ._teacher_records .items ()}

    def assign_student_to_teacher (self ,student_name ,teacher_name ):

        student_name =student_name .strip ().capitalize ()
        teacher_name =teacher_name .strip ().capitalize ()

        student_found =False 
        student_id =None 
        for sid ,details in self ._records .items ():
            if details ["name"]==student_name :
                student_found =True 
                student_id =sid 
                break 

        if not student_found :
            return False ,"Student not found"

        teacher_found =False 
        teacher_id =None 
        for tid ,details in self ._teacher_records .items ():
            if details ["name"]==teacher_name :
                teacher_found =True 
                teacher_id =tid 
                break 

        if not teacher_found :
            return False ,"Teacher not found"

        self ._records [student_id ]["assigned_teacher"]=teacher_name 

        if "assigned_students"not in self ._teacher_records [teacher_id ]:
            self ._teacher_records [teacher_id ]["assigned_students"]=[]
        if student_name not in self ._teacher_records [teacher_id ]["assigned_students"]:
            self ._teacher_records [teacher_id ]["assigned_students"].append (student_name )

        self ._save ()
        self ._save_teachers ()
        return True ,"Success"

    def change_student_teacher (self ,student_name ,new_teacher_name ):

        student_name =student_name .strip ().capitalize ()
        new_teacher_name =new_teacher_name .strip ().capitalize ()

        student_found =False 
        student_id =None 
        old_teacher =None 
        for sid ,details in self ._records .items ():
            if details ["name"]==student_name :
                student_found =True 
                student_id =sid 
                old_teacher =details .get ("assigned_teacher")
                break 

        if not student_found :
            return False ,"Student not found"

        new_teacher_found =False 
        new_teacher_id =None 
        for tid ,details in self ._teacher_records .items ():
            if details ["name"]==new_teacher_name :
                new_teacher_found =True 
                new_teacher_id =tid 
                break 

        if not new_teacher_found :
            return False ,"New teacher not found"

        if old_teacher :
            for tid ,details in self ._teacher_records .items ():
                if details ["name"]==old_teacher :
                    if "assigned_students"in self ._teacher_records [tid ]:
                        if student_name in self ._teacher_records [tid ]["assigned_students"]:
                            self ._teacher_records [tid ]["assigned_students"].remove (student_name )
                    break 

        if "assigned_students"not in self ._teacher_records [new_teacher_id ]:
            self ._teacher_records [new_teacher_id ]["assigned_students"]=[]
        if student_name not in self ._teacher_records [new_teacher_id ]["assigned_students"]:
            self ._teacher_records [new_teacher_id ]["assigned_students"].append (student_name )

        self ._records [student_id ]["assigned_teacher"]=new_teacher_name 

        self ._save ()
        self ._save_teachers ()
        return True ,f"Changed from {old_teacher or 'None'} to {new_teacher_name }"

    def add_student_mark (self ,name ,subject ,score ):
        name =name .capitalize ()
        for sid ,details in self ._records .items ():
            if details ["name"]==name :
                marks =self ._records [sid ].get ("marks",{})
                marks [subject ]=float (score )
                self ._records [sid ]["marks"]=marks 
                self ._save ()
                return True 
        return False 

    def create_record_interactive (self ):
        name =input ("Enter student name: ").strip ().capitalize ()
        try :
            age =int (input ("Enter age: "))
            grade =input ("Enter grade: ").strip ().upper ()
            course =input ("Enter course enrolled: ").strip ().upper ()
            teacher =input ("Enter assigned teacher name (optional): ").strip ().capitalize ()
            teacher =teacher if teacher else None 
            return self .create_record (name ,age ,grade ,course ,assigned_teacher =teacher )
        except ValueError :
            raise InvalidInputError ("Invalid numeric input for age.")

    def list_records (self ):
        return {int (k ):StudentRecord .from_dict (v )for k ,v in self ._records .items ()}

    def display_record (self ):
        if not self ._records :
            print ("No records available.")
            return 
        choice =input ("Do you want to view all records, a specific student, or 'Teacher' records? (all/specific/teacher): ").lower ()
        if choice =="all":
            print ("\nAll Student Records:")
            for id_num ,details in sorted (self ._records .items (),key =lambda x :int (x [0 ])):
                teacher_info =f", Teacher: {details .get ('assigned_teacher','None')}"
                marks_info =f", Marks: {details .get ('marks',{})}"
                print (f"ID: {id_num }, Name: {details ['name']}, Age: {details ['age']}, Grade: {details ['grade']}, Course: {details ['course']}{teacher_info }{marks_info }")
        elif choice =="specific":
            try :
                id_num =str (int (input ("Enter student ID to view details: ")))
            except ValueError :
                print ("Invalid ID input.")
                return 
            if id_num not in self ._records :
                print ("No records found for the student.")
                return 
            details =self ._records [id_num ]
            teacher_info =f", Teacher: {details .get ('assigned_teacher','None')}"
            marks_info =f", Marks: {details .get ('marks',{})}"
            print (f"\nStudent Record: ID: {id_num }, Name: {details ['name']}, Age: {details ['age']}, Grade: {details ['grade']}, Course: {details ['course']}{teacher_info }{marks_info }")
        elif choice =="teacher":
            print ("\nAll Teacher Records:")
            if not self ._teacher_records :
                print ("No teacher records found.")
            else :
                for id_num ,details in sorted (self ._teacher_records .items (),key =lambda x :int (x [0 ])):
                    print (f"\nTeacher ID: {id_num }, Name: {details ['name']}, Department: {details ['department']}")
                    assigned_students =details .get ('assigned_students',[])
                    if assigned_students :
                        print (f"  Assigned Students ({len (assigned_students )}):")
                        for student_name in assigned_students :

                            for sid ,sdetails in self ._records .items ():
                                if sdetails ['name']==student_name :
                                    marks_info =f", Marks: {sdetails .get ('marks',{})}"
                                    print (f"    - {sdetails ['name']} (Age: {sdetails ['age']}, Grade: {sdetails ['grade']}, Course: {sdetails ['course']}{marks_info })")
                                    break 
                            else :
                                print (f"    - {student_name } (Details not found)")
                    else :
                        print ("  No assigned students")
                    print ("-"*60 )
        else :
            print ("Invalid choice.")

    def update_record (self ,id_num =None ):
        try :
            if id_num is None :
                id_num =str (int (input ("Enter student ID to update details: ")))
            else :
                id_num =str (int (id_num ))
        except ValueError :
            raise InvalidInputError ("Invalid ID input.")

        if id_num not in self ._records :
            raise RecordNotFoundError ("No records found for the student.")

        choice =input ("What do you want to update? (age/grade/course/teacher): ").lower ()
        if choice =="age":
            try :
                self ._records [id_num ]["age"]=int (input ("Enter new age: "))
            except ValueError :
                raise InvalidInputError ("Invalid age input.")
        elif choice =="grade":
            self ._records [id_num ]["grade"]=input ("Enter new grade: ").upper ()
        elif choice =="course":
            self ._records [id_num ]["course"]=input ("Enter new course: ").upper ()
        elif choice =="teacher":
            self ._records [id_num ]["assigned_teacher"]=input ("Enter new teacher name: ").capitalize ()
        else :
            raise InvalidInputError ("Unknown field to update.")

        self ._save ()
        return True 

    def delete_record (self ,id_num =None ):
        try :
            if id_num is None :
                id_num =str (int (input ("Enter student ID to delete details: ")))
            else :
                id_num =str (int (id_num ))
        except ValueError :
            raise InvalidInputError ("Invalid ID input.")

        if id_num not in self ._records :
            raise RecordNotFoundError ("No records found for the student.")

        del self ._records [id_num ]
        self ._save ()
        return True 

def main ():
    manager =RecordManager ()
    while True :
        action =input ("Choose action:\n 1.Add a record\n 2.View a record\n 3.Update a record\n 4.Delete a record\n 5.Exit\nEnter your choice: ").lower ()
        match action :
            case "1"|"add":
                try :
                    sid =manager .create_record_interactive ()
                    print (f"Record created with ID: {sid }")
                except Exception as e :
                    print (e )
            case "2"|"view":
                manager .display_record ()
            case "3"|"update":
                try :
                    manager .update_record ()
                except Exception as e :
                    print (e )
            case "4"|"delete":
                try :
                    manager .delete_record ()
                except Exception as e :
                    print (e )
            case "5"|"exit":
                print ("Exiting Student Record Manager. Goodbye!")
                break 
            case _ :
                print ("Invalid action. Please try again.")
