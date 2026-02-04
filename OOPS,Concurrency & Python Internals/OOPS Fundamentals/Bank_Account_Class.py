import json

USERS_FILE='users.json'
EMPLOYEE_FILE='employee_data.json'
CUSTOMER_FILE='customer_data.json'
LOAN_FILE='loan_application.json'
DESIGNATION_FILE='designations.json'

PERMISSION_MAP={
    "view_customers":"view_customers",
    "deposit_money":"deposit_money",
    "withdraw_any":"withdraw_any",
    "check_eligibility":"check_eligibility",
    "apply_loan":"apply_loan",
    "update_loan_status":"update_loan_status",
    "remove_customer":"remove_customer"
}

def load_json(filename, default):
    try:
        with open(filename,'r') as f:
            data=json.load(f)
            if isinstance(default,set):
                return set(data)
            return data
    except FileNotFoundError:
        with open(filename,'w') as f:
            json.dump(list(default) if isinstance(default,set) else default,f,indent=4)
        return default
def save_json(filename,data):
    try:
        if isinstance(data,set):
            data=list(data)
        with open(filename,'w') as f:
            json.dump(data,f,indent=4)
    except IOError as e:
        print(f"Error saving to {filename}: {e}")

class Data:
    def __init__(self,username=None):
        self.username=username
    @property
    def password(self):
        users=load_json(USERS_FILE,{})
        return users.get(self.username,{}).get("password")
    @password.setter
    def password(self,new):
        users=load_json(USERS_FILE,{})
        if self.username in users:
            users[self.username]["password"]=new
            save_json(USERS_FILE,users)
            print("Password updated successfully.")
        else:
            print("User not found.")
    def authenticate(self,u,p):
        users=load_json(USERS_FILE,{})
        if u in users and users[u]["password"]==p:
            d=users[u]
            d["username"]=u
            return d
        return None
    def deposit_money(self):
        acc=input("Account Number: ")
        try:
            amt=float(input("Amount: "))
            if amt<=0:
                print("Amount must be positive.")
                return
        except ValueError:
            print("Invalid amount entered.")
            return
        customers=load_json(CUSTOMER_FILE,[])
        for c in customers:
            if c["Account Number"]==acc:
                if c.get("Status")=="Removed":
                    print("Account is removed/inactive.")
                    return
                c["Balance"]+=amt
                save_json(CUSTOMER_FILE,customers)
                print(f"Successfully deposited {amt}. New Balance: {c['Balance']}")
                return
        print("Account not found")
    def withdraw_any(self):
        acc=input("Account Number: ")
        try:
            amt=float(input("Amount: "))
            if amt<=0:
                print("Amount must be positive.")
                return
        except ValueError:
            print("Invalid amount entered.")
            return
        customers=load_json(CUSTOMER_FILE,[])
        for c in customers:
            if c["Account Number"]==acc:
                if c.get("Status")=="Removed":
                    print("Account is removed/inactive.")
                    return
                if c["Balance"]>=amt:
                    c["Balance"]-=amt
                    save_json(CUSTOMER_FILE,customers)
                    print(f"Successfully withdrawn {amt}. Remaining Balance: {c['Balance']}")
                else:
                    print("Insufficient Balance")
                return
        print("Account not found")
    def remove_customer(self):
        acc=input("Enter Account Number to remove: ")
        customers=load_json(CUSTOMER_FILE, [])
        found=False
        for c in customers:
            if c["Account Number"]==acc:
                if c.get("Status")=="Removed":
                    print("Customer is already removed.")
                    return
                c["Status"]="Removed"
                found=True
                break
        if found:
            save_json(CUSTOMER_FILE, customers)
            print(f"Customer with Account {acc} has been removed.")
        else:
            print("Account not found")

    def view_customers(self):
        customers=load_json(CUSTOMER_FILE,[])
        if not customers:
            print("No customers found.")
        for c in customers:
            print(c)
    def check_eligibility(self):
        acc=input("Account Number: ")
        try:
            amt=float(input("Loan Amount: "))
            if amt<=0:
                print("Loan amount must be positive.")
                return
        except ValueError:
            print("Invalid amount entered.")
            return
        customers=load_json(CUSTOMER_FILE,[])
        for c in customers:
            if c["Account Number"]==acc:
                if c.get("Status")=="Removed":
                    print("Account is removed/inactive.")
                    return
                if c["CIBIL Score"]>=750 and amt<=c["Balance"]*10:
                    print("Eligible for loan.")
                else:
                    print("Not Eligible for loan.")
                return
        print("Account not found")
    def apply_loan(self):
        acc=input("Account Number: ")
        try:
            amt=float(input("Loan Amount: "))
            if amt<=0:
                print("Loan amount must be positive.")
                return
            dur=int(input("Duration (months): "))
            if dur<=0:
                print("Duration must be positive.")
                return
        except ValueError:
            print("Invalid input for amount or duration.")
            return
        ltype=input("Loan Type: ")
        customers=load_json(CUSTOMER_FILE,[])
        cust=next((c for c in customers if c["Account Number"]==acc),None)
        if not cust:
            print("Account not found")
            return
        if cust.get("Status")=="Removed":
            print("Account is removed/inactive.")
            return
        loans=load_json(LOAN_FILE,[])
        lid=max([l["Loan ID"] for l in loans],default=0)+1
        loans.append({"Loan ID":lid,"Customer ID":cust["Customer ID"],"Account Number":acc,"Amount":amt,"Type":ltype,"Duration":dur,"Status":"Pending"})
        save_json(LOAN_FILE,loans)
        print(f"Loan Applied Successfully. Loan ID: {lid}")
    def update_loan_status(self):
        try:
            lid=int(input("Loan ID: "))
        except ValueError:
            print("Invalid Loan ID.")
            return
        loans=load_json(LOAN_FILE,[])
        for l in loans:
            if l["Loan ID"]==lid:
                print(f"Current Status: {l['Status']}")
                ch=input("1.Approve 2.Reject 3.Pending: ")
                if ch=='1':
                    l["Status"]="Approved"
                    customers=load_json(CUSTOMER_FILE,[])
                    for c in customers:
                        if c["Customer ID"]==l["Customer ID"]:
                            if c.get("Status")=="Removed":
                                print("Cannot approve loan for removed customer.")
                                return
                            c["Balance"]+=l["Amount"]
                            save_json(CUSTOMER_FILE,customers)
                    print(f"Loan {lid} Approved.")
                elif ch=='2':
                    l["Status"]="Rejected"
                    print(f"Loan {lid} Rejected.")
                elif ch=='3':
                    l["Status"]="Pending"
                    print(f"Loan {lid} marked as Pending.")
                else:
                    print("Invalid choice. No changes made.")
                    return
                save_json(LOAN_FILE,loans)
                return
        print("Loan not found")

class Admin(Data):
    def menu(self):
        while True:
            print("\n--- Admin Menu ---")
            ch=input("1.Add Employee 2.Add Customer 3.Update Permissions 4.Bank Operations 5.Logout: ")
            if ch=='1': self.add_employee()
            elif ch=='2': self.add_customer()
            elif ch=='3': self.update_designation_permissions()
            elif ch=='4': self.bank_operations()
            elif ch=='5': break
            else: print("Invalid choice.")
    def bank_operations(self):
        while True:
            print("\n--- Bank Operations (Admin) ---")
            ops_list=list(PERMISSION_MAP.keys())
            for i, op in enumerate(ops_list, 1):
                print(f"{i}. {op.replace('_', ' ').title()}")
            print(f"{len(ops_list)+1}. Back")
            try:
                ch=int(input("Choice: "))
                if ch==len(ops_list) + 1:
                    break
                if 1<=ch<=len(ops_list):
                    getattr(self, PERMISSION_MAP[ops_list[ch-1]])()
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input.")
    def add_employee(self):
        name=input("Name: ")
        username=input("Username: ")
        users=load_json(USERS_FILE,{})
        if username in users:
            print("Username already exists!")
            return
        password=input("Password: ")
        designations=load_json(DESIGNATION_FILE,{})
        if not designations:
            print("No designations defined.")
            return
        des_list=list(designations.keys())
        for i,d in enumerate(des_list,1):
            print(f"{i}. {d}")
        try:
            choice=int(input("Choice: "))
            if 1<=choice<=len(des_list):
                designation=des_list[choice-1]
            else:
                print("Invalid choice.")
                return
        except ValueError:
            print("Invalid input.")
            return
        employees=load_json(EMPLOYEE_FILE,[])
        if designation=="Assistant Manager":
            am_count=sum(1 for e in employees if e.get("Designation")=="Assistant Manager" and e.get("Status")=="Working")
            if am_count>=1:
                print("Error: Only one Assistant Manager is allowed.")
                return
                
        eid=max([e["Employee ID"] for e in employees],default=0)+1
        employees.append({"Employee ID":eid,"Name":name,"Designation":designation,"Salary":0,"Status":"Working"})
        save_json(EMPLOYEE_FILE,employees)
        users[username]={"password":password,"role":"Employee","designation":designation,"employee_id":eid}
        save_json(USERS_FILE,users)
        print(f"Employee {name} added successfully with ID {eid}.")
    def add_customer(self):
        name=input("Name: ")
        username=input("Username: ")
        users=load_json(USERS_FILE,{})
        if username in users:
            print("Username already exists!")
            return
        password=input("Password: ")
        customers=load_json(CUSTOMER_FILE,[])
        cid=max([c["Customer ID"] for c in customers],default=0)+1
        acc=f"ACC{cid}"
        customers.append({"Customer ID":cid,"Account Number":acc,"Customer Name":name,"Balance":0,"CIBIL Score":700,"Status":"Active"})
        save_json(CUSTOMER_FILE,customers)
        users[username]={"password":password,"role":"Customer","customer_id":cid,"account_number":acc}
        save_json(USERS_FILE,users)
        print(f"Customer {name} added successfully. Account Number: {acc}")
    def update_designation_permissions(self):
        designations=load_json(DESIGNATION_FILE,{})
        name=input("Designation Name: ")
        perms_input=input("Permissions (comma separated): ").split(',')
        perms={p.strip() for p in perms_input if p.strip() in PERMISSION_MAP}
        if not perms:
            print("No valid permissions provided. Valid: " + ", ".join(PERMISSION_MAP.keys()))
            return
        designations[name]={"permissions":list(perms)}
        save_json(DESIGNATION_FILE,designations)
        print(f"Permissions updated for {name}.")

class Employee(Data):
    def __init__(self,username,data):
        super().__init__(username)
        self.designation=data.get("designation")
        self.emp_id=data.get("employee_id")
    def menu(self):
        employees=load_json(EMPLOYEE_FILE,[])
        emp=next((e for e in employees if e["Employee ID"]==self.emp_id), None)
        if not emp:
            print("Employee record not found.")
            return
        if emp.get("Status")!="Working":
            print("Access Denied: You are not working.")
            return
        designations=load_json(DESIGNATION_FILE,{})
        des_data=designations.get(self.designation)
        if not des_data:
            print(f"Designation {self.designation} not found.")
            return
        perms=set(des_data.get("permissions", []))
        while True:
            print(f"\n--- Employee Menu ({self.designation}) ---")
            plist=list(perms)
            if not plist:
                print("No permissions assigned.")
                break
            for i,p in enumerate(plist,1):
                print(f"{i}. {p.replace('_',' ').title()}")
            print(f"{len(plist)+1}. Logout")
            try:
                ch=int(input("Choice: "))
                if ch==len(plist)+1:
                    break
                if 1<=ch<=len(plist):
                    getattr(self,PERMISSION_MAP[plist[ch-1]])()
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input.")

class Customer(Data):
    def __init__(self,username,data):
        super().__init__(username)
        self.cust_id=data.get("customer_id")
    def menu(self):
        while True:
            print("\n--- Customer Menu ---")
            ch=input("1.View 2.Withdraw 3.Deposit 4.Update Password 5.Logout: ")
            if ch=='1': self.view()
            elif ch=='2': self.withdraw()
            elif ch=='3': self.deposit_money()
            elif ch=='4': self.update_password()
            elif ch=='5': break
            else: print("Invalid choice.")
    def view(self):
        customers=load_json(CUSTOMER_FILE,[])
        found=False
        for c in customers:
            if c["Customer ID"]==self.cust_id:
                print("\nCustomer Details:")
                for k,v in c.items():
                    print(f"{k}: {v}")
                found=True
        if not found:
            print("Customer profile not found.")
    def withdraw(self):
        try:
            amt=float(input("Amount: "))
            if amt<=0:
                print("Amount must be positive.")
                return
        except ValueError:
             print("Invalid input.")
             return
        customers=load_json(CUSTOMER_FILE,[])
        for c in customers:
            if c["Customer ID"]==self.cust_id:
                if c["Balance"]>=amt:
                    c["Balance"]-=amt
                    save_json(CUSTOMER_FILE,customers)
                    print(f"Successfully withdrawn {amt}. Balance: {c['Balance']}")
                else:
                    print("Insufficient Balance")
                return
        print("Customer record not found")
    def update_password(self):
        old_pass=input("Old Password: ")
        if old_pass==self.password:
            new_pass=input("New Password: ")
            if new_pass:
                self.password=new_pass
            else:
                print("Password cannot be empty.")
        else:
            print("Incorrect Old Password.")

def main():
    try:
        users=load_json(USERS_FILE,{})
        if not any(u.get("role")=="Admin" for u in users.values()):
            users["manager"]={"password":"manager@123","role":"Admin"}
            save_json(USERS_FILE,users)
        designations=load_json(DESIGNATION_FILE, {})
        if not designations:
             designations={
                "Cashier":{"permissions":["view_customers","deposit_money","withdraw_any"]},
                "Loan Officer":{"permissions":["check_eligibility","apply_loan"]},
                "Assistant Manager":{"permissions":["view_customers","check_eligibility","apply_loan","update_loan_status"]}
            }
             save_json(DESIGNATION_FILE, designations)
        while True:
            print("\n=== Bank System ===")
            ch=input("1.Login 2.Exit: ")
            if ch=='1':
                u=input("Username: ")
                p=input("Password: ")
                d=Data().authenticate(u,p)
                if not d:
                    print("Invalid Username or Password.")
                    continue
                role=d.get("role")
                if role=="Admin":
                    Admin(u).menu()
                elif role=="Employee":
                    Employee(u,d).menu()
                elif role=="Customer":
                    Customer(u,d).menu()
                else:
                    print("Unknown role.")
            elif ch=='2':
                print("Exiting...")
                break
            else:
                print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__=="__main__":
    main()