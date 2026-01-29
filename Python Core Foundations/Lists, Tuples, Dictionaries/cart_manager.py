cart={}
buyer_cart={}
total_price=0

def add_product_seller():
    product_name=input("Enter product name to add: ").capitalize()
    product_price=float(input("Enter product price: "))
    product_quantity=int(input("Enter product quantity: "))
    cart[product_name]={"price": product_price, "quantity": product_quantity}
    print(f"{product_name} added with price {product_price} and quantity {product_quantity}.")
    return

def update_product():
    product_name=input("Enter product name to update: ").capitalize()
    if product_name in cart:
        new_price=float(input("Enter new price: "))
        new_quantity=int(input("Enter new quantity: "))
        cart[product_name]={"price": new_price, "quantity": new_quantity}
        print(f"{product_name} updated with price {new_price} and quantity {new_quantity}.")
    else:
        print(f"{product_name} not found in cart.")
    return

def remove_product():
    product_name=input("Enter product name to remove: ").capitalize()
    if product_name in cart:
        del cart[product_name]
        print(f"{product_name} removed from cart.")
    else:
        print(f"{product_name} not found in cart.")
    return

def view_products():
    if cart:
        print("Products in Cart:")
        for product, details in cart.items():
            print(f"{product}: Price - {details['price']}, Quantity - {details['quantity']}")
    else:
        print("Cart is empty.")
    return
while True:
    user=input("Login (Buyer/Seller/Exit): ").capitalize()
    match user:
        case "Seller":
            while True:
                action=int(input("What do you want to do?\n 1.Add a product\n 2.Update product details\n 3.Remove a product\n 4.View products\n 5.Exit\n Enter your action: "))
                match action:
                    case 1:
                        add_product_seller()
                    case 2:
                        update_product()
                    case 3:
                        remove_product()
                    case 4:
                        view_products()
                    case 5:
                        print("Exiting Seller mode.")
                        break
                    case _:
                        print("Invalid action. Please try again.")
        case "Buyer":
            if not cart:
                print("Cart is empty. Please ask the seller to add products.")
                continue
            while True:
                view_products()
                buyer_choice=int(input("\n1.Add to cart\n2.View my cart\n3.Checkout\n4.Exit\nEnter choice: "))
                match buyer_choice:
                    case 1:
                        product_name=input("Enter product name to add to your cart: ").capitalize()
                        if product_name in cart:
                            quantity=int(input("Enter quantity: "))
                            if quantity<=cart[product_name]['quantity']:
                                print(f"{quantity} of {product_name} added to your cart.")
                                cart[product_name]['quantity']-=quantity
                                if product_name in buyer_cart:
                                    buyer_cart[product_name]['quantity']+=quantity
                                else:
                                    buyer_cart[product_name]={"price": cart[product_name]['price'], "quantity": quantity}
                            else:
                                print(f"Only {cart[product_name]['quantity']} of {product_name} available.")
                        else:
                            print(f"{product_name} not found.")
                    case 2:
                        if buyer_cart:
                            print("\nYour Cart:")
                            total=0
                            for product, details in buyer_cart.items():
                                subtotal=details['price']*details['quantity']
                                print(f"{product}: Price - {details['price']}, Quantity - {details['quantity']}, Subtotal - {subtotal}")
                                total+=subtotal
                            print(f"Total Price: {total}")
                        else:
                            print("Your cart is empty.")
                    case 3:
                        if buyer_cart:
                            total_price=0
                            for details in buyer_cart.values():
                                total_price+=details['price']*details['quantity']
                            print(f"\nCheckout successful! Total amount: {total_price}")
                            buyer_cart.clear()
                        else:
                            print("Cart is empty. Add items to checkout.")
                    case 4:
                        print("Exiting Buyer mode.")
                        break
                    case _:
                        print("Invalid choice.")
        case "Exit":
            print("\nFinal Cart:", cart)
            print("Exiting the system.")
            break
        case _:
            print("Invalid login type. Please enter Buyer, Seller, or Exit.")