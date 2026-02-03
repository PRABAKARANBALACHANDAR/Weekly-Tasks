# Day 5 Task


Exceptions, Files & JSON:
    1.Student_management_system.py
        * Student_data
            -name,id,age,grade
        * Student_login
        * Student_operations
        * Student_attendance
        * Student_announcements
        * Student_query
    2.Managers/                          
        * __init__.py
        * students_record_manager.py
            -add_student()
            -remove_student()
            -update_student()
            -view_students()
        * Students_Attendance_tracker.py
            -add_attendance()
            -remove_attendance()
            -update_attendance()
            -view_attendance()
        * announcements_manager.py
            -add_announcement()
            -remove_announcement()
            -update_announcement()
            -view_announcements()
        * query_manager.py
            -add_query()
            -remove_query()
            -update_query()
            -view_query()
    3.Exceptions/                        
        * __init__.py
        * custom_exceptions.py
     

# Day 6 Task

OOPS Fundamentals:
    1.Bank_Account_Class.py 
        *Data
            -users.json
            -employee_data.json
            -customer_data.json
            -loan_application.json
            -designations.json
        * Employee(Data)
            *Emp_data
                -name,id,salary,designation
            *Emp_login
            *Emp_operations(Role-based access)
                -add_customer()
                -remove_customer()
                -update_customer()
                -view_customers()
                -check_eligibility()
                -apply_loan()
                -update_loan_status()
                -deposit_money()
                -withdraw_any()
        * Customer (Data)
            *Cust_data
                -name,id,balance,cibil_score
            *Cust_login
            *Cust_operations
                -check_eligibility()
                -apply_loan()
                -deposit_money()
                -withdraw_any()
        * Loan (Data)
            *Loan_data
                -name,id,balance,cibil_score
            *Loan_login
            *Loan_operations
                -check_eligibility()
                -apply_loan()
                -deposit_money()
                -withdraw_any()
        * Admin (Data)
            *Admin_data
                -username,password
            *Admin_login
            *Admin_operations
                -add_customer()
                -remove_customer()
                -update_customer()
                -view_customers()
                -check_eligibility()
                -apply_loan()
                -update_loan_status()
                -deposit_money()
                -withdraw_any()
    2.Inventory_class.py
        * Products
            -name,id,price,quantity
        * Inventory_Manager
            *add_product()
                -name,price,quantity,category
                -date_added
            *remove_product()
                -name
                -del self.products[name]
            *auto_remove_expired_food()
                -name,category,date_added,sold_quantity
            *update_product()
                -name,price,quantity,category
            *view_products()
                -name,price,quantity,category
            *order_stocks()
                -name,price,quantity,category
            *calculate_refill_time()
            *record_sale()
            *recommend_discounts()
            *sold_products_report()

    
