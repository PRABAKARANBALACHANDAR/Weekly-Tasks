from Managers import Students_Attendance_tracker
from Managers import students_record_manager
from Managers import announcements_manager
from Managers import query_manager
from Exceptions import custom_exceptions

class AdminUI(Students_Attendance_tracker.Admin):
    def __init__(self, attendance_manager, record_manager):
        super().__init__(attendance_manager, record_manager)
        self._record_manager=record_manager

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
            age=int(input("Enter age: "))
            grade=input("Enter grade: ").strip().upper()
            course=input("Enter course enrolled: ").strip().upper()
            dept=input("Enter department: ").strip().capitalize()
            
            sid=self._record_manager.create_record(name, age, grade, course)
            print(f"Record created with ID: {sid}")
                        
            if self.manager.add_student(name, dept):
                print(f"Added {name} to Attendance System.")
            else:
                print(f"{name} already exists in Attendance System.")   
            return name
            
        except (custom_exceptions.RecordExistsError, custom_exceptions.InvalidInputError, ValueError) as e:
            print(f"Error registering student: {e}")
            return None
    
    def add_student_record(self):
        if not self._record_manager:
            print("No record manager attached.")
            return
        self.register_new_student()

    def add_record(self):
        name=input("Enter student's name to add attendance: ").strip().capitalize()
        student=self.manager.get_student(name)
        if student is None:
            print(f"Student '{name}' not found. initiating registration...")
            name=self.register_new_student(name)
            if not name:
                return     
        student=self.manager.get_student(name)
        if not student: 
            return
        date=input("Enter date (YYYY-MM-DD): ")
        if date in student._attendance_records:
            print(f"Attendance for {name} on {date} already exists. Use update option to modify.")
            return

        while True:
            status=self.get_status_input()
            if status=='Invalid':
                print("Invalid input. Please enter 'Present' or 'Absent'.")
            else:
                self.manager.add_attendance(name, date, status)
                print(f"Attendance for {name} on {date} recorded as {status}.")
                break

class StudentManagementSystem:
    def __init__(self):
        self._record_manager=students_record_manager.RecordManager()
        self._attendance_manager=Students_Attendance_tracker.AttendanceManager()
        self._announcement_manager=announcements_manager.AnnouncementManager()
        self._query_manager=query_manager.QueryManager()
        self._admin=AdminUI(self._attendance_manager, self._record_manager)

    def run(self):
        while True:
            user_type=input("Are you an 'admin' or 'student'? Type 'Exit' to quit: ").strip().lower()
            match user_type:
                case "admin" | "1":
                    while True:
                        action=input("Choose action:\n 1. Add attendance record\n 2. View attendance records\n 3. View student records DB\n 4. Update last attendance\n 5. Add student record\n 6. Update student record\n 7. Delete student record\n 8. Post announcement\n 9. View announcements\n 10. View student queries\n 11. Reply to query\n 12. Back to main menu\nEnter your choice: ").strip().lower()
                        match action:
                            case '1' | 'add attendance':
                                try:
                                    self._admin.add_record()
                                except (custom_exceptions.RecordExistsError, custom_exceptions.InvalidInputError) as e:
                                    print(f"Error: {e}")
                            case '2' | 'view attendance':
                                self._admin.admin_view()
                            case '3' | 'records':
                                try:
                                    self._admin.view_student_db()
                                except (custom_exceptions.RecordNotFoundError, custom_exceptions.InvalidInputError) as e:
                                    print(f"Error viewing student records: {e}")
                            case '4' | 'update':
                                name=input("Enter student's name to update attendance: ")
                                status=input("Enter new status (Present/Absent): ")
                                
                                status_norm='P' if status.lower() in ['present', 'p'] else ('A' if status.lower() in ['absent', 'a'] else None)
                                if status_norm is None:
                                    print("Invalid status input.")
                                else:
                                    if self._attendance_manager.update_last_attendance(name, status_norm):
                                        print(f"Attendance updated for {name}.")
                                    else:
                                        print(f"Failed to update attendance for {name}.")
                            case '5' | 'add record':
                                self._admin.add_student_record()
                            case '6' | 'update record':
                                self._admin.update_student_record()
                            case '7' | 'delete record':
                                self._admin.delete_student_record()
                            case '8' | 'post announcement':
                                title=input("Enter announcement title: ")
                                content=input("Enter announcement content: ")
                                try:
                                    self._announcement_manager.post_announcement(title, content)
                                    print("Announcement posted successfully!")
                                except ValueError as e:
                                    print(f"Error: {e}")
                            case '9' | 'announcements':
                                self._announcement_manager.view_all_announcements()
                            case '10' | 'queries':
                                self._query_manager.view_pending_queries()
                            case '11' | 'reply':
                                try:
                                    query_id=input("Enter query ID to reply: ")
                                    reply_text=input("Enter your reply: ")
                                    self._query_manager.reply_to_query(query_id, reply_text)
                                    print("Reply sent successfully!")
                                except ValueError as e:
                                    print(f"Error: {e}")
                            case '12' | 'back':
                                break
                            case _:
                                print("Invalid choice. Try again.")
                case "student" | "2":
                    student_name=input("Enter your name: ").strip().capitalize()
                    while True:
                        student_choice=input("\nStudent Menu:\n1. View attendance\n2. View announcements\n3. Submit query\n4. View my queries\n5. Back to main menu\nEnter your choice: ").strip().lower()
                        match student_choice:
                            case '1' | 'attendance':
                                student=self._attendance_manager.get_student(student_name)
                                if not student:
                                    print(f"No attendance records found for {student_name}.")
                                else:
                                    self._admin.view_specific_student(student_name)
                            case '2' | 'announcements':
                                self._announcement_manager.view_all_announcements()
                            case '3' | 'submit':
                                query_text=input("Enter your query: ")
                                try:
                                    self._query_manager.submit_query(student_name, query_text)
                                    print("Your query has been submitted successfully!")
                                except ValueError as e:
                                    print(f"Error: {e}")
                            case '4' | 'my queries':
                                self._query_manager.view_student_queries(student_name)
                            case '5' | 'back':
                                break
                            case _:
                                print("Invalid choice. Try again.")
                case "exit" | "quit":
                    print("Exiting Student Management System. Goodbye!")
                    break
                case _:
                    print("Please enter 'admin', 'student', or 'Exit'.")


if __name__=="__main__":
    system=StudentManagementSystem()
    system.run()