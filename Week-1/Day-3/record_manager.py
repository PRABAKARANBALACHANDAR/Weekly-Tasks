student_records={"John": {"age": 20, "grade": "A"}}

def operations(choice):
    if choice=="create":
        name=input("Enter student name: ").capitalize()
        age=int(input("Enter age: "))
        grade=input("Enter grade: ").upper()
        student_records[name]={"age": age, "grade": grade}
        print("\nRecord Created Successfully")
        print("Name :", name)
        print("Age  :", age)
        print("Grade:", grade)
    elif choice=="read":
        name=input("Enter student name to view details: ").capitalize()
        if name not in student_records:
            print("No records found for the student.")
            return
        print("\nStudent Record")
        print("Name :", name)
        print("Age  :", student_records[name]["age"])
        print("Grade:", student_records[name]["grade"])
    elif choice=="update":
        name=input("Enter student name to update details: ").capitalize()
        if name not in student_records:
            print("No records found for the student.")
            return
        student_records[name]["age"]=int(input("Enter new age: "))
        student_records[name]["grade"]=input("Enter new grade: ").upper()
        print("\nRecord Updated Successfully")
        print("Name :", name)
        print("Age  :", student_records[name]["age"])
        print("Grade:", student_records[name]["grade"])
    elif choice=="delete":
        name=input("Enter student name to delete details: ").capitalize()
        if name not in student_records:
            print("No records found for the student.")
            return
        del student_records[name]
        print("\nRecord Deleted Successfully")
        print(student_records)
    else:
        print("Invalid choice. Please choose create, read, update, or delete.")
        
while True:
    user_choice=input("Choose an operation (create, read, update, delete) or type 'exit' to quit: ").lower()
    if user_choice=="exit":
        print("\nFinal Student Records:", student_records)
        print("Exiting the record manager.")
        break
    operations(user_choice)
