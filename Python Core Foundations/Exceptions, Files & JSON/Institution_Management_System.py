from Managers import Students_Attendance_tracker 
from Managers import students_record_manager 
from Managers import announcements_manager 
from Managers import query_manager 
from Managers import user_manager 

from Exceptions import custom_exceptions 

try :
    import pwinput 
except ImportError :
    pwinput =None 

from Managers import leave_module 
from Managers import notification_manager

import os

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')
 

class PrincipalUI (Students_Attendance_tracker .Principal ):

    def __init__ (self ,attendance_manager ,record_manager ,usr_manager ):

        super ().__init__ (attendance_manager ,record_manager )
        self ._record_manager =record_manager 
        self ._user_manager =usr_manager 

    def view_student_db (self ):

        if not self ._record_manager :
            print ("No record manager attached.")
            return 
        self ._record_manager .display_record ()

    def register_new_student (self ,name =None ):

        if name is None :
            name =input ("Enter student name: ").strip ().capitalize ()
        else :
            name =name .strip ().capitalize ()

        print (f"Registering new student: {name }")
        try :

            print ("Create Login Credentials:")
            username =input ("Username: ").strip ()

            if self ._user_manager .user_exists (username ):
                print ("Username already taken.")
                return None 

            if pwinput :
                 password =pwinput .pwinput (prompt ="Password: ").strip ()
            else :
                 password =input ("Password: ").strip ()

            age =int (input ("Enter age: "))
            grade =input ("Enter grade: ").strip ().upper ()
            course =input ("Enter Course/Department: ").strip ().upper ()

            student_type =input ("Student Type (1: Regular, 2: GradeStudent): ").strip ()
            student_type ="GradeStudent"if student_type =='2'else "Regular"

            all_teachers =self ._record_manager .list_teachers ()

            available_teachers =[t .name for t in all_teachers .values ()if t .department .lower ()==course .lower ()]

            if not available_teachers :
                print (f"No teachers found for course '{course }'. First teacher record should be added.")
                return None 

            print (f"Teachers available for {course }: {', '.join (available_teachers )}")
            while True :
                teacher =input ("Enter assigned teacher name: ").strip ().capitalize ()
                if teacher in available_teachers :
                    break 
                print (f"Invalid teacher. Please choose from: {', '.join (available_teachers )}")

            sid =self ._record_manager .create_record (name ,age ,grade ,course ,assigned_teacher =teacher ,student_type =student_type )

            self ._user_manager .add_user (username ,password ,"Student",name )
            print (f"Record created with ID: {sid } and User created.")

            if self .manager .add_student (name ,course ,course ,teacher ,student_type =student_type ):
                print (f"Added {name } to Attendance System.")
            else :
                print (f"{name } already exists in Attendance System.")

            success ,message =self ._record_manager .assign_student_to_teacher (name ,teacher )
            if success :
                print (f"✓ Assigned {name } to teacher {teacher }")
            else :
                print (f"Warning: Could not assign to teacher: {message }")

            teacher_obj =self .manager .get_teacher (teacher )
            student_obj =self .manager .get_student (name )
            if teacher_obj and student_obj :
                if student_obj not in teacher_obj ._assigned_students_objects :
                    teacher_obj ._assigned_students_objects .append (student_obj )
                    print (f"✓ Synchronized in-memory teacher assignment")

            return name 

        except (custom_exceptions .RecordExistsError ,custom_exceptions .InvalidInputError ,ValueError )as e :

            print (f"Error registering student: {e }")
            return None 

    def register_new_teacher (self ):

        name =input ("Enter teacher name: ").strip ().capitalize ()
        try :

            print ("Create Login Credentials:")
            username =input ("Username: ").strip ()

            if self ._user_manager .user_exists (username ):
                print ("Username already taken.")
                return 

            if pwinput :
                 password =pwinput .pwinput (prompt ="Password:").strip ()
            else :
                 password =input ("Password: ").strip ()

            dept =input ("Enter department: ").strip ().upper ()

            tid =self ._record_manager .create_teacher_record (name ,dept )

            self ._user_manager .add_user (username ,password ,"Teacher",name )
            print (f"Teacher record created with ID: {tid } and User created.")

            self .manager .register_teacher (name ,dept )
            print (f"Teacher {name } registered in system.")
        except Exception as e :

            print (f"Error registering teacher: {e }")

    def assign_student_to_teacher (self ):
        print("\n--- Assign Student to Teacher ---")
        print("Available Students:")
        for s in self._record_manager.list_records().values(): print(f"- {s.name} (Course: {s.course})")
        print("\nAvailable Teachers:")
        for t in self._record_manager.list_teachers().values(): print(f"- {t.name} (Dept: {t.department})")
        
        student_name =input ("\nEnter student name: ").strip ().capitalize ()
        teacher_name =input ("Enter teacher name: ").strip ().capitalize ()

        success ,message =self ._record_manager .assign_student_to_teacher (student_name ,teacher_name )
        if success :
            print (f"Assigned {student_name } to {teacher_name }.")
            t =self .manager .get_teacher (teacher_name )
            s =self .manager .get_student (student_name )
            if t and s :
                 t .assign_student (s )
                 s .assigned_teacher =teacher_name 
        else :
             print (f"Assignment failed: {message }. Please check if names are correct.")

    def change_assigned_teacher (self ):
        print("\n--- Change Assigned Teacher ---")
        print("Available Students:")
        for s in self._record_manager.list_records().values(): print(f"- {s.name} (Current: {s.assigned_teacher})")
        print("\nAvailable Teachers:")
        for t in self._record_manager.list_teachers().values(): print(f"- {t.name}")

        student_name =input ("\nEnter student name: ").strip ().capitalize ()
        new_teacher_name =input ("Enter new teacher name: ").strip ().capitalize ()

        success ,message =self ._record_manager .change_student_teacher (student_name ,new_teacher_name )
        if success :
            print (f"Successfully changed teacher assignment. {message }")

            s =self .manager .get_student (student_name )
            new_t =self .manager .get_teacher (new_teacher_name )
            if s and new_t :
                s .assigned_teacher =new_teacher_name 
                new_t .assign_student (s )
        else :
            print (f"Failed to change teacher: {message }")

    def view_teacher_performance (self ):
        teachers =self .manager .get_all_teachers ()
        if not teachers :
            print ("No teachers found.")
            return 
        print ("\nTeacher Performance Evaluation:")
        for name ,teacher_obj in teachers .items ():
             perf =teacher_obj .calculate_performance ()
             print (f"Teacher: {name }, Performance: {perf }")

    def add_student_record (self ):
        if not self ._record_manager :
            print ("No record manager attached.")
            return 
        self .register_new_student ()

    def update_student_record (self ):

        if not self ._record_manager :
            print ("No record manager attached.")
            return 

        try :

            records=self._record_manager._records
            print("\nAvailable Students:")
            for sid, data in records.items(): print(f"ID: {sid} | Name: {data['name']}")
            id_num =str (int (input ("\nEnter student ID to update details: ")))

            records =self ._record_manager ._records 
            if id_num not in records :
                raise custom_exceptions .RecordNotFoundError ("No records found for the student.")

            student_data =records [id_num ]
            student_name =student_data ["name"]
            old_teacher =student_data .get ("assigned_teacher")

            choice =input ("What do you want to update? (age/grade/course/teacher): ").lower ()

            if choice =="teacher":

                new_teacher =input ("Enter new teacher name: ").strip ().capitalize ()

                teacher_records =self ._record_manager ._teacher_records 
                teacher_found =False 
                for tid ,tdata in teacher_records .items ():
                    if tdata ["name"]==new_teacher :
                        teacher_found =True 
                        break 

                if not teacher_found :
                    print (f"Teacher '{new_teacher }' not found in system.")
                    return 

                records [id_num ]["assigned_teacher"]=new_teacher 

                if old_teacher :
                    for tid ,tdata in teacher_records .items ():
                        if tdata ["name"]==old_teacher :
                            if "assigned_students"in tdata :
                                if student_name in tdata ["assigned_students"]:
                                    tdata ["assigned_students"].remove (student_name )
                            break 

                for tid ,tdata in teacher_records .items ():
                    if tdata ["name"]==new_teacher :
                        if "assigned_students"not in tdata :
                            tdata ["assigned_students"]=[]
                        if student_name not in tdata ["assigned_students"]:
                            tdata ["assigned_students"].append (student_name )
                        break 

                self ._record_manager ._save ()
                self ._record_manager ._save_teachers ()

                student_obj =self .manager .get_student (student_name )
                new_teacher_obj =self .manager .get_teacher (new_teacher )

                if student_obj and new_teacher_obj :

                    if old_teacher :
                        old_teacher_obj =self .manager .get_teacher (old_teacher )
                        if old_teacher_obj and student_obj in old_teacher_obj ._assigned_students_objects :
                            old_teacher_obj ._assigned_students_objects .remove (student_obj )

                    student_obj ._assigned_teacher =new_teacher 

                    if student_obj not in new_teacher_obj ._assigned_students_objects :
                        new_teacher_obj ._assigned_students_objects .append (student_obj )

                print ("Student record updated.")
                print (f"Teacher changed from '{old_teacher or 'None'}' to '{new_teacher }'")
                print ("✓ Synchronized with attendance system")

            else :

                if choice =="age":
                    try :
                        records [id_num ]["age"]=int (input ("Enter new age: "))
                    except ValueError :
                        raise custom_exceptions .InvalidInputError ("Invalid age input.")
                elif choice =="grade":
                    records [id_num ]["grade"]=input ("Enter new grade: ").upper ()
                elif choice =="course":
                    records [id_num ]["course"]=input ("Enter new course: ").upper ()
                else :
                    raise custom_exceptions .InvalidInputError ("Unknown field to update.")

                self ._record_manager ._save ()
                print ("Student record updated.")

        except (custom_exceptions .RecordNotFoundError ,custom_exceptions .InvalidInputError ,ValueError )as e :
            print (f"Error updating record: {e }")

    def delete_student_record (self ):
        if not self ._record_manager :
            print ("No record manager attached.")
            return 
        try :
            records=self._record_manager._records
            print("\nAvailable Students:")
            for sid, data in records.items(): print(f"ID: {sid} | Name: {data['name']}")
            id_num=str(int(input("\nEnter student ID to delete details: ")))
            self._record_manager.delete_record(id_num)
            print ("Student record deleted.")
        except (custom_exceptions .RecordNotFoundError ,custom_exceptions .InvalidInputError )as e :
            print (f"Error deleting record: {e }")

    def add_record (self ):
        print("\n--- Add Attendance Record ---")
        print("Available Students:")
        for s in self.manager.get_all_students(): print(f"- {s}")
        print("\nAvailable Teachers:")
        for t in self.manager.get_all_teachers(): print(f"- {t}")

        name =input ("\nEnter name: ").strip ().capitalize ()
        person =self .manager .get_person (name )

        if person is None :
            print (f"Person '{name }' not found.")
            choice =input (f"Register '{name }' as new Student? (y/n): ").lower ()
            if choice =='y':
                name =self .register_new_student (name )
                if not name :return 
                person =self .manager .get_person (name )
            else :
                return 

        if not person :return 

        date =input ("Enter date (YYYY-MM-DD): ")
        if date in person ._attendance_records :
            print (f"Attendance for {name } on {date } already exists. Use update option to modify.")
            return 

        while True :
            status =self .get_status_input ()
            if status =='Invalid':
                print ("Invalid input. Please enter 'Present' or 'Absent'.")
            else :
                self .manager .add_attendance (name ,date ,status )
                if hasattr (person ,'course'):
                    print (f"Attendance for {name } ({person .course }) on {date } recorded as {status }.")
                else :
                    print (f"Attendance for {name } on {date } recorded as {status }.")
                break 

    def admin_view (self ):
        choice =input ("View attendance for:\n1. All Students\n2. Specific Person (Student/Teacher)\n3. All Teachers\nChoice: ").lower ()
        match choice :
            case '1':
                students =self .manager .get_sorted_students_by_attendance ()
                self .view_all_students (students )
            case '2':
                print("\nAvailable Persons:")
                for s in self.manager.get_all_students(): print(f"- {s} (Student)")
                for t in self.manager.get_all_teachers(): print(f"- {t} (Teacher)")
                name =input ("\nEnter name: ")
                person =self .manager .get_person (name )
                if person :
                    self .print_student_details (person )
                else :
                    print ("Not found.")
            case '3':
                teachers =self .manager .get_all_teachers ()
                for t in teachers .values ():
                    self .print_student_details (t )
            case _ :
                print ("Invalid.")

class TeacherUI (Students_Attendance_tracker .Teacher ):
    def __init__ (self ,attendance_manager ,record_manager ):
        super ().__init__ ("Guest","Staff",manager =attendance_manager ,record_manager =record_manager )
        self .current_teacher_name =None 

    def set_user (self ,name ):
        self .current_teacher_name =name 
        if not self .manager .get_teacher (name ):
             rec =self ._record_manager .get_teacher_by_name (name )
             if rec :
                 self .manager .register_teacher (name ,rec .department )
             else :
                 self .manager .register_teacher (name ,"Staff")

        teacher_obj =self .manager .get_teacher (name )

        rec =self ._record_manager .get_teacher_by_name (name )
        if rec :
            for s_name in rec .assigned_students :
                s_obj =self .manager .get_student (s_name )
                if s_obj :
                    teacher_obj .assign_student (s_obj )

    def view_student_db (self ):
        if not self .current_teacher_name :return 
        teacher_record =self ._record_manager .get_teacher_by_name (self .current_teacher_name )
        if not teacher_record or not teacher_record .assigned_students :
             print ("No assigned students to view.")
             return 

        print (f"\nAssigned Students for {self .current_teacher_name }:")
        for s_name in teacher_record .assigned_students :
            found =False 
            for rid ,details in self ._record_manager .list_records ().items ():
                if details .name ==s_name :
                    print (f"Name: {details .name }, Grade: {details .grade }, Course: {details .course }, Marks: {details .marks }")
                    found =True 
            if not found :
                  print (f"Name: {s_name } (Record details not found)")

    def add_record (self ):
        if not self .current_teacher_name :return 
        t_obj=self.manager.get_teacher(self.current_teacher_name)
        print(f"\n--- Add Attendance for {self.current_teacher_name}'s Students ---")
        if t_obj and t_obj._assigned_students_objects:
            for s in t_obj._assigned_students_objects: print(f"- {s.name}")
        else: print("No students assigned.")

        name =input ("\nEnter student name: ").strip ().capitalize ()

        student =self .manager .get_student (name )
        if student is None :
            print (f"Student '{name }' not found in the system.")
            return 

        teacher_obj =self .manager .get_teacher (self .current_teacher_name )
        is_assigned =any (s .name ==name for s in teacher_obj ._assigned_students_objects )

        if not is_assigned :
             print (f"Access Denied: Student {name } is not assigned to you.")
             return 

        date =input ("Enter date (YYYY-MM-DD): ")
        if date in student ._attendance_records :
            print (f"Attendance for {name } on {date } already exists.")
            return 

        while True :
            status =self .get_status_input ()
            if status =='Invalid':
                print ("Invalid input. Please enter 'Present' or 'Absent'.")
            else :
                self .manager .add_attendance (name ,date ,status )
                print (f"Attendance for {name } recorded as {status }.")
                break 

    def add_marks (self ):
        if not self .current_teacher_name :return 
        t_obj=self.manager.get_teacher(self.current_teacher_name)
        print(f"\n--- Add Marks for {self.current_teacher_name}'s Students ---")
        if t_obj and t_obj._assigned_students_objects:
            for s in t_obj._assigned_students_objects: print(f"- {s.name}")
        else: print("No students assigned.")

        name =input ("\nEnter student name: ").strip ().capitalize ()

        teacher_obj =self .manager .get_teacher (self .current_teacher_name )
        is_assigned =any (s .name ==name for s in teacher_obj ._assigned_students_objects )

        if not is_assigned :
             print (f"Access Denied: Student {name } is not assigned to you.")
             return 

        subject =input ("Enter subject: ")
        try :
             score =float (input ("Enter marks: "))
             if self ._record_manager .add_student_mark (name ,subject ,score ):
                  s =self .manager .get_student (name )
                  if s :s .add_mark (subject ,score )
                  print ("Marks added successfully.")
             else :
                  print ("Failed to add marks. Student record might usually not exist?")
        except ValueError :
             print ("Invalid marks input.")

class StudentManagementSystem :

    def __init__ (self ):

        self ._record_manager =students_record_manager .RecordManager ()
        self ._attendance_manager =Students_Attendance_tracker .AttendanceManager ()
        self ._announcement_manager =announcements_manager .AnnouncementManager ()
        self ._query_manager =query_manager .QueryManager ()
        self ._user_manager =user_manager .UserManager ()
        self ._leave_manager =leave_module .LeaveManager ()
        self ._notification_manager =notification_manager .NotificationManager (self ._attendance_manager ,self ._leave_manager )

        self ._principal =PrincipalUI (self ._attendance_manager ,self ._record_manager ,self ._user_manager )
        self ._principal .leave_manager =self ._leave_manager 
        self ._teacher =TeacherUI (self ._attendance_manager ,self ._record_manager )
        self ._teacher .leave_manager =self ._leave_manager 

        self ._bootstrap_data ()

    def _bootstrap_data (self ):

        records =self ._record_manager .list_records ()
        for rid ,rec in records .items ():

            self ._attendance_manager .add_student (rec .name ,"General",rec .course ,rec .assigned_teacher )

            s =self ._attendance_manager .get_student (rec .name )
            if s and rec .marks :
                 s .marks =rec .marks 

        t_records =self ._record_manager .list_teachers ()
        for tid ,trec in t_records .items ():

            self ._attendance_manager .register_teacher (trec .name ,trec .department )

            t_obj =self ._attendance_manager .get_teacher (trec .name )
            if t_obj :

                 for s_name in trec .assigned_students :
                      s_obj =self ._attendance_manager .get_student (s_name )
                      if s_obj :t_obj .assign_student (s_obj )

    def run (self ):

        print ("Welcome to Student Management System")
        try :
            while True :

                print ("\n--- Login ---")
                username =input ("Username (or 'exit' to quit): ").strip ()

                if username .lower ()=='exit':
                    break 

                if pwinput :
                    password =pwinput .pwinput (prompt ="Password: ").strip ()
                else :
                    password =input ("Password: ").strip ()

                user_data =self ._user_manager .authenticate (username ,password )
                if not user_data :
                    print ("Invalid credentials.")
                    continue 

                role =user_data .get ("role")
                name =user_data .get ("name")
                print (f"\nWelcome, {name } ({role })")

                if role =="Principal":
                    self ._principal_menu ()

                elif role =="Teacher":

                    self ._teacher .set_user (name )

                    alerts =self ._notification_manager .check_uninformed_absences ()
                    if alerts :

                        print ("\n"+"!"*60 )
                        print ("CRITICAL NOTIFICATIONS:")
                        for alert in alerts :
                            print (alert ["message"])
                        print ("!"*60 +"\n")

                        mark_contacted =input ("Have you contacted any of these students? (y/n): ").lower ()
                        if mark_contacted =='y':

                            for alert in alerts :
                                contacted =input (f"Contacted {alert ['student_name']}? (y/n): ").lower ()
                                if contacted =='y':

                                    self ._notification_manager .mark_absence_contacted (alert ["alert_id"])
                                    print (f"Marked {alert ['student_name']} as contacted.")

                        input ("Press Enter to continue...")

                    self ._teacher_menu ()

                elif role =="Student":
                    self ._student_menu (name )
                else :
                    print ("Unknown role.")

        except KeyboardInterrupt :
            print ("\nExiting System. Goodbye!")

    def _principal_menu (self ):
        while True :

            viewed =self ._notification_manager .get_viewed_announcements ("principal")
            unread_count =self ._announcement_manager .get_unread_count (viewed )

            summary =self ._notification_manager .get_notification_summary ("Principal","Principal",self ._query_manager ,self ._leave_manager )

            notif_badge =""
            if unread_count >0 :notif_badge +=f" [Announcements: {unread_count }]"
            if summary ["queries"]>0 :notif_badge +=f" [Queries: {summary ['queries']}]"
            if summary ["leaves"]>0 :notif_badge +=f" [Leaves: {summary ['leaves']}]"

            print ("\n--- Principal Dashboard ---")
            print (f"1. Attendance Management\n2. Student Management\n3. Teacher Management\n4. Communication (Announcements/Queries/Leaves){notif_badge }\n5. Leave Management\n6. Logout")
            choice =input ("Enter choice: ").strip ()
            clear_screen()
            match choice:
                case '1':
                    self ._principal_attendance_menu ()
                case '2':
                    self ._principal_student_menu ()
                case '3':
                    self ._principal_teacher_menu ()
                case '4':
                    self ._principal_comm_menu ()
                case '5':
                    self ._principal_leave_menu ()
                case '6':
                    break 
                case _:
                    print ("Invalid choice.")

    def _principal_attendance_menu (self ):
        while True :
            print ("\n  -- Attendance Management --")
            print ("  1. Add Attendance\n  2. View Attendance\n  3. Update Attendance\n  4. Back")
            action =input ("  Choice: ").strip ()
            clear_screen()
            match action:
                case '1':
                    self ._principal .add_record ()
                case '2':
                    self ._principal .admin_view ()
                case '3':
                    print("\nAvailable students for attendance update:")
                    for s in self._attendance_manager.get_all_students(): print(f"- {s}")
                    name =input ("\nEnter name: ")
                    status =input ("Enter new status (Present/Absent): ")
                    status_norm ='P'if status .lower ()in ['present','p']else ('A'if status .lower ()in ['absent','a']else None )
                    if status_norm :
                        success ,updated_date =self ._attendance_manager .update_last_attendance (name ,status_norm )
                        if success :
                            print (f"Attendance updated for {name } on {updated_date }.")
                        else :
                            print (f"Failed to update attendance for {name }. No records found.")
                    else :
                        print ("Invalid status.")
                case '4':
                    break 
                case _:
                    print ("Invalid action.")

    def _principal_student_menu (self ):
        while True :
            print ("\n  -- Student Management --")
            print ("  1. Register Student\n  2. View Student Database\n  3. Update Student Record\n  4. Delete Student Record\n  5. Assign Teacher\n  6. Change Assigned Teacher\n  7. Back")
            action =input ("  Choice: ").strip ()
            clear_screen()
            match action:
                case '1':
                    self ._principal .register_new_student ()
                case '2':
                    self ._principal .view_student_db ()
                case '3':
                    self ._principal .update_student_record ()
                case '4':
                    self ._principal .delete_student_record ()
                case '5':
                    self ._principal .assign_student_to_teacher ()
                case '6':
                    self ._principal .change_assigned_teacher ()
                case '7':
                    break 
                case _:
                    print ("Invalid action.")

    def _principal_teacher_menu (self ):
        while True :
            print ("\n  -- Teacher Management --")
            print ("  1. Register Teacher\n  2. View Teacher Performance\n  3. Back")
            action =input ("  Choice: ").strip ()
            clear_screen()
            if action =='1':self ._principal .register_new_teacher ()
            elif action =='2':self ._principal .view_teacher_performance ()
            elif action =='3':break 

    def _principal_comm_menu (self ):
        while True :
            print ("\n  -- Communication --")
            print ("  1. Post Announcement\n  2. View Announcements\n  3. View Student Queries\n  4. Reply to Queries\n  5. Back")
            action =input ("  Choice: ").strip ()
            clear_screen()
            match action:
                case '1':
                    title =input ("Enter title: ")
                    content =input ("Enter content: ")
                    deadline_input =input ("Enter deadline (YYYY-MM-DD) or press Enter to skip: ").strip ()
                    deadline =deadline_input if deadline_input else None 
                    try :
                        self ._announcement_manager .post_announcement (title ,content ,deadline )
                        print ("Announcement posted successfully.")
                    except ValueError as e :
                        print (f"Error: {e }")
                case '2':
                    self ._announcement_manager .view_all_announcements ()

                    announcement_ids =self ._announcement_manager .get_announcement_ids ()
                    self ._notification_manager .mark_announcements_viewed ("principal",announcement_ids )
                case '3':
                    self ._query_manager .view_pending_queries ()
                case '4':
                    print("\nPending Queries:")
                    self._query_manager.view_pending_queries()
                    q =input ("\nEnter Query ID to reply: ")
                    r =input ("Reply: ")
                    self ._query_manager .reply_to_query (q ,r )
                case '5':
                    break 
                case _:
                    print ("Invalid action.")

    def _principal_leave_menu (self ):
        while True :
            print ("\n  -- Leave Management --")
            print ("  1. View Pending Leaves\n  2. Approve Leave\n  3. Reject Leave\n  4. Back")
            action =input ("  Choice: ").strip ()
            clear_screen()
            match action:
                case '1':
                    leaves =self ._leave_manager .get_pending_leaves ()
                    if not leaves :
                        print ("No pending leaves.")
                    else :
                        for l in leaves :
                            role_display =l .get ("role","Student")
                            applicant =l .get ("applicant_name",l .get ("student_name","Unknown"))
                            print (f"ID: {l ['id']} | {role_display }: {applicant } | Days: {l ['days']} | Reason: {l ['reason']}")
                case '2':
                    print("\nPending Leave Applications:")
                    leaves=self._leave_manager.get_pending_leaves()
                    if not leaves: print("No pending leaves.")
                    else:
                        for l in leaves: print(f"ID: {l['id']} | {l.get('role', 'Student')}: {l.get('student_name') or l.get('applicant_name')}")
                    lid =input ("\nEnter Leave ID to Approve: ")
                    if self ._leave_manager .approve_leave (lid ):
                        print ("Leave Approved.")
                    else :
                        print ("Failed to approve leave (Invalid ID or not pending).")
                case '3':
                    print("\nPending Leave Applications:")
                    leaves=self._leave_manager.get_pending_leaves()
                    if not leaves: print("No pending leaves.")
                    else:
                        for l in leaves: print(f"ID: {l['id']} | {l.get('role', 'Student')}: {l.get('student_name') or l.get('applicant_name')}")
                    lid =input ("\nEnter Leave ID to Reject: ")
                    if self ._leave_manager .reject_leave (lid ):
                        print ("Leave Rejected.")
                    else :
                        print ("Failed to reject leave.")
                case '4':
                    break 
                case _:
                    print ("Invalid action.")

    def _teacher_leave_check (self ):

         if not self ._teacher .current_teacher_name :return 

         print (f"\n--- Leave Requests for {self ._teacher .current_teacher_name }'s Students ---")

         teacher_obj =self ._attendance_manager .get_teacher (self ._teacher .current_teacher_name )
         if not teacher_obj :return 

         all_leaves =self ._leave_manager .get_pending_leaves ()

         my_leaves =[l for l in all_leaves if any (s .name ==l ['student_name']for s in teacher_obj ._assigned_students_objects )]

         if not my_leaves :
             print ("No pending leave requests from your students.")
             return 

         for l in my_leaves :
             print (f"ID: {l ['id']} | Student: {l ['student_name']} | Days: {l ['days']} | Reason: {l ['reason']}")

         action =input ("Approve (A) / Reject (R) / Cancel (C): ").lower ()
         if action =='a':
             lid =input ("Enter ID: ")

             if any (l ['id']==int (lid )for l in my_leaves if l ['id']==int (lid )):
                  self ._leave_manager .approve_leave (lid )
                  print ("Approved.")
             else :print ("Invalid ID.")
         elif action =='r':
             lid =input ("Enter ID: ")
             if any (l ['id']==int (lid )for l in my_leaves if l ['id']==int (lid )):
                  self ._leave_manager .reject_leave (lid )
                  print ("Rejected.")
             else :print ("Invalid ID.")

    def _teacher_query_menu (self ):

        if not self ._teacher .current_teacher_name :return 

        print (f"\n--- Queries for {self ._teacher .current_teacher_name } ---")
        print ("1. View Pending Queries\n2. Reply to Query\n3. Back")
        choice =input ("Choice: ").strip ()

        if choice =='1':
            self ._query_manager .view_pending_queries (target_filter =self ._teacher .current_teacher_name )
        elif choice =='2':
            q_id =input ("Query ID: ")
            reply =input ("Reply: ")
            try :
                self ._query_manager .reply_to_query (q_id ,reply )
                print ("Reply sent successfully.")
            except ValueError as e :
                print (f"Error: {e }")
        elif choice =='3':
            return 
        else :
            print ("Invalid choice.")

    def _teacher_apply_leave (self ):

        if not self ._teacher .current_teacher_name :return 

        print (f"\n--- Apply for Leave ({self ._teacher .current_teacher_name }) ---")
        date =input ("Start Date (YYYY-MM-DD): ")
        try :
            days =int (input ("Number of days: "))
            reason =input ("Reason: ")
            lid =self ._leave_manager .apply_leave (self ._teacher .current_teacher_name ,date ,days ,reason ,role ="Teacher")
            print (f"Leave application submitted. ID: {lid }")
        except ValueError :
            print ("Invalid input.")

    def _teacher_check_leave_status (self ):

        if not self ._teacher .current_teacher_name :return 

        leaves =self ._leave_manager .get_applicant_leaves (self ._teacher .current_teacher_name )
        if not leaves :
            print ("No leave applications found.")
            return 

        print (f"\n--- My Leave Applications ({self ._teacher .current_teacher_name }) ---")
        for l in leaves :
            role_display =l .get ("role","Student")
            print (f"ID: {l ['id']} | Date: {l ['start_date']} | Days: {l ['days']} | Status: {l ['status']} | Role: {role_display }")
            print (f"Reason: {l ['reason']}")
            print ("-"*50 )

    def _teacher_menu (self ):
        while True :

            viewed =self ._notification_manager .get_viewed_announcements (self ._teacher .current_teacher_name )
            unread_count =self ._announcement_manager .get_unread_count (viewed )

            summary =self ._notification_manager .get_notification_summary ("Teacher",self ._teacher .current_teacher_name ,self ._query_manager ,self ._leave_manager )

            notification_badge =f" [{unread_count } new]"if unread_count >0 else ""
            query_badge =f" [{summary ['queries']}]"if summary ["queries"]>0 else ""
            leave_badge =f" [{summary ['leaves']}]"if summary ["leaves"]>0 else ""

            print (f"\n--- Teacher Dashboard ({self ._teacher .current_teacher_name }) ---")
            print (f"1. Add Attendance (Assigned)\n2. View Attendance\n3. View Assigned Students\n4. Add Marks\n5. View My Attendance\n6. Announcements{notification_badge }\n7. Queries{query_badge }\n8. Leave Requests (Students){leave_badge }\n9. Apply for Leave\n10. Check My Leave Status\n11. Logout")
            action =input ("Choice: ").strip ()
            clear_screen()
            match action:
                case '1':self ._teacher .add_record ()
                case '2':self ._teacher .admin_view ()
                case '3':self ._teacher .view_student_db ()
                case '4':self ._teacher .add_marks ()
                case '5':self ._teacher .view_own_attendance ()
                case '6':
                    self ._announcement_manager .view_all_announcements ()
                    announcement_ids =self ._announcement_manager .get_announcement_ids ()
                    self ._notification_manager .mark_announcements_viewed (self ._teacher .current_teacher_name ,announcement_ids )
                case '7':self ._teacher_query_menu ()
                case '8':self ._teacher_leave_check ()
                case '9':self ._teacher_apply_leave ()
                case '10':self ._teacher_check_leave_status ()
                case '11':break 
                case _:
                    print ("Invalid.")

    def _student_menu (self ,student_name ):
        while True :
            viewed =self ._notification_manager .get_viewed_announcements (student_name )
            unread_count =self ._announcement_manager .get_unread_count (viewed )
            notification_badge =f" [{unread_count } new]"if unread_count >0 else ""

            print (f"\n--- Student Dashboard ({student_name }) ---")
            print (f"1. View Attendance\n2. View Announcements{notification_badge }\n3. Submit Query\n4. View My Queries\n5. View My Marks/Performance\n6. Apply for Leave\n7. Check Leave Status\n8. Logout")
            action =input ("Choice: ").strip ()
            clear_screen()
            match action:
                case '1':
                    self ._principal .view_specific_student (student_name )
                case '2':
                    self ._announcement_manager .view_all_announcements ()

                    announcement_ids =self ._announcement_manager .get_announcement_ids ()
                    self ._notification_manager .mark_announcements_viewed (student_name ,announcement_ids )
                case '3':
                    target_choice =input ("submit to (1) Principal or (2) Specific Teacher? ")
                    if target_choice =='1':
                        target ="Principal"
                    else :
                        teachers =self ._attendance_manager .get_all_teachers ()
                        print (f"\nAvailable Teachers: {', '.join (teachers .keys ())}")
                        target =input ("Enter teacher name: ").capitalize ()

                    q =input ("Query: ")
                    self ._query_manager .submit_query (student_name ,q ,target )
                    print("Query submitted successfully.")
                case '4':self ._query_manager .view_student_queries (student_name )
                case '5':
                    s =self ._attendance_manager .get_student (student_name )
                    if s :
                        print (f"\nMarks: {s .marks }")
                        print (f"Average: {s .calculate_average_marks ():.2f}")
                        print (f"Performance: {s .calculate_performance ()}")
                    else :print ("Record not found.")
                case '6':
                    date =input ("Start Date (YYYY-MM-DD): ")
                    try :
                        days =int (input ("Number of days: "))
                        reason =input ("Reason: ")
                        lid =self ._leave_manager .apply_leave (student_name ,date ,days ,reason )
                        print (f"Leave applied. ID: {lid }")
                    except ValueError :print ("Invalid days.")
                case '7':
                    leaves =self ._leave_manager .get_student_leaves (student_name )
                    for l in leaves :
                        print (f"ID: {l ['id']} | Date: {l ['start_date']} | Status: {l ['status']}")
                case '8':break 
                case _:
                    print ("Invalid.")

if __name__ =="__main__":
    system =StudentManagementSystem ()
    system .run ()
