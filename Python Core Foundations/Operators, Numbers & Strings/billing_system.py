menu ={'BIRYANI':150 ,'FRIED RICE':120 ,'CURRY':100 ,'PIZZA':200 ,'BURGER':80 }
print ("Welcome to the Billing System\nMenu:\n",menu )
total_bill =0 
while True :
    item =input ("Enter the item you want to order (or type 'done' to finish): ")
    item =item .upper ()
    if item .lower ()=='done':
        print (f"Your total bill is: {total_bill }")
        break 
    if item in menu :
        quantity =int (input (f"Enter quantity of {item }: "))
        total_bill +=menu [item ]*quantity 
        print (f"Added {quantity } x {item } to your bill.")
    else :
        print ("Item not found in menu.")
