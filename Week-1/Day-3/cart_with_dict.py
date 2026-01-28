items=['Light Bulb','Brush','Toothpaste','Shampoo','Conditioner']
prices=[100,50,30,120,150]
cart={k:v for (k,v) in zip(items,prices)}
total_price=0
while True:
    print("Items Available: ",cart)
    user_input=input("Enter an item to add to your cart(or type 'exit' to finish): ").capitalize()
    if user_input.lower()=='exit':
        print("Your Bill Amount is: ",total_price)
        print("Thank you for visiting!")
        break
    elif user_input in cart:
        total_price+=cart[user_input]
        print(f"{user_input} is added to your cart (Price: {cart[user_input]})")
    else:
        print(f"Sorry, {user_input} is not available.")