import sys
import os

# Create path to handle imports from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Managers.Students_Attendance_tracker import Student
from Exceptions.custom_exceptions import InvalidInputError

class GradeStudent(Student):
    def __init__(self, name, department, course=None):
        super().__init__(name, department, course)
    
    # Method Overriding: Adding validation logic before calling parent method
    def add_mark(self, subject, score):
        if not (0<=score<=100):
            raise InvalidInputError(f"Invalid Score: {score}. Marks must be between 0 and 100.")
        super().add_mark(subject, score)
        print(f"Verified and added mark for {subject}: {score}")

    # Method Overriding: Changing the behavior to return a formatted status string
    def calculate_average_marks(self):
        avg=super().calculate_average_marks()
        status="PASS" if avg>=50 else "FAIL"
        return f"Average: {avg:.2f} ({status})"

if __name__=="__main__":
    try:
        print("--- Method Overriding Demo ---")
        student=GradeStudent("Alice", "Computer Science", "B.Tech")
        
        # Valid marks
        student.add_mark("Math", 95)
        student.add_mark("Physics", 88)
        
        # Invalid marks (Demonstrating Override Validation)
        try:
            student.add_mark("Chemistry", 150)
        except InvalidInputError as e:
            print(f"Caught Expected Error: {e}")
            
        # Valid mark to correct it
        student.add_mark("Chemistry", 45)
        
        # Overridden Calculation
        print(student.calculate_average_marks())
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
