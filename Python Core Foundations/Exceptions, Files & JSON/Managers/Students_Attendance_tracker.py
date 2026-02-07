import json 
import os 
from .students_record_manager import RecordManager 

class Data_Records :
    def __init__ (self ,name ,department ):
        self .name =name 
        self .department =department 
        self ._attendance_records ={}

    def add_attendance (self ,date ,status ):
        self ._attendance_records [date ]=status 

    def get_all_dates (self ):
        return sorted (self ._attendance_records .keys ())

    def __str__ (self ):
        return f"{self .name } - Department: {self .department }"

    def calculate_annual_percentage (self ):
        if not self ._attendance_records :
            return 0 
        total_days =len (self ._attendance_records )
        present_days =sum (1 for s in self ._attendance_records .values ()if s =='P')
        return 0 if total_days ==0 else (present_days /total_days )*100 

class Student (Data_Records ):
    def __init__ (self ,name ,department ,course =None ,assigned_teacher =None ):
        super ().__init__ (name ,department )
        self .course =course 
        self .assigned_teacher =assigned_teacher 
        self .marks ={}

    def add_mark (self ,subject ,score ):
        self .marks [subject ]=score 

    def calculate_average_marks (self ):
        if not self .marks :
            return 0 
        return sum (self .marks .values ())/len (self .marks )

    def calculate_performance (self ):
        avg =self .calculate_average_marks ()
        if avg >=90 :return "Outstanding"
        elif avg >=75 :return "Excellent"
        elif avg >=50 :return "Good"
        else :return "Needs Improvement"

class GradeStudent (Student ):
    def __init__ (self ,name ,department ,course =None ,assigned_teacher =None ):
        super ().__init__ (name ,department ,course ,assigned_teacher )

    def add_mark (self ,subject ,score ):
        if not (0 <=score <=100 ):
            print (f"Error: Marks for {subject } must be between 0 and 100.")
            return False 
        super ().add_mark (subject ,score )
        return True 

    def calculate_average_marks (self ):
        if not self .marks :
            return 0.0 
        avg =sum (self .marks .values ())/len (self .marks )
        return float (f"{avg :.2f}")

class Teacher (Student ):
    def __init__ (self ,name ,department ,manager =None ,record_manager =None ):
        super ().__init__ (name ,department ,course ="Faculty")
        self .manager =manager 
        self ._record_manager =record_manager 
        self ._assigned_students_objects =[]

    def assign_student (self ,student ):
        if student not in self ._assigned_students_objects :
            self ._assigned_students_objects .append (student )

    def calculate_performance (self ):
        if not self ._assigned_students_objects :
            return "No Students Assigned"

        total_student_avg =sum (s .calculate_average_marks ()for s in self ._assigned_students_objects )
        class_average =total_student_avg /len (self ._assigned_students_objects )

        if class_average >=85 :return "Gold Standard Teacher"
        elif class_average >=70 :return "Silver Standard Teacher"
        elif class_average >=50 :return "Bronze Standard Teacher"
        else :return "Under Review"

    def set_record_manager (self ,record_manager ):
        self ._record_manager =record_manager 

    def view_own_attendance (self ):
        if not self .manager :
             print ("Manager not attached.")
             return 

        print (f"\n--- My Attendance ({self .name }) ---")
        if not self ._attendance_records :
            print ("No attendance records found.")
        else :
             for date in sorted (self ._attendance_records .keys ()):
                 print (f"Date: {date } | Status: {self ._attendance_records [date ]}")

             per =self .calculate_annual_percentage ()
             print (f"Overall Percentage: {per :.2f}%")

    def add_record (self ):
        name =input ("Enter student's name to add attendance: ")
        dept =input ("Enter student's department: ").capitalize ()
        date =input ("Enter date (YYYY-MM-DD): ")

        if not self .manager :
            print ("Manager not attached.")
            return 

        if self .manager .get_student (name )is None :
            print (f"Student {name } not found. Teachers cannot register new students. Please contact Principal.")
            return 

        student =self .manager .get_student (name )
        if date in student ._attendance_records :
            print (f"Attendance for {name } on {date } already exists. Use update option to modify.")
            return 

        while True :
            status =self .get_status_input ()
            if status =='Invalid':
                print ("Invalid input. Please enter 'Present' or 'Absent'.")
            else :
                self .manager .add_attendance (name ,date ,status )
                print (f"Attendance for {name } in department {dept } on {date }  recorded as {status }.")
                break 

    def update_record (self ):
        name =input ("Enter student's name to update attendance: ")

        if not self .manager :
            print ("Manager not attached.")
            return 

        student =self .manager .get_student (name )

        if not student :
            print (f"No records found for {name }.")
            return 

        dates =student .get_all_dates ()
        if not dates :
            print (f"No attendance records found for {name }.")
            return 

        last_date =dates [-1 ]
        current_status =student ._attendance_records [last_date ]
        print (f"Updating last record for {name } on {last_date }  (Current status: {current_status })")

        while True :
            status =self .get_status_input ()
            if status =='Invalid':
                print ("Invalid input. Please enter 'Present' or 'Absent'.")
            else :
                self .manager .update_last_attendance (name ,status )
                print (f"Attendance for {name } on {last_date } updated to {status }.")
                break 

    def admin_view (self ):
        if not self .manager or not self .manager .get_all_students ():
            print ("No attendance records available.")
            return 

        choice =input ("Do you want to view records for:\n1. All students\n2. Specific student\n3. students with Low attendance\nEnter your choice: ").lower ()

        sorted_students =self .manager .get_sorted_students_by_attendance ()

        match choice :
            case '1':
                self .view_all_students (sorted_students )
            case '2':
                print("\nAvailable Students:")
                if self.manager:
                    for s in self.manager.get_all_students(): print(f"- {s}")
                name =input ("\nEnter student's name to view attendance: ")
                self .view_specific_student (name )
            case '3':
                self .view_low_attendance_students (sorted_students )
            case _ :
                print ("Invalid choice.")

    def view_all_students (self ,sorted_students ):
        for _ ,student in sorted_students :
            self .print_student_details (student )

    def view_specific_student (self ,name ):
        if not self .manager :return 

        student =self .manager .get_student (name )
        if not student :
            print (f"No records found for {name }.")
            return 

        choice =input ("Do you want to view all dates or a specific range? (all/specific): ").lower ()

        match choice :
            case "all":
                self .print_student_details (student )
            case "specific":
                start_date =input ("Enter start date (YYYY-MM-DD): ")
                end_date =input ("Enter end date (YYYY-MM-DD): ")
                self .print_student_details (student ,start_date ,end_date )
            case _ :
                print ("Invalid choice.")

    def view_low_attendance_students (self ,sorted_students ):
        print ("\nstudents with attendance below 75%:")
        found =False 
        for _ ,student in sorted_students :
            percentage =student .calculate_annual_percentage ()
            if percentage <=75 :
                found =True 
                self .print_student_details (student )

        if not found :
            print ("No students with low attendance.")

    def print_student_details (self ,student ,start_date =None ,end_date =None ):
        print (f"\nAttendance records for {student .name }:")

        for date in student .get_all_dates ():
            if start_date and end_date and not (start_date <=date <=end_date ):
                continue 

            status =student ._attendance_records [date ]
            print (f"  Date: {date },Status: {status }")

        print (f"  Department: {student .department }")

        annual_percentage =student .calculate_annual_percentage ()

        print (f"  Annual Attendance %: {annual_percentage :.2f}%")
        if annual_percentage <=75 :
            print (f"  Warning: {student .name }'s attendance is below 75%!")

    def get_status_input (self ):
        status =input ("Enter attendance status (Present/Absent): ")
        if status .lower ()in ['present','p']:
            return 'P'
        elif status .lower ()in ['absent','a']:
            return 'A'
        else :
            return 'Invalid'

class AttendanceManager :
    def __init__ (self ):
        self ._storage_file =os .path .join (os .path .dirname (__file__ ),"..","Data","attendance.json")
        self ._students ={}
        self ._teachers ={}

        self ._attendance_cache ={}
        self ._load_attendance ()

    def _load_attendance (self ):
        if os .path .exists (self ._storage_file ):
            try :
                with open (self ._storage_file ,"r")as f :
                    self ._attendance_cache =json .load (f )
            except Exception :
                self ._attendance_cache ={}
            self ._attendance_cache ={}

    def _save_attendance (self ):

        data ={}

        for name ,s in self ._students .items ():
            data [name ]=s ._attendance_records 

        for name ,t in self ._teachers .items ():
            data [name ]=t ._attendance_records 

        with open (self ._storage_file ,"w")as f :
            json .dump (data ,f ,indent =2 )

    def _apply_cached_attendance (self ,person ):
        if person .name in self ._attendance_cache :
            person ._attendance_records =self ._attendance_cache [person .name ]

    def add_student (self ,name ,department ,course ="General",assigned_teacher =None ,student_type ="Regular"):
        name =name .capitalize ()
        if name in self ._students :
            return False 

        if student_type =="GradeStudent":
             s =GradeStudent (name ,department ,course ,assigned_teacher )
        else :
             s =Student (name ,department ,course ,assigned_teacher )

        self ._apply_cached_attendance (s )
        self ._students [name ]=s 
        return True 

    def register_teacher (self ,name ,department ):
        name =name .capitalize ()
        if name in self ._teachers :
            return False 
        t =Teacher (name ,department )
        self ._apply_cached_attendance (t )
        self ._teachers [name ]=t 
        return True 

    def get_student (self ,name ):
        if name is None :return None 
        name =name .capitalize ()
        return self ._students .get (name )

    def get_teacher (self ,name ):
        if name is None :return None 
        name =name .capitalize ()
        return self ._teachers .get (name )

    def get_person (self ,name ):
        s =self .get_student (name )
        if s :return s 
        return self .get_teacher (name )

    def add_attendance (self ,name ,date ,status ):
        person =self .get_person (name )
        if not person :
            return False 
        if date in person ._attendance_records :
            return False 

        person .add_attendance (date ,status )
        self ._save_attendance ()
        return True 

    def update_last_attendance (self ,name ,status ):
        person =self .get_person (name )
        if not person or not person ._attendance_records :
            return False ,None 
        last_date =max (person .get_all_dates ())
        person .add_attendance (last_date ,status )
        self ._save_attendance ()
        return True ,last_date 

    def get_all_students (self ):
        return self ._students 

    def get_all_teachers (self ):
        return self ._teachers 

    def get_sorted_students_by_attendance (self ):
        return sorted (
        self ._students .items (),
        key =lambda x :x [1 ].calculate_annual_percentage (),
        reverse =True ,
        )

class Principal (Teacher ):
    def __init__ (self ,manager ,record_manager =None ):
        super ().__init__ ("Principal","Administration",manager =manager ,record_manager =record_manager )

    def add_record (self ):
        target_type =input ("Add attendance for (1) Student or (2) Teacher? ").strip ()

        if target_type =='1':
             name =input ("Enter student's name to add attendance: ")
             dept =input ("Enter student's department: ").capitalize ()

             if self .manager .get_student (name )is None :
                self .manager .add_student (name ,dept )
        elif target_type =='2':
             name =input ("Enter teacher's name to add attendance: ")
             dept =input ("Enter teacher's department: ").capitalize ()

             if self .manager .get_teacher (name )is None :
                 if not self .manager .register_teacher (name ,dept ):
                     print ("Failed to register teacher.")
                     return 
        else :
             print ("Invalid choice.")
             return 

        date =input ("Enter date (YYYY-MM-DD): ")

        person =self .manager .get_person (name )
        if date in person ._attendance_records :
            print (f"Attendance for {name } on {date } already exists. Use update option to modify.")
            return 

        while True :
            status =self .get_status_input ()
            if status =='Invalid':
                print ("Invalid input. Please enter 'Present' or 'Absent'.")
            else :
                self .manager .add_attendance (name ,date ,status )
                print (f"Attendance for {name } ({'Teacher'if target_type =='2'else 'Student'}) on {date } recorded as {status }.")
                break 

    def view_teacher_attendance (self ):
        teachers =self .manager .get_all_teachers ()
        if not teachers :
            print ("No teacher records found.")
            return 

        print ("\n--- Teacher Attendance ---")
        choice =input ("View (1) All Teachers or (2) Specific Teacher? ")

        if choice =='1':
            for name ,teacher in teachers .items ():
                print (f"\nTeacher: {name } | Dept: {teacher .department }")
                per =teacher .calculate_annual_percentage ()
                print (f"Attendance: {per :.2f}%")
        elif choice =='2':
            name =input ("Enter teacher name: ")
            teacher =self .manager .get_teacher (name )
            if teacher :
                self .print_student_details (teacher )
            else :
                print ("Teacher not found.")
        else :
            print ("Invalid choice.")

def main ():
    manager =AttendanceManager ()
    principal =Principal (manager )
    record_manager =RecordManager ()

    while True :
        authority =input ("\nEnter your role (Principal/Teacher/Student/Exit): ").capitalize ()
        match authority :
            case "Principal":
                while True :
                    action =input ("\nWhat do you want to do?\n 1. Add attendance record\n 2. View attendance record\n 3. Update Record (Last record only)\n 4. View Teacher Attendance\n 5. Exit\n Enter your action: ")
                    match action :
                        case '1':
                            principal .add_record ()
                        case '2':
                            principal .admin_view ()
                        case '3':
                            principal .update_record ()
                        case '4':
                            principal .view_teacher_attendance ()
                        case '5':
                            print ("Exiting Principal mode.")
                            break 
                        case _ :
                            print ("Invalid action. Please try again.")
            case "Teacher":
                teacher =Teacher ("Teacher","General",manager )
                while True :
                    action =input ("\nWhat do you want to do?\n 1. Add attendance record (Student)\n 2. View attendance record (Students)\n 3. Update Record (Student - Last only)\n 4. View My Attendance\n 5. Exit\n Enter your action: ")
                    match action :
                        case '1':
                            teacher .add_record ()
                        case '2':
                            teacher .admin_view ()
                        case '3':
                            teacher .update_record ()
                        case '4':
                            teacher .view_own_attendance ()
                        case '5':
                            print ("Exiting Teacher mode.")
                            break 
                        case _ :
                            print ("Invalid action. Please try again.")
            case "Student":
                print ("\n --- Student Record Management ---")
                while True :
                    action =input ("\nWhat do you want to do?\n 1. Add attendance record\n 2. View attendance record\n 3. Update Record (Last record only)\n 4. Exit\n Enter your action: ")
                    match action :
                        case '1':
                            try :
                                record_manager .create_record_interactive ()
                            except Exception as e :
                                print (f"Error: {e }")
                        case '2':
                            record_manager .display_record ()
                        case '3':
                            try :
                                record_manager .update_record ()
                            except Exception as e :
                                print (f"Error: {e }")
                        case '4':
                            print ("Exiting Student mode.")
                            break 
                        case _ :
                            print ("Invalid action. Please try again.")
            case "Exit":
                print ("Exiting program.")
                break 
            case _ :
                print ("Invalid role. Please try again.")

if __name__ =="__main__":
    main ()
