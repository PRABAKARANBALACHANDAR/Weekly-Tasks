class Task:
    def __init__(self, task_name, dept, difficulty, duration_days):
        self.task_name=task_name
        self.dept=dept
        self.difficulty=difficulty
        self.duration_days=duration_days


class Employee:
    def __init__(self, name, years_of_exp, dept, team_num):
        self.name=name
        self.years_of_exp=years_of_exp
        self.dept=dept
        self.team_num=team_num


class Employees:
    def __init__(self):
        self.employees={}

    def add_employee(self, name, years_of_exp, dept, team_num):
        name=name.capitalize()
        if name in self.employees:
            print(f"Employee {name} already exists.")
            return False
        print(f"Adding employee {name}.")
        self.employees[name]=Employee(name, years_of_exp, dept, team_num)
        return True

    def get_employee(self, name):
        return self.employees.get(name.capitalize())


class TaskAllocator:
    def __init__(self):
        self.tasks=[]

    def add_task(self, task_name, dept, difficulty, duration_days):
        task=Task(task_name, dept, difficulty, duration_days)
        self.tasks.append(task)

    def allocate_tasks(self, employees):
        allocation={}
        for employee_name, employee in employees.employees.items():
            allocation[employee_name]=[]
            emp_dept=employee.dept
            emp_exp=employee.years_of_exp

            suitable_tasks=[task for task in self.tasks if task.dept==emp_dept and emp_exp >= task.difficulty and task.difficulty <= 3]
            suitable_tasks.sort(key=lambda x: (x.difficulty, x.duration_days))

            allocated_tasks=[]
            for task in suitable_tasks:
                allocation[employee_name].append(task.task_name)
                allocated_tasks.append(task)

            for task in allocated_tasks:
                if task in self.tasks:
                    self.tasks.remove(task)

        return allocation

    def get_remaining_tasks(self):
        return [task.task_name for task in self.tasks]

    def print_allocation(self, allocation):
        for employee_name, tasks in allocation.items():
            print(f"\nTasks allocated to {employee_name}:")
            if tasks:
                for task in tasks:
                    print(f" - {task}")
            else:
                print(" No tasks allocated.")

    def print_remaining_tasks(self):
        remaining_tasks=self.get_remaining_tasks()
        print("\nRemaining unallocated tasks:")
        if remaining_tasks:
            for task in remaining_tasks:
                print(f" - {task}")
        else:
            print(" All tasks have been allocated.")

    def is_team_available(self, employees, team_num):
        return any(employee.team_num==team_num for employee in employees.employees.values())


def main():
    employees=Employees()
    task_allocator=TaskAllocator()

    while True:
        print("\nTask Allocation System")
        print("1. Add Employee")
        print("2. Add Task")
        print("3. Allocate Tasks")
        print("4. View Remaining Tasks")
        print("5.Teams Availability")
        print("6. Exit")

        choice=input("Enter your choice: ")

        if choice=='1':
            try:
                name=input("Enter employee name: ")
                years_of_exp=int(input("Enter years of experience: "))
                dept=input("Enter department: ").capitalize()
                team_num=int(input("Enter team number: "))
            except ValueError:
                print("Invalid input. Please enter numbers for experience and team number.")
                continue
            employees.add_employee(name, years_of_exp, dept, team_num)

        elif choice=='2':
            try:
                task_name=input("Enter task name: ")
                dept=input("Enter department: ").capitalize()
                difficulty=int(input("Enter difficulty (1-5): "))
                duration_days=int(input("Enter duration_days (in hours): "))
            except ValueError:
                print("Invalid input. Please enter numeric values for difficulty and duration.")
                continue
            task_allocator.add_task(task_name, dept, difficulty, duration_days)

        elif choice=='3':
            allocation=task_allocator.allocate_tasks(employees)
            task_allocator.print_allocation(allocation)

        elif choice=='4':
            task_allocator.print_remaining_tasks()

        elif choice=='5':
            print("Exiting Task Allocation System.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__=='__main__':
    main()
