# Student Management System (Day 5 Task)

## 1. Class Structure

* **Data_Records** (Base Class)
   - Base attributes (name, department) and attendance management.
* **Student** (Inherits Data_Records)
   - Core student entity with course and assigned teacher.
   - Manages marks and grade calculation.
* **Teacher** (Inherits Student)
   - Manages assigned students.
   - Capabilities: Add/Update Attendance, Add Marks.
* **Principal** (Inherits Teacher)
   - Superuser role.
   - Manages Students, Teachers, and system configurations.
* **GradeStudent** (Inherits Student) - *New in Exceptions module*
   - Specialized class demonstrating Method Overriding.
   - Overrides `add_mark` (Validation) and `calculate_average_marks` (Formatting).

## 2. Files & Modules

* **i. Student_management_system.py** (Main)
   - Central entry point.
   - Handles login (Principal/Teacher/Student) and menu navigation.
* **ii. Managers/**
   - `students_record_manager.py`: CRUD for Student records.
   - `Students_Attendance_tracker.py`: Core logic for Attendance and Person classes.
   - `announcements_manager.py`: Broadcasting system.
   - `query_manager.py`: Student-Principal Q&A system.
   - `user_manager.py`: Authentication logic.
* **iii. Exceptions/**
   - `custom_exceptions.py`: Application-specific errors (RecordExists, InvalidInput).
   - `Student_Grades.py`: Demonstrates inheritance and polymorphism via `GradeStudent`.
* **iv. Data/**
   - `users.json`: Stores credentials (`username`, `password`, `role`).

## 3. Use of OOPS Concepts

* **Inheritance**: Multilevel (`Data_Records` -> `Student` -> `Teacher` -> `Principal`).
* **Polymorphism**: `GradeStudent` overrides methods from parent `Student`.
* **Encapsulation**: Managers encapsulate logic (e.g., `attendance_manager` handles all attendance storage).
* **Abstraction**: `Data_Records` serves as a blueprint for all person entities.

## 4. Workflows

* **Principal**: Full control. Can register students/teachers, view all data, and post announcements.
* **Teacher**: Limited to assigned students. Can mark attendance and input grades.
* **Student**: Viewer role. Can check own attendance, grades, and submit queries.

---

# Bank & Inventory Systems (Day 6 Task)

## A. OOPS Fundamentals - Bank System

### 1. Class Structure
* **Data** (Base Class)
   - Handles Json Load/Save, Authentication (`password` property), and common operations.
* **Admin** (Inherits Data)
   - System Administrator. Adds Customers/Employees, manages permissions.
* **Employee** (Inherits Data)
   - Bank Staff. Operations defined by Designation permissions (e.g., Cashier vs Loan Officer).
* **Customer** (Inherits Data)
   - End-user. Can View Balance, Deposit, Withdraw.
* **Loan** (Data Entity)
   - Represents loan applications and status.

### 2. Files
* **Bank_Account_Class.py**: Contains all classes (`Data`, `Admin`, `Employee`, `Customer`, `Loan`) and logic.
* **Data Files**: `users.json`, `customer_data.json`, `loan_application.json`, `designations.json`.

### 3. OOPS Concepts
* **Method Overriding**: `__init__` and `menu()` methods are overridden in child classes.
* **Properties**: `password` is managed via `@property` for secure access.
* **Dynamic Dispatch**: `getattr(self, ...)` used to dynamically call methods based on permissions.

### 4. Walkthrough
1.  **Admin**: Log in -> Add Customer -> Add Employee (Assign Role/Designation).
2.  **Employee**: Log in -> Perform allowed actions (Check Eligibility, Approve Loan).
3.  **Customer**: Log in -> Apply for Loan -> Withdraw/Deposit funds.

## B. OOPS Fundamentals - Inventory System

### 1. Class Structure
* **Products**
   - Data class holding Name, Price, Qty, Category, Date Added, Sold Qty.
* **Inventory_Manager**
   - Logic Controller. Manages the `products` dictionary.
   - Handles Add/Update/Remove, Sales, and Reporting.

### 2. Files
* **Inventory_class.py**: Single-file solution containing both classes and the main menu loop.

### 3. Key Logic
* **Auto-Remove**: Automatically deletes "Food" category items older than 3 days.
* **Refill Calculation**: Estimates days until stockout based on daily sales rate.
* **Discount Recommendation**: Suggests discounts for old stock (>30 days) with low sales.

### 4. Workflows
1.  **Management**: Add products to inventory -> Update details (Price/Qty).
2.  **Sales**: Record a sale -> Updates Stock & Sold Count.
3.  **Analysis**: Generate Sales Report, check Refill times.

# Advanced OOPS & Design Thinking - Employee Management System

## 1. Class Structure

* **Data** (Abstract Class)
   - Base attributes and utility methods
* **Managers** (Inherits Data)
   - Roles: CEO, CTO, COO, CFO, HR
   - **CEO**: The Admin/Superuser. Can manage other C-Level managers (CRUD). Restricted from direct HR duties (Employee CRUD).
   - **CTO**: Allocates tasks using Project/Task Allocator. Updates project status.
   - **COO**: Managerial oversight. Calculates employee performance (Tasks + Attendance). Suggests promotions.
   - **CFO**: Financials. Manages salaries, increments, and calculates company revenue based on completed projects.
   - **HR**: Employee Management (CRUD), Attendance management, Leave Request Approvals.
* **Admin** (Inherits Managers)
   - Specialized Manager class for System Administration (CEO role).
* **Employees** (Inherits Managers)
   - Staff with Levels 1-3.
   - Associated with a Department and Team.
   - Attributes: Experience Level, Leaves, Tasks, Performance Score (Diff Sum).

## 2. Files & Modules

* **i. Employee Management System.py** (Main)
   - Central entry point.
   - Handles Login and directs users to role-specific portals (Admin/CEO, Manager, Employee).
* **ii. core/task_allocator.py**
   - Allocates projects to teams based on Department compatibility, Team Size (<6), and Experience Level vs. Difficulty.
   - Moves allocated projects from `projects.json` to `tasks.json`.
* **iii. core/attendance.py**
   - Manages daily attendance records.
   - **Auto-create**: Created instantly when a new employee is registered.
   - **Views**: All employees, specific employee history.
   - **Calculations**: Attendance percentage logic.
* **iv. core/employees.py**
   - CRUD Operations for Employees.
   - Views: All, Grouped by Team, Sorted by Performance (Descending).
* **v. core/leave_requests.py**
   - Handles leave submissions.
   - **Validation**: CEO/CTO/COO/CFO can **View** requests; ONLY **HR** can **Approve/Reject**.
* **vi. core/managers.py**
   - Implementation of C-Level roles and shared manager logic.
   - Enforces Singleton constraint (Only 1 CEO, 1 CTO, etc.).
* **vii. core/project.py**
   - Project entity management (Title, Dept, Duration, Difficulty).
   - Status tracking (Pending -> In-Progress -> Completed).
* **viii. core/team.py**
   - Team structure management.
   - Enforces Max Team Size=6 (Leader + 5 Members).
* **ix. Data Files (.json)**
   - `managers.json`, `employees.json`, `projects.json`, `tasks.json`, `teams.json`, `attendance.json`, `leave_requests.json`.

## 3. Use of OOPS Concepts

* **Abstraction**: `Data` class provides a template for common data operations.
* **Encapsulation**: Private attributes (`_name`, `_salary`) protected by properties.
* **Inheritance**: Multilevel inheritance (`Data` -> `Managers` -> `Employees`).
* **Polymorphism**: Method overriding for `create()`, `update()` across different classes.
* **Singleton Pattern**: Ensures uniqueness of C-Suite roles.

## 4. Data & Persistence

* **Storage**: Data stored as JSON objects.
* **Initialization**: System auto-initializes with a default Admin if none exists.
* **Constraints**: 
   - No duplicates allowed (ID checks).
   - Singleton C-Roles.
   - Allocated tasks move to separate storage (`tasks.json`).

## 5. Exceptions

* **Handling**: Robust `try-except` blocks for file I/O and user input.
* **Custom Errors**: `ValueError` for duplicates, `PermissionError` for unauthorized actions (e.g., CEO trying to approve leave).
* **Interrupts**: Handles `KeyboardInterrupt` for graceful exit.

## 6. Detailed Walkthrough

### Login & Navigation
1.  **System Start**: Checks for Admin. If missing, creates default (`admin`/`admin123`).
2.  **Login**: User enters credentials. System detects role (Manager/Employee) and routes to correct portal.

### Manager Workflows
*   **CEO**: Creates other managers (CTO, HR, etc.). Views system status.
*   **HR**: 
    -   **Add Employee**: Enter details -> System creates Employee -> **Auto-creates Attendance**.
    -   **Attendance**: View records, calculate %.
    -   **Leaves**: View Pending requests -> Approve/Reject.
*   **CTO**:
    -   **Project**: Add new project.
    -   **Allocation**: Run allocator. System matches project to suitable team -> Moves to `tasks.json`.
*   **COO**:
    -   **Performance**: Select Employee -> View Score (Tasks + Attendance).
    -   **Promotion**: Check eligibility based on score/level.
*   **CFO**:
    -   **Finance**: Update Salary.
    -   **Revenue**: Calculate total revenue from completed projects.

### Employee Workflows
*   **Profile**: View salary, leaves, performance.
*   **Actions**: Request Leave (Status set to 'Pending').