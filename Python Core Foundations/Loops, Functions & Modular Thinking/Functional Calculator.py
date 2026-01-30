class operations:
    def add(self,a, b):
        return a + b

    def subtract(self,a, b):
        return a - b

    def multiply(self,a, b):
        return a * b

    def divide(self,a, b):
            return "Error! Division by zero." if b==0 else a / b

class advanced_operations(operations):
    def power(self,a, b):
        return a ** b

    def modulus(self,a, b):
        return a % b
    
class Calculator(advanced_operations):
    def calculate(self, operation, a, b):
        match operation:
            case '+':
                return self.add(a, b)
            case '-':
                return self.subtract(a, b)
            case '*':
                return self.multiply(a, b)
            case '/':
                return self.divide(a, b)
            case '^':
                return self.power(a, b)
            case '%':
                return self.modulus(a, b)
            case _:
                return "Invalid operation."
        
if __name__=="__main__":
    calc=Calculator()
    print("Functional Calculator")
    while True:
        choice=input("Do you want to perform a calculation? (yes/no): ").lower()
        if choice=='no':
            print("Exiting the calculator...")
            break
        print("Available operations: add(+), subtract(-), multiply(*), divide(/), power(^), modulus(%)")
        operation=input("Enter operation: ")
        try:
            a=float(input("Enter first number: "))
            b=float(input("Enter second number: "))
            result=calc.calculate(operation, a, b)
            print(f"Result: {result}")
        except ValueError:
            print("Invalid input! Please enter numeric values for numbers.")