import json
import os

USERS_FILE='users.json'
EMPLOYEE_FILE='employee_data.json'
CUSTOMER_FILE='customer_data.json'
LOAN_FILE='loan_application.json'

def load_json(filename, default=None):
    if default is None:
        default={} if filename==USERS_FILE else []
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(filename, 'w') as f:
            json.dump(default, f, indent=4)
        return default
def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

class Data:
    def __init__(self, username=None):
        self.username=username
    @property
    def password(self):
        if not self.username:
            return None
        users=load_json(USERS_FILE, {})
        return users.get(self.username, {}).get("password")
    @password.setter
    def password(self, new_password):
        if not self.username:
            return
        users=load_json(USERS_FILE, {})
        if self.username in users:
            users[self.username]["password"]=new_password
            save_json(USERS_FILE, users)
    def authenticate(self, username, password):
        users=load_json(USERS_FILE, {})
        if username in users:
            if users[username]["password"]==password:
                data=users[username]
                data['username']=username
                return data
        return None
    def deposit_money(self):
        try:
            target_acc=input("Enter Account Number to deposit into: ")
            amount=float(input("Enter Amount to deposit: "))
            if amount <= 0:
                print("Amount must be positive.")
                return
            customers=load_json(CUSTOMER_FILE, [])
            found=False
            for cust in customers:
                if cust.get("Account Number")==target_acc:
                    cust["Balance"] += amount
                    print(f"Deposited {amount} successfully. New Balance: {cust['Balance']}")
                    found=True
                    break
            if found:
                save_json(CUSTOMER_FILE, customers)
            else:
                print("Account Number not found.")
        except ValueError:
            print("Invalid input.")

class Admin(Data):
    def __init__(self, username):
        super().__init__(username)
    def menu(self):
        while True:
            print("\n=== Admin Menu ===")
            choice=input("\n1. Add Employee\n2. Add Customer\n3. View Employees\n4. View Customers\n5. Deposit Money\n6. Withdraw Money (As Cashier)\n7. Update Password\n8. Update Employee\n9. Check Loan Eligibility\n10. Apply for Loan\n11. Update Loan Status\n12. Logout\nChoice: ")
            if choice=='1': 
                self.add_employee()
            elif choice=='2': 
                self.add_customer()
            elif choice=='3': 
                self.view_employees()
            elif choice=='4': 
                self.view_customers()
            elif choice=='5': 
                self.deposit_money()
            elif choice=='6': 
                self.withdraw_any()
            elif choice=='7': 
                self.update_password()
            elif choice=='8': 
                self.update_employee()
            elif choice=='9': 
                self.check_eligibility()
            elif choice=='10': 
                self.apply_loan()
            elif choice=='11': 
                self.update_loan_status()
            elif choice=='12': 
                break
            else: 
                print("Invalid choice.")
    def check_eligibility(self):
        try:
            acc_num=input("Enter Account Number: ")
            amount=float(input("Enter Loan Amount: "))
            customers=load_json(CUSTOMER_FILE, [])
            found=False
            for c in customers:
                if c.get("Account Number")==acc_num:
                    found=True
                    cibil=c.get("CIBIL Score", 0)
                    balance=c.get("Balance", 0)
                    if cibil >= 750 and amount <= (balance * 10):
                        print("Eligible for loan.")
                    else:
                        print("Not eligible.")
                    break
            if not found:
                print("Account Number not found.")
        except ValueError:
            print("Invalid input.")
    def apply_loan(self):
        try:
            acc_num=input("Enter Account Number: ")
            amount=float(input("Enter Loan Amount: "))
            l_type=input("Enter Loan Type: ")
            duration=int(input("Duration (months): "))
            customers=load_json(CUSTOMER_FILE, [])
            cust_data=next((c for c in customers if c.get("Account Number")==acc_num), None)
            if not cust_data:
                print("Account Number not found.")
                return
            loans=load_json(LOAN_FILE, [])
            loan_id=1
            if loans:
                loan_id=max(l["Loan ID"] for l in loans) + 1
            new_loan={"Loan ID": loan_id,"Customer ID": cust_data["Customer ID"],"Account Number": acc_num,"Amount": amount,"Type": l_type,"Duration": duration,"Status": "Pending"}
            loans.append(new_loan)
            save_json(LOAN_FILE, loans)
            print(f"Loan Application Submitted. ID: {loan_id}")
        except ValueError:
            print("Invalid input.")
    def update_loan_status(self):
        try:
            loan_id = int(input("Enter Loan ID to update: "))
            loans = load_json(LOAN_FILE, [])
            found = False
            for loan in loans:
                if loan["Loan ID"] == loan_id:
                    print(f"Loan ID: {loan_id}, Current Status: {loan.get('Status')}")
                    ch = input("1. Approve\n2. Reject\n3. Pending\n Enter your choice: ")
                    if ch == '1': loan["Status"] = "Approved"
                    elif ch == '2': loan["Status"] = "Rejected"
                    elif ch == '3': loan["Status"] = "Pending"
                    else: print("Invalid choice, status unchanged.")
                    print(f"Status is now: {loan['Status']}")
                    found = True
                    break
            if found:
                save_json(LOAN_FILE, loans)
            else:
                print("Loan ID not found.")
        except ValueError:
            print("Invalid input.")
    def update_employee(self):
        try:
            emp_id = int(input("Enter Employee ID to update: "))
            employees = load_json(EMPLOYEE_FILE, [])
            found = False
            for emp in employees:
                if emp["Employee ID"] == emp_id:
                    print(f"Updating Employee: {emp['Name']}")
                    ch = input("1. Update Salary\n2. Update Status\nEnter your choice: ")
                    if ch == '1':
                        new_sal = float(input("Enter new Salary: "))
                        emp["Salary"] = new_sal
                        print("Salary Updated.")
                    elif ch == '2':
                        st_ch = input("Enter Status(1.Working or 2.Not Working): ")
                        if st_ch == '1': emp["Status"] = "Working"
                        elif st_ch == '2': emp["Status"] = "Not Working"
                        else: print("Invalid Status Choice.")
                        print(f"Status Updated to {emp.get('Status')}")
                    found = True
                    break
            if found:
                save_json(EMPLOYEE_FILE, employees)
            else:
                print("Employee ID not found.")
        except ValueError:
            print("Invalid Input.")
    def update_password(self):
        old_pass=input("Enter current password: ")
        if old_pass==self.password:
            new_pass=input("Enter new password: ")
            self.password=new_pass
            print("Password updated successfully.")
        else:
            print("Incorrect Password.")
    def add_employee(self):
        name=input("Enter Employee Name: ").capitalize()
        username=input("Enter Username: ").lower()
        users=load_json(USERS_FILE, {})
        if username in users:
            print("Username already taken.")
            return
        password=input("Enter Password: ")
        print("Select Designation:\n1. Cashier\n2. Loan Officer")
        d_choice=input("Choice: ").capitalize()
        designation="Cashier" if d_choice=='1' else "Loan Officer" if d_choice=='2' else None
        if not designation:
            print("Invalid Designation.")
            return
        employees=load_json(EMPLOYEE_FILE, [])
        emp_id=1
        if employees:
            emp_id=max(e["Employee ID"] for e in employees) + 1
        new_emp={"Employee ID": emp_id,"Name": name,"Designation": designation,"Salary": 0.0,"Status": "Working"}
        employees.append(new_emp)
        save_json(EMPLOYEE_FILE, employees)
        users[username]={"password": password,"role": "Employee","designation": designation,"employee_id": emp_id}
        save_json(USERS_FILE, users)
        print(f"Employee {name} added with ID {emp_id}.")
    def add_customer(self):
        name=input("Enter Customer Name: ")
        username=input("Enter Username for Customer: ")
        users=load_json(USERS_FILE, {})
        if username in users:
            print("Username already taken.")
            return
        password=input("Enter Password: ")
        customers=load_json(CUSTOMER_FILE, [])
        cust_id=1
        if customers:
            cust_id=max(c["Customer ID"] for c in customers) + 1
        acc_num=f"ACC{cust_id}"
        new_cust={"Customer ID": cust_id,"Account Number": acc_num,"Customer Name": name,"Balance": 0.0,"CIBIL Score": 700 }
        customers.append(new_cust)
        save_json(CUSTOMER_FILE, customers)
        users[username]={"password": password,"role": "Customer","customer_id": cust_id,"account_number": acc_num}
        save_json(USERS_FILE, users)
        print(f"Customer {name} added. Account Number: {acc_num}")
    def view_employees(self):
        print("\n=== Employee List ===")
        employees=load_json(EMPLOYEE_FILE, [])
        if not employees:
            print("No employees found.")
            return  
        for e in employees: print(e)
    def view_customers(self):
        print("\n=== Customer List ===")
        customers=load_json(CUSTOMER_FILE, [])
        if not customers:
            print("No customers found.")
            return
        for c in customers: print(c)
    def withdraw_any(self):
        try:
            target_acc=input("Enter Account Number to withdraw from: ")
            amount=float(input("Enter Amount: "))
            if amount <= 0:
                print("Invalid amount.")
                return
            customers=load_json(CUSTOMER_FILE, [])
            found=False
            for c in customers:
                if c.get("Account Number")==target_acc:
                    if c["Balance"] >= amount:
                        c["Balance"] -= amount
                        print(f"Withdrawn {amount}. New Balance: {c['Balance']}")
                        found=True
                    else:
                        print("Insufficient Balance.")
                        return
                    break
            if found:
                save_json(CUSTOMER_FILE, customers)
            else:
                print("Account Number not found.")
        except ValueError:
            print("Invalid input.")

class Employee(Data):
    def __init__(self, username, user_data):
        super().__init__(username)
        self.designation=user_data.get("designation")
        self.emp_id=user_data.get("employee_id")
    def menu(self):
        employees = load_json(EMPLOYEE_FILE, [])
        is_working = False
        for emp in employees:
            if emp["Employee ID"] == self.emp_id:
                if emp.get("Status") == "Working":
                    is_working = True
                break
        if not is_working:
            print("Access Denied: You are not currently marked as 'Working'.")
            return
        if self.designation=="Cashier":
            self.cashier_menu()
        elif self.designation=="Loan Officer":
            self.loan_officer_menu()
        else:
            print("Invalid Designation.")
    def cashier_menu(self):
        while True:
            print(f"\n=== Cashier Menu ({self.designation}) ===")
            choice=input("1. View All Customers\n2. Deposit Money\n3. Withdraw Money (Any Account)\n4. Logout\n Enter choice: ")
            if choice=='1': self.view_customers()
            elif choice=='2': self.deposit_money() 
            elif choice=='3': self.withdraw_any()
            elif choice=='4': break
            else: print("Invalid choice.")
    def loan_officer_menu(self):
        while True:
            print(f"\n=== Loan Officer Menu ({self.designation}) ===")
            choice=input("1. Check Loan Eligibility\n2. Apply for Loan\n3. Update Loan Status\n4. Logout\n Enter choice: ")
            if choice=='1': self.check_eligibility()
            elif choice=='2': self.apply_loan()
            elif choice=='3': self.update_loan_status()
            elif choice=='4': break
            else: print("Invalid choice.")
    def update_loan_status(self):
        Admin(self.username).update_loan_status()
    def view_customers(self):
        print("\n=== Customer List ===")
        customers=load_json(CUSTOMER_FILE, [])
        if not customers:
            print("No customers found.")
            return
        for c in customers: print(c)
    def withdraw_any(self):
        Admin(self.username).withdraw_any()
    def check_eligibility(self):
        try:
            acc_num=input("Enter Account Number: ")
            amount=float(input("Enter Loan Amount: "))
            customers=load_json(CUSTOMER_FILE, [])
            found=False
            for c in customers:
                if c.get("Account Number")==acc_num:
                    found=True
                    cibil=c.get("CIBIL Score", 0)
                    balance=c.get("Balance", 0)
                    if cibil >= 750 and amount <= (balance * 10):
                        print("Eligible for loan.")
                    else:
                        print("Not eligible.")
                    break
            if not found:
                print("Account Number not found.")
        except ValueError:
            print("Invalid input.")
    def apply_loan(self):
        try:
            acc_num=input("Enter Account Number: ")
            amount=float(input("Enter Loan Amount: "))
            l_type=input("Enter Loan Type: ")
            duration=int(input("Duration (months): "))
            customers=load_json(CUSTOMER_FILE, [])
            cust_data=next((c for c in customers if c.get("Account Number")==acc_num), None)
            if not cust_data:
                print("Account Number not found.")
                return
            loans=load_json(LOAN_FILE, [])
            loan_id=1
            if loans:
                loan_id=max(l["Loan ID"] for l in loans) + 1
            new_loan={"Loan ID": loan_id,"Customer ID": cust_data["Customer ID"],"Account Number": acc_num,"Amount": amount,"Type": l_type,"Duration": duration,"Status": "Pending"}
            loans.append(new_loan)
            save_json(LOAN_FILE, loans)
            print(f"Loan Application Submitted. ID: {loan_id}")
        except ValueError:
            print("Invalid input.")

class Customer(Data):
    def __init__(self, username, user_data):
        super().__init__(username)
        self.cust_id=user_data.get("customer_id")
        self.account_number=user_data.get("account_number")
    def menu(self):
        while True:
            print("\n=== Customer Menu ===")
            choice=input("1. View My Details\n2. Withdraw Money (My Account)\n3. Deposit Money (Any Account)\n4. Update Password\n5. Logout\n Enter choice: ")
            if choice=='1': self.view_details()
            elif choice=='2': self.withdraw_self()
            elif choice=='3': self.deposit_money()
            elif choice=='4': self.update_password()
            elif choice=='5': break
            else: print("Invalid choice.")
    def update_password(self):
        old_pass=input("Enter current password: ")
        if old_pass==self.password:
            new_pass=input("Enter new password: ")
            self.password=new_pass
            print("Password updated successfully.")
        else:
            print("Incorrect Password.")
    def view_details(self):
        customers=load_json(CUSTOMER_FILE, [])
        for c in customers:
            if c["Customer ID"]==self.cust_id:
                print(c)
                return
        print("Account record not found.")
    def withdraw_self(self):
        try:
            amount=float(input("Enter Amount: "))
            if amount <= 0:
                print("Invalid amount.")
                return
            customers=load_json(CUSTOMER_FILE, [])
            for c in customers:
                if c["Customer ID"]==self.cust_id:
                    if c["Balance"] >= amount:
                        c["Balance"] -= amount
                        print(f"Withdrawn {amount}. New Balance: {c['Balance']}")
                        save_json(CUSTOMER_FILE, customers)
                    else:
                        print("Insufficient funds.")
                    return
        except ValueError:
            print("Invalid input.")

def main():
    users=load_json(USERS_FILE, {})
    has_admin=False
    for u in users.values():
        if u.get("role")=="Admin":
            has_admin=True
            break
    if not has_admin:
        users["manager"]={
            "password": "manager@123",
            "role": "Admin"
        }
        save_json(USERS_FILE, users)
    while True:
        print("\n--- Bank Management System ---")
        choice=input("1. Login\n2. Exit\n Enter Choice: ")
        if choice=='1':
            username=input("Username: ")
            password=input("Password: ")
            auth=Data()
            user_data=auth.authenticate(username, password)
            if user_data:
                role=user_data.get("role")
                username_val=user_data.get("username")
                print(f"Login Successful. Welcome {role}!")
                if role=="Admin":
                    Admin(username_val).menu()
                elif role=="Employee":
                    Employee(username_val, user_data).menu()
                elif role=="Customer":
                    Customer(username_val, user_data).menu()
                else:
                    print("Invalid Role Assigned.")
            else:
                print("Invalid Credentials.")
        elif choice=='2':
            print("Exiting...")
            break
        else:
            print("Invalid Choice.")

if __name__=="__main__":
    main()