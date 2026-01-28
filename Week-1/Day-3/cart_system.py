items=['Light Bulb','Brush','Toothpaste','Shampoo','Conditioner']
cart=[]
def add_to_cart(item):
    if item in items:
        cart.append(item)
        return f"{item} has been added to your cart."
    else:
        return f"Sorry, {item} is not available."
while True:
    print("Items Available: ",items)
    user_input=input("Enter an item to add to your cart (or type 'exit' to finish): ").capitalize()
    if user_input.lower()=='exit':
        print("Final Cart:", cart)
        break
    print(add_to_cart(user_input))
