student_records={}
id_list=[]
missing_id=[]
def generate_id():
    if not id_list:
        return 1
    else:
        min_id=min(id_list)
        max_id=max(id_list)
        missing_id.clear()
        for value in range(min_id, max_id+1):
            if value not in id_list:
                missing_id.append(value)
        if missing_id:
            return missing_id[0]   
        else:
            return max_id+1
def create_record():
    id_num=generate_id()
    name=input("Enter student name: ").capitalize()
    if id_num in student_records:
        print("Record ID already exists.")
        return
    for student_id, details in student_records.items():
        if details['name'] == name:
            print(f"Record already exists for {name} with ID {student_id}.")
            opt=input("Do you want to update the existing record? (yes/no): ").lower()
            if opt=='yes':
                update_record()
            return
    age=int(input("Enter age: "))
    grade=input("Enter grade: ").upper()
    course=input("Enter course enrolled: ").upper()
    student_records[id_num]={"name":name,"age": age, "grade": grade, "course": course}
    id_list.append(id_num)
    print("\nRecord Created Successfully")
    print("id   :", id_num)
    print("Name :", name)
    print("Age  :", age)
    print("Grade:", grade)
    print("Course:", course)

def display_record():
    if not student_records:
            print("No records available.")
            return
    choice=input("Do you want to view all records or a specific student? (all/specific): ").lower()
    if choice=="all":
        print("\nAll Student Records:")
        for id_num, details in student_records.items():
            print(f"ID: {id_num}, Name: {details['name']}, Age: {details['age']}, Grade: {details['grade']}, Course: {details['course']}")
    elif choice=="specific":
        id_num=int(input("Enter student ID to view details: "))
        if id_num not in student_records:
            print("No records found for the student.")
            return
        details=student_records[id_num]
        print(f"\nStudent Record: ID: {id_num}, Name: {details['name']}, Age: {details['age']}, Grade: {details['grade']}, Course: {details['course']}")
        
def update_record():
    id_num=int(input("Enter student ID to update details: "))
    if id_num not in student_records:
        print("No records found for the student.")
        return
    choice=input("What do you want to update? (age/grade/course): ").lower()
    if choice=="age":
        student_records[id_num]["age"]=int(input("Enter new age: "))
    elif choice=="grade":
        student_records[id_num]["grade"]=input("Enter new grade: ").upper()
    elif choice=="course":
        student_records[id_num]["course"]=input("Enter new course: ").upper()
    details=student_records[id_num]
    print(f"\nRecord Updated Successfully")
    print("ID   :", id_num)
    print("Name :", details['name'])
    print("Age  :", details['age'])
    print("Grade:", details['grade'])
    print("Course:", details['course'])
    


def delete_record():
    id_num=int(input("Enter student ID to delete details: "))
    if id_num not in student_records:
        print("No records found for the student.")
        return
    del student_records[id_num]
    id_list.remove(id_num)
    print("\nRecord Deleted Successfully")
    print("Remaining records:", student_records)
def operations(choice):
    match choice:
        case 1:
            create_record()
        case 2:
            display_record()
        case 3:
            update_record()
        case 4:
            delete_record()
        case _:
            print("Invalid choice. Please choose create, read, update, or delete.")
        
while True:
    user_choice=int(input("Choose an operation:\n1.Create\n2.Read\n3.Update\n4.Delete\n5.Exit\nEnter your choice:"))
    if user_choice==5:
        print("\nFinal Student Records:", student_records)
        print("Exiting the record manager.")
        break
    operations(user_choice)
