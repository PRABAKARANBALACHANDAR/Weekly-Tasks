std_name =input ("Enter Student Name: ")
avg_marks =0 
for i in range (3 ):
    std_marks =int (input (f"Enter Marks of Subject {i }: "))
    avg_marks +=std_marks 
if avg_marks /3 >=80 :
    print (f"{std_name }'s Grade is A")
elif avg_marks /3 >=60 :
    print (f"{std_name }'s Grade is B")
elif avg_marks /3 >=40 :
    print (f"{std_name }'s Grade is C")
else :
    print (f"{std_name }'s Grade is Fail")
