from Managers import Students_Attendance_tracker
from Managers import students_record_manager
from Managers import announcements_manager
from Managers import query_manager
from Managers import user_manager
from Exceptions import custom_exceptions

class PrincipalUI(Students_Attendance_tracker.Principal):
    def __init__(self, attendance_manager, record_manager, usr_manager):
        super().__init__(attendance_manager, record_manager)
        self._record_manager=record_manager
        self._user_manager=usr_manager

    def view_student_db(self):
        if not self._record_manager:
            print("No record manager attached.")
            return
        self._record_manager.display_record()

    def register_new_student(self, name=None):
        if name is None:
            name=input("Enter student name: ").strip().capitalize()
        else:
            name=name.strip().capitalize()
            
        print(f"Registering new student: {name}")
        try:
            print("Create Login Credentials:")
            username=input("Username: ").strip()
            if self._user_manager.user_exists(username):
                print("Username already taken.")
                return None
            password=input("Password: ").strip()

            age=int(input("Enter age: "))
            grade=input("Enter grade: ").strip().upper()
            course=input("Enter Course/Department: ").strip().capitalize()
            
            all_teachers=self._record_manager.list_teachers()
            available_teachers=[t.name for t in all_teachers.values() if t.department.lower()==course.lower()]
            
            if not available_teachers:
                print(f"No teachers found for course '{course}'. First teacher record should be added.")
                return None
            
            print(f"Teachers available for {course}: {', '.join(available_teachers)}")
            while True:
                teacher=input("Enter assigned teacher name: ").strip().capitalize()
                if teacher in available_teachers:
                    break
                print(f"Invalid teacher. Please choose from: {', '.join(available_teachers)}")

            sid=self._record_manager.create_record(name, age, grade, course, assigned_teacher=teacher)
            self._user_manager.add_user(username, password, "Student", name)
            print(f"Record created with ID: {sid} and User created.")
            
            if self.manager.add_student(name, course, course, teacher):
                print(f"Added {name} to Attendance System.")
            else:
                print(f"{name} already exists in Attendance System.")   
            return name
            
        except (custom_exceptions.RecordExistsError, custom_exceptions.InvalidInputError, ValueError) as e:
            print(f"Error registering student: {e}")
            return None
    
    def register_new_teacher(self):
        name=input("Enter teacher name: ").strip().capitalize()
        try:
            print("Create Login Credentials:")
            username=input("Username: ").strip()
            if self._user_manager.user_exists(username):
                print("Username already taken.")
                return 
            password=input("Password: ").strip()

            dept=input("Enter department: ").strip().capitalize()
            tid=self._record_manager.create_teacher_record(name, dept)
            self._user_manager.add_user(username, password, "Teacher", name)
            print(f"Teacher record created with ID: {tid} and User created.")

            self.manager.register_teacher(name, dept)
            print(f"Teacher {name} registered in system.")
        except Exception as e:
            print(f"Error registering teacher: {e}")

    def assign_student_to_teacher(self):
        student_name=input("Enter student name: ").strip().capitalize()
        teacher_name=input("Enter teacher name: ").strip().capitalize()
        
        if self._record_manager.assign_student_to_teacher(student_name, teacher_name):
            print(f"Assigned {student_name} to {teacher_name}.")
            t=self.manager.get_teacher(teacher_name)
            s=self.manager.get_student(student_name)
            if t and s:
                 t.assign_student(s)
                 s.assigned_teacher=teacher_name
        else:
             print("Assignment failed. Check if names are correct.")

    def view_teacher_performance(self):
        teachers=self.manager.get_all_teachers()
        if not teachers:
            print("No teachers found.")
            return
        print("\nTeacher Performance Evaluation:")
        for name, teacher_obj in teachers.items():
             perf=teacher_obj.calculate_performance()
             print(f"Teacher: {name}, Performance: {perf}")

    def add_student_record(self):
        if not self._record_manager:
            print("No record manager attached.")
            return
        self.register_new_student()

    def update_student_record(self):
        if not self._record_manager:
            print("No record manager attached.")
            return
        try:
            self._record_manager.update_record()
            print("Student record updated.")
        except (custom_exceptions.RecordNotFoundError, custom_exceptions.InvalidInputError) as e:
            print(f"Error updating record: {e}")

    def delete_student_record(self):
        if not self._record_manager:
            print("No record manager attached.")
            return
        try:
            self._record_manager.delete_record()
            print("Student record deleted.")
        except (custom_exceptions.RecordNotFoundError, custom_exceptions.InvalidInputError) as e:
            print(f"Error deleting record: {e}")

    def add_record(self):
        name=input("Enter name to add attendance: ").strip().capitalize()
        person=self.manager.get_person(name)
        
        if person is None:
            print(f"Person '{name}' not found.")
            choice=input(f"Register '{name}' as new Student? (y/n): ").lower()
            if choice=='y':
                name=self.register_new_student(name)
                if not name: return
                person=self.manager.get_person(name)
            else:
                return

        if not person: return

        date=input("Enter date (YYYY-MM-DD): ")
        if date in person._attendance_records:
            print(f"Attendance for {name} on {date} already exists. Use update option to modify.")
            return

        while True:
            status=self.get_status_input()
            if status=='Invalid':
                print("Invalid input. Please enter 'Present' or 'Absent'.")
            else:
                self.manager.add_attendance(name, date, status)
                if hasattr(person, 'course'):
                    print(f"Attendance for {name} ({person.course}) on {date} recorded as {status}.")
                else:
                    print(f"Attendance for {name} on {date} recorded as {status}.")
                break
    
    def admin_view(self):
        choice=input("View attendance for:\n1. All Students\n2. Specific Person (Student/Teacher)\n3. All Teachers\nChoice: ").lower()
        match choice:
            case '1':
                students=self.manager.get_sorted_students_by_attendance()
                self.view_all_students(students)
            case '2':
                name=input("Enter name: ")
                person=self.manager.get_person(name)
                if person:
                    self.print_student_details(person)
                else:
                    print("Not found.")
            case '3':
                teachers=self.manager.get_all_teachers()
                for t in teachers.values():
                    self.print_student_details(t)
            case _:
                print("Invalid.")

class TeacherUI(Students_Attendance_tracker.Teacher):
    def __init__(self, attendance_manager, record_manager):
        super().__init__("Guest", "Staff", manager=attendance_manager, record_manager=record_manager)
        self.current_teacher_name=None

    def set_user(self, name):
        self.current_teacher_name=name
        if not self.manager.get_teacher(name):
             rec=self._record_manager.get_teacher_by_name(name)
             if rec:
                 self.manager.register_teacher(name, rec.department)
             else:
                 self.manager.register_teacher(name, "Staff")
        
        teacher_obj=self.manager.get_teacher(name)
        
        rec=self._record_manager.get_teacher_by_name(name)
        if rec:
            for s_name in rec.assigned_students:
                s_obj=self.manager.get_student(s_name)
                if s_obj:
                    teacher_obj.assign_student(s_obj)

    def view_student_db(self):
        if not self.current_teacher_name: return
        teacher_record=self._record_manager.get_teacher_by_name(self.current_teacher_name)
        if not teacher_record or not teacher_record.assigned_students:
             print("No assigned students to view.")
             return
             
        print(f"\nAssigned Students for {self.current_teacher_name}:")
        for s_name in teacher_record.assigned_students:
            found=False
            for rid, details in self._record_manager.list_records().items():
                if details.name==s_name:
                    print(f"Name: {details.name}, Grade: {details.grade}, Course: {details.course}, Marks: {details.marks}")
                    found=True
            if not found:
                  print(f"Name: {s_name} (Record details not found)")

    def add_record(self):
        if not self.current_teacher_name: return
        
        name=input("Enter name to add attendance: ").strip().capitalize()
        
        teacher_obj=self.manager.get_teacher(self.current_teacher_name)
        is_assigned=any(s.name==name for s in teacher_obj._assigned_students_objects)
        
        if not is_assigned:
             print(f"Access Denied: Student {name} is not assigned to you.")
             return

        if self.manager.get_student(name) is None:
            print(f"Student {name} not found.")
            return

        student=self.manager.get_student(name)
        date=input("Enter date (YYYY-MM-DD): ")
        if date in student._attendance_records:
            print(f"Attendance for {name} on {date} already exists.")
            return

        while True:
            status=self.get_status_input()
            if status=='Invalid':
                print("Invalid input. Please enter 'Present' or 'Absent'.")
            else:
                self.manager.add_attendance(name, date, status)
                print(f"Attendance for {name} recorded as {status}.")
                break
    
    def add_marks(self):
        if not self.current_teacher_name: return
        name=input("Enter student's name to add marks: ").strip().capitalize()
        
        teacher_obj=self.manager.get_teacher(self.current_teacher_name)
        is_assigned=any(s.name==name for s in teacher_obj._assigned_students_objects)
        
        if not is_assigned:
             print(f"Access Denied: Student {name} is not assigned to you.")
             return
             
        subject=input("Enter subject: ")
        try:
             score=float(input("Enter marks: "))
             if self._record_manager.add_student_mark(name, subject, score):
                  s=self.manager.get_student(name)
                  if s: s.add_mark(subject, score)
                  print("Marks added successfully.")
             else:
                  print("Failed to add marks. Student record might usually not exist?")
        except ValueError:
             print("Invalid marks input.")

class StudentManagementSystem:
    def __init__(self):
        self._record_manager=students_record_manager.RecordManager()
        self._attendance_manager=Students_Attendance_tracker.AttendanceManager()
        self._announcement_manager=announcements_manager.AnnouncementManager()
        self._query_manager=query_manager.QueryManager()
        self._user_manager=user_manager.UserManager()
        
        self._principal=PrincipalUI(self._attendance_manager, self._record_manager, self._user_manager)
        self._teacher=TeacherUI(self._attendance_manager, self._record_manager)
        self._bootstrap_data()
    
    def _bootstrap_data(self):
        records=self._record_manager.list_records()
        for rid, rec in records.items():
            self._attendance_manager.add_student(rec.name, "General", rec.course, rec.assigned_teacher)
            s=self._attendance_manager.get_student(rec.name)
            if s and rec.marks:
                 s.marks=rec.marks
        
        t_records=self._record_manager.list_teachers()
        for tid, trec in t_records.items():
            self._attendance_manager.register_teacher(trec.name, trec.department)
            t_obj=self._attendance_manager.get_teacher(trec.name)
            if t_obj:
                 for s_name in trec.assigned_students:
                      s_obj=self._attendance_manager.get_student(s_name)
                      if s_obj: t_obj.assign_student(s_obj)


    def run(self):
        print("Welcome to Student Management System")
        try:
            while True:
                print("\n--- Login ---")
                username=input("Username (or 'exit' to quit): ").strip()
                if username.lower()=='exit':
                    break
                password=input("Password: ").strip()

                user_data=self._user_manager.authenticate(username, password)
                if not user_data:
                    print("Invalid credentials.")
                    continue

                role=user_data.get("role")
                name=user_data.get("name")
                print(f"\nWelcome, {name} ({role})")

                if role=="Principal":
                    self._principal_menu()
                elif role=="Teacher":
                    self._teacher.set_user(name)
                    self._teacher_menu()
                elif role=="Student":
                    self._student_menu(name)
                else:
                    print("Unknown role.")
        except KeyboardInterrupt:
            print("\nExiting System. Goodbye!")
    
    def _principal_menu(self):
        while True:
            print("\n--- Principal Dashboard ---")
            print("1. Attendance Management\n2. Student Management\n3. Teacher Management\n4. Communication (Announcements/Queries)\n5. Logout")
            choice=input("Enter choice: ").strip()
            
            if choice=='1':
                self._principal_attendance_menu()
            elif choice=='2':
                self._principal_student_menu()
            elif choice=='3':
                self._principal_teacher_menu()
            elif choice=='4':
                self._principal_comm_menu()
            elif choice=='5':
                break
            else:
                print("Invalid choice.")

    def _principal_attendance_menu(self):
        while True:
            print("\n  -- Attendance Management --")
            print("  1. Add Attendance\n  2. View Attendance\n  3. Update Attendance\n  4. Back")
            action=input("  Choice: ").strip()
            if action=='1': self._principal.add_record()
            elif action=='2': self._principal.admin_view()
            elif action=='3': 
                name=input("Enter name to update attendance: ")
                status=input("Enter new status (Present/Absent): ")
                status_norm='P' if status.lower() in ['present', 'p'] else ('A' if status.lower() in ['absent', 'a'] else None)
                if status_norm:
                    success, updated_date=self._attendance_manager.update_last_attendance(name, status_norm)
                    if success:
                        print(f"Attendance updated for {name} on {updated_date}.")
                    else:
                        print(f"Failed to update attendance for {name}. No records found.")
                else: print("Invalid status.")
            elif action=='4': break

    def _principal_student_menu(self):
        while True:
            print("\n  -- Student Management --")
            print("  1. Register Student\n  2. View Student Database\n  3. Update Student Record\n  4. Delete Student Record\n  5. Assign Teacher\n  6. Back")
            action=input("  Choice: ").strip()
            if action=='1': self._principal.register_new_student()
            elif action=='2': self._principal.view_student_db()
            elif action=='3': self._principal.update_student_record()
            elif action=='4': self._principal.delete_student_record()
            elif action=='5': self._principal.assign_student_to_teacher()
            elif action=='6': break
    
    def _principal_teacher_menu(self):
        while True:
            print("\n  -- Teacher Management --")
            print("  1. Register Teacher\n  2. View Teacher Performance\n  3. Back")
            action=input("  Choice: ").strip()
            if action=='1': self._principal.register_new_teacher()
            elif action=='2': self._principal.view_teacher_performance()
            elif action=='3': break

    def _principal_comm_menu(self):
        while True:
            print("\n  -- Communication --")
            print("  1. Post Announcement\n  2. View Announcements\n  3. View Student Queries\n  4. Reply to Queries\n  5. Back")
            action=input("  Choice: ").strip()
            if action=='1':
                title=input("Enter title: ")
                content=input("Enter content: ")
                self._announcement_manager.post_announcement(title, content)
            elif action=='2': self._announcement_manager.view_all_announcements()
            elif action=='3': self._query_manager.view_pending_queries()
            elif action=='4':
                q=input("Query ID: ")
                r=input("Reply: ")
                self._query_manager.reply_to_query(q, r)
            elif action=='5': break

    def _teacher_menu(self):
        while True:
             print(f"\n--- Teacher Dashboard ({self._teacher.current_teacher_name}) ---")
             print("1. Add Attendance (Assigned)\n2. View Attendance\n3. View Assigned Students\n4. Add Marks\n5. Announcements\n6. Queries\n7. Logout")
             action=input("Choice: ").strip()
             if action=='1': self._teacher.add_record()
             elif action=='2': self._teacher.admin_view()
             elif action=='3': self._teacher.view_student_db()
             elif action=='4': self._teacher.add_marks()
             elif action=='5': self._announcement_manager.view_all_announcements()
             elif action=='6': self._query_manager.view_pending_queries()
             elif action=='7': break
             else: print("Invalid.")

    def _student_menu(self, student_name):
        while True:
            print(f"\n--- Student Dashboard ({student_name}) ---")
            print("1. View Attendance\n2. View Announcements\n3. Submit Query\n4. View My Queries\n5. View My Marks/Performance\n6. Logout")
            action=input("Choice: ").strip()
            if action=='1':
                 self._principal.view_specific_student(student_name)
            elif action=='2': self._announcement_manager.view_all_announcements()
            elif action=='3':
                q=input("Query: ")
                self._query_manager.submit_query(student_name, q)
            elif action=='4': self._query_manager.view_student_queries(student_name)
            elif action=='5':
                 s=self._attendance_manager.get_student(student_name)
                 if s:
                    print(f"\nMarks: {s.marks}")
                    print(f"Average: {s.calculate_average_marks():.2f}")
                    print(f"Performance: {s.calculate_performance()}")
                 else: print("Record not found.")
            elif action=='6': break
            else: print("Invalid.")

if __name__=="__main__":
    system=StudentManagementSystem()
    system.run()