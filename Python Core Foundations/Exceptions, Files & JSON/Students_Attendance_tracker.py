class Student:
    def __init__(self, name, department):
        self.name=name
        self.department=department
        self._attendance_records={}

    def add_attendance(self, date, status):
        self._attendance_records[date]=status

    def get_all_dates(self):
        return sorted(self._attendance_records.keys())

    def __str__(self):
        return f"{self.name} - Department: {self.department}"

    def calculate_annual_percentage(self):
        if not self._attendance_records:
            return 0

        total_days=len(self._attendance_records)
        present_days=sum(1 for s in self._attendance_records.values() if s=='P')
        return 0 if total_days==0 else (present_days / total_days) * 100

class AttendanceManager:
    def __init__(self):
        self._students={}

    def add_student(self, name, department):
        name=name.capitalize()
        if name in self._students:
            return False
        self._students[name]=Student(name, department)
        return True

    def get_student(self, name):
        if name is None:
            return None
        return self._students.get(name.capitalize())

    def add_attendance(self, name, date, status):
        student=self.get_student(name)
        if not student:
            return False

        if date in student._attendance_records:
            return False

        student.add_attendance(date, status)
        return True

    def update_last_attendance(self, name, status):
        student=self.get_student(name)
        if not student or not student._attendance_records:
            return False

        last_date=max(student.get_all_dates())
        student.add_attendance(last_date, status)
        return True

    def get_all_students(self):
        return self._students

    def get_sorted_students_by_attendance(self):
        return sorted(
            self._students.items(),
            key=lambda x: x[1].calculate_annual_percentage(),
            reverse=True,
        )

class Admin:
    def __init__(self, manager, record_manager=None):
        self.manager=manager
        self._record_manager=record_manager

    def set_record_manager(self, record_manager):
        self._record_manager=record_manager

    def add_record(self):
        name=input("Enter student's name to add attendance: ")
        dept=input("Enter student's department: ").capitalize()
        date=input("Enter date (YYYY-MM-DD): ")

        if self.manager.get_student(name) is None:
            self.manager.add_student(name, dept)

        student=self.manager.get_student(name)
        if date in student._attendance_records:
            print(f"Attendance for {name} on {date} already exists. Use update option to modify.")
            return

        while True:
            status=self.get_status_input()
            if status=='Invalid':
                print("Invalid input. Please enter 'Present' or 'Absent'.")
            else:
                self.manager.add_attendance(name, date, status)
                print(f"Attendance for {name} in department {dept} on {date}  recorded as {status}.")
                break

    def update_record(self):
        name=input("Enter student's name to update attendance: ")
        student=self.manager.get_student(name)

        if not student:
            print(f"No records found for {name}.")
            return

        dates=student.get_all_dates()
        if not dates:
            print(f"No attendance records found for {name}.")
            return

        last_date=dates[-1]
        current_status=student._attendance_records[last_date]
        print(f"Updating last record for {name} on {last_date}  (Current status: {current_status})")

        while True:
            status=self.get_status_input()
            if status=='Invalid':
                print("Invalid input. Please enter 'Present' or 'Absent'.")
            else:
                self.manager.update_last_attendance(name, status)
                print(f"Attendance for {name} on {last_date} updated to {status}.")
                break

    def admin_view(self):
        if not self.manager.get_all_students():
            print("No attendance records available.")
            return

        choice=input("Do you want to view records for:\n1. All students\n2. Specific student\n3. students with Low attendance\nEnter your choice: ").lower()

        sorted_students=self.manager.get_sorted_students_by_attendance()

        match choice:
            case '1':
                self.view_all_students(sorted_students)
            case '2':
                name=input("Enter student's name to view attendance: ")
                self.view_specific_student(name)
            case '3':
                self.view_low_attendance_students(sorted_students)
            case _:
                print("Invalid choice.")

    def view_all_students(self, sorted_students):
        for _, student in sorted_students:
            self.print_student_details(student)

    def view_specific_student(self, name):
        student=self.manager.get_student(name)
        if not student:
            print(f"No records found for {name}.")
            return

        choice=input("Do you want to view all dates or a specific range? (all/specific): ").lower()

        match choice:
            case "all":
                self.print_student_details(student)
            case "specific":
                start_date=input("Enter start date (YYYY-MM-DD): ")
                end_date=input("Enter end date (YYYY-MM-DD): ")
                self.print_student_details(student, start_date, end_date)
            case _:
                print("Invalid choice.")

    def view_low_attendance_students(self, sorted_students):
        print("\nstudents with attendance below 75%:")
        found=False
        for _, student in sorted_students:
            percentage=student.calculate_annual_percentage()
            if percentage <= 75:
                found=True
                self.print_student_details(student)

        if not found:
            print("No students with low attendance.")

    def print_student_details(self, student, start_date=None, end_date=None):
        print(f"\nAttendance records for {student.name}:")

        for date in student.get_all_dates():
            if start_date and end_date and not (start_date <= date <= end_date):
                continue

            status=student._attendance_records[date]
            print(f"  Date: {date},Status: {status}")

        print(f"  Department: {student.department}")

        annual_percentage=student.calculate_annual_percentage()

        print(f"  Annual Attendance %: {annual_percentage:.2f}%")
        if annual_percentage <= 75:
            print(f"  Warning: {student.name}'s attendance is below 75%!")

    def get_status_input(self):
        status=input("Enter attendance status (Present/Absent): ")
        if status.lower() in ['present', 'p']:
            return 'P'
        elif status.lower() in ['absent', 'a']:
            return 'A'
        else:
            return 'Invalid'
        

def main():
    manager=AttendanceManager()
    admin=Admin(manager)
    
    while True:
        authority=input("\nEnter your role (Admin/student/Exit): ").capitalize()
        match authority:
            case "Admin":
                while True:
                    action=input("\nWhat do you want to do?\n 1. Add attendance record\n 2. View attendance record\n 3. Update Record (Last record only)\n 4. Exit\n Enter your action: ")
                    match action:
                        case '1':
                            admin.add_record()
                        case '2':
                            admin.admin_view()
                        case '3':
                            admin.update_record()
                        case '4':
                            print("Exiting Admin mode.")
                            break
                        case _:
                            print("Invalid action. Please try again.")
            case "student":
                student_name=input("Enter your name: ")
                student=manager.get_student(student_name)
                if not student:
                    print(f"No records found for {student_name}.")
                    continue
                admin.view_specific_student(student_name)
            case "Exit":
                print("Exiting Attendance Tracker. Goodbye!")
                break
            case _:
                print("Invalid role. Please enter Admin,student,or Exit.")

if __name__=="__main__":
    main()