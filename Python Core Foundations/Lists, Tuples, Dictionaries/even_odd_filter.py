print ("Even/odd Filter System")
while True :
    num =int (input ("Enter a number: "))
    result ="Even"if num %2 ==0 else "Odd"
    print (f"The number {num } is {result }.")
    cont =input ("Do you want to continue? (yes/no): ").lower ()
    if cont !='yes':
        print ("Exiting...")
        break 
    else :
        print ("Continuing...")
