import sys 
import os 

sys .path .append (os .path .dirname (os .path .dirname (os .path .abspath (__file__ ))))

from Managers .Students_Attendance_tracker import Student 
from Exceptions .custom_exceptions import InvalidInputError 

class GradeStudent (Student ):

    def __init__ (self ,name ,department ,course =None ):

        super ().__init__ (name ,department ,course )

    def add_mark (self ,subject ,score ):

        if not (0 <=score <=100 ):

            raise InvalidInputError (f"Invalid Score: {score }. Marks must be between 0 and 100.")

        super ().add_mark (subject ,score )

        print (f"Verified and added mark for {subject }: {score }")

    def calculate_average_marks (self ):

        avg =super ().calculate_average_marks ()

        status ="PASS"if avg >=50 else "FAIL"

        return f"Average: {avg :.2f} ({status })"

if __name__ =="__main__":
    """
    Demonstration of GradeStudent class functionality.
    
    This demo shows:
    1. Creating a GradeStudent instance
    2. Adding valid marks
    3. Handling invalid input (marks > 100)
    4. Calculating average with Pass/Fail status
    5. Exception handling with try-except blocks
    """
    try :
        print ("--- Method Overriding Demo ---")

        student =GradeStudent ("Alice","Computer Science","B.Tech")
        print (f"Created student: {student .name } from {student .department }")

        print ("\n--- Adding Valid Marks ---")
        student .add_mark ("Math",95 )
        student .add_mark ("Physics",88 )

        print ("\n--- Testing Invalid Input Handling ---")
        try :

            student .add_mark ("Chemistry",150 )
        except InvalidInputError as e :

            print (f"Caught Expected Error: {e }")

        print ("\n--- Adding More Valid Marks ---")
        student .add_mark ("Chemistry",45 )

        print ("\n--- Calculating Average ---")
        print (student .calculate_average_marks ())

    except Exception as e :

        print (f"An unexpected error occurred: {e }")

"""
Key Concepts Demonstrated in This Module:

1. INHERITANCE:
   - GradeStudent inherits from Student
   - Gets all attributes and methods from parent class
   - Can add new functionality while reusing existing code

2. METHOD OVERRIDING:
   - add_mark() overrides parent to add validation
   - calculate_average_marks() overrides parent to add status
   - Uses super() to call parent methods

3. EXCEPTION HANDLING:
   - Raises InvalidInputError for invalid marks
   - Uses try-except to catch and handle errors
   - Prevents program crashes from bad input

4. INPUT VALIDATION:
   - Checks marks are within 0-100 range
   - Provides clear error messages
   - Ensures data integrity

5. ENCAPSULATION:
   - Uses methods to control data access
   - Validates before modifying internal state
   - Maintains data consistency

Usage in the Student Management System:
- This class can be used when students need enhanced grade validation
- The student_type field in registration determines if GradeStudent is used
- Provides stricter controls for critical grade data
- Demonstrates extensibility of the system architecture
"""
