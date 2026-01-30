import re
pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
input_email=input("Enter your email address: ")
if re.match(pattern, input_email):
    print("Valid email address")   
else:
    print("Invalid email address")