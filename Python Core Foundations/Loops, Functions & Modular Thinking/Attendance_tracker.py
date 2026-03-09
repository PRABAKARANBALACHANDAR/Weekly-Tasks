class Employee :
    def __init__ (self ,name ,department ):
        self .name =name 
        self .department =department 
        self .attendance_records ={}

    def add_attendance (self ,date ,status ):
        self .attendance_records [date ]=status 

    def get_all_dates (self ):
        return sorted (self .attendance_records .keys ())

    def __str__ (self ):
        return f"{self .name } - Department: {self .department }"

    def calculate_annual_percentage (self ,employee ):
        if not employee .attendance_records :
            return 0 

        total_days =0 
        present_days =0 

        for _ ,status in employee .attendance_records .items ():
            total_days +=1 
            if status =='P':
                present_days +=1 

        return 0 if total_days ==0 else (present_days /total_days )*100 

class AttendanceManager :
    def __init__ (self ):
        self .employees ={}

    def add_employee (self ,name ,department ):
        name =name .capitalize ()
        if name in self .employees :
            print (f"Employee {name } already exists.")
            return False 
        self .employees [name ]=Employee (name ,department )
        return True 

    def get_employee (self ,name ):
        return self .employees .get (name .capitalize ())

    def add_attendance (self ,name ,date ,status ):
        employee =self .get_employee (name )
        if not employee :
            return False 

        if date in employee .attendance_records :
            return False 

        employee .add_attendance (date ,status )
        return True 

    def update_last_attendance (self ,name ,status ):
        employee =self .get_employee (name )
        if not employee or not employee .attendance_records :
            return False 

        last_date =max (employee .get_all_dates ())
        employee .add_attendance (last_date ,status )
        return True 

    def get_all_employees (self ):
        return self .employees 

    def get_sorted_employees_by_attendance (self ):
        return sorted (
        self .employees .items (),
        key =lambda x :x [1 ].calculate_annual_percentage (x [1 ]),
        reverse =True 
        )

class Admin :
    def __init__ (self ,manager ):
        self .manager =manager 

    def add_record (self ):
        name =input ("Enter Employee's name to add attendance: ")
        dept =input ("Enter Employee's department: ").capitalize ()
        date =input ("Enter date (YYYY-MM-DD): ")

        if self .manager .get_employee (name )is None :
            self .manager .add_employee (name ,dept )

        employee =self .manager .get_employee (name )
        if date in employee .attendance_records :
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
        name =input ("Enter Employee's name to update attendance: ")
        employee =self .manager .get_employee (name )

        if not employee :
            print (f"No records found for {name }.")
            return 

        dates =employee .get_all_dates ()
        if not dates :
            print (f"No attendance records found for {name }.")
            return 

        last_date =dates [-1 ]
        current_status =employee .attendance_records [last_date ]
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
        if not self .manager .get_all_employees ():
            print ("No attendance records available.")
            return 

        choice =input ("Do you want to view records for:\n1. All employees\n2. Specific employee\n3. Employees with Low attendance\nEnter your choice: ").lower ()

        sorted_employees =self .manager .get_sorted_employees_by_attendance ()

        match choice :
            case '1':
                self .view_all_employees (sorted_employees )
            case '2':
                name =input ("Enter Employee's name to view attendance: ")
                self .view_specific_employee (name )
            case '3':
                self .view_low_attendance_employees (sorted_employees )
            case _ :
                print ("Invalid choice.")

    def view_all_employees (self ,sorted_employees ):
        for _ ,employee in sorted_employees :
            self .print_employee_details (employee )

    def view_specific_employee (self ,name ):
        employee =self .manager .get_employee (name )
        if not employee :
            print (f"No records found for {name }.")
            return 

        choice =input ("Do you want to view all dates or a specific range? (all/specific): ").lower ()

        match choice :
            case "all":
                self .print_employee_details (employee )
            case "specific":
                start_date =input ("Enter start date (YYYY-MM-DD): ")
                end_date =input ("Enter end date (YYYY-MM-DD): ")
                self .print_employee_details (employee ,start_date ,end_date )
            case _ :
                print ("Invalid choice.")

    def view_low_attendance_employees (self ,sorted_employees ):
        print ("\nEmployees with attendance below 75%:")
        found =False 
        for _ ,employee in sorted_employees :
            percentage =employee .calculate_annual_percentage (employee )
            if percentage <=75 :
                found =True 
                self .print_employee_details (employee )

        if not found :
            print ("No employees with low attendance.")

    def print_employee_details (self ,employee ,start_date =None ,end_date =None ):
        print (f"\nAttendance records for {employee .name }:")

        for date in employee .get_all_dates ():
            if start_date and end_date and not (start_date <=date <=end_date ):
                continue 

            status =employee .attendance_records [date ]
            print (f"  Date: {date },Status: {status }")

        print (f"  Department: {employee .department }")

        annual_percentage =employee .calculate_annual_percentage (employee )

        print (f"  Annual Attendance %: {annual_percentage :.2f}%")
        if annual_percentage <=75 :
            print (f"  Warning: {employee .name }'s attendance is below 75%!")

    def get_status_input (self ):
        status =input ("Enter attendance status (Present/Absent): ")
        if status .lower ()in ['present','p']:
            return 'P'
        elif status .lower ()in ['absent','a']:
            return 'A'
        else :
            return 'Invalid'

def main ():
    manager =AttendanceManager ()
    admin =Admin (manager )

    while True :
        authority =input ("\nEnter your role (Admin/Employee/Exit): ").capitalize ()
        match authority :
            case "Admin":
                while True :
                    action =input ("\nWhat do you want to do?\n 1. Add attendance record\n 2. View attendance record\n 3. Update Record (Last record only)\n 4. Exit\n Enter your action: ")
                    match action :
                        case '1':
                            admin .add_record ()
                        case '2':
                            admin .admin_view ()
                        case '3':
                            admin .update_record ()
                        case '4':
                            print ("Exiting Admin mode.")
                            break 
                        case _ :
                            print ("Invalid action. Please try again.")
            case "Employee":
                emp_name =input ("Enter your name: ")
                employee =manager .get_employee (emp_name )
                if not employee :
                    print (f"No records found for {emp_name }.")
                    continue 
                admin .view_specific_employee (emp_name )
            case "Exit":
                print ("Exiting Attendance Tracker. Goodbye!")
                break 
            case _ :
                print ("Invalid role. Please enter Admin,Employee,or Exit.")

if __name__ =="__main__":
    main ()
