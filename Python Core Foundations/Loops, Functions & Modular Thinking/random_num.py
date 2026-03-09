import random 
print ("Welcome to the Random Number Generator!")
lower =int (input ("Enter the lower bound: "))
upper =int (input ("Enter the upper bound: "))
random_num =random .randint (lower ,upper )
total_attempts =upper -lower +1 
count =0 
while count <total_attempts :
    count +=1 
    guess =int (input ("Guess the number: "))
    if guess <random_num :
        print (f"The number is greater than {guess }. Try again.")
    elif guess >random_num :
        print (f"The number is less than {guess }. Try again.")
    else :
        print ("Congratulations! You've guessed the correct number.")
        break 
if count ==total_attempts :
    print (f"Sorry, you've used all your attempts. The correct number was {random_num }.")
elif count ==1 :
    print ("Amazing! You guessed the number on your first try!")
elif count <=3 :
    print (f"Excellent guess! You guessed the number in {count } attempts.")
else :
    print (f"Good job! It took you {count } attempts.")
