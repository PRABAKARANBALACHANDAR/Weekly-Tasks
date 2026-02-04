from datetime import datetime, timedelta

class Products:
    def __init__(self, name, price, quantity, category):
        self.name=name
        self.price=price
        self.quantity=quantity
        self.category=category
        self.date_added=datetime.now()
        self.sold_quantity=0

    def __str__(self):
        return f"Name: {self.name}, Price: {self.price}, Qty: {self.quantity}, Cat: {self.category}, Date: {self.date_added.strftime('%Y-%m-%d')}"

class Inventory_Manager:
    def __init__(self):
        self.products={}
        self.max_quantity_limit=100

    def add_product(self):
        name=input("Enter Name: ").capitalize()
        if name in self.products:
            self.update_product()
            return

        price=float(input("Enter Price: "))
        quantity=int(input("Enter Quantity: "))
        category=input("Enter Category: ").capitalize()
        
        if quantity > self.max_quantity_limit:
            print("Quantity exceeds limit. Stop adding.")
            return

        self.products[name]=Products(name, price, quantity, category)
        print(f"Product {name} added.")

    def update_product(self):
        name=input("Enter Product Name to Update: ").capitalize()
        
        if name in self.products:
            p=self.products[name]
            print(f"Updating {name}. Press Enter to keep current value.")
            
            p_price=input(f"Price ({p.price}): ")
            if p_price: p.price=float(p_price)
            
            p_qty=input(f"Quantity ({p.quantity}): ")
            if p_qty: 
                new_qty=int(p_qty)
                if new_qty > self.max_quantity_limit:
                    print("Cannot update. Max quantity reached.")
                else:
                    p.quantity=new_qty
            
            p_cat=input(f"Category ({p.category}): ")
            if p_cat: p.category=p_cat.capitalize()
            
            print("Updated successfully.")
        else:
            print("Product not found.")

    def remove_product(self):
        name=input("Enter Product to Remove: ").capitalize()
        if name in self.products:
            del self.products[name]
            print("Removed.")
        else:
            print("Not found.")

    def auto_remove_expired_food(self):
        to_remove=[]
        for name, p in self.products.items():
            if p.category=="Food":
                delta=datetime.now() - p.date_added
                if delta.days>=3:
                    to_remove.append(name)
        
        for name in to_remove:
            del self.products[name]
            print(f"Removed expired food: {name}")

    def view_products(self,mode):
        if mode=='1':
            cat=input("Enter Category: ").capitalize()
            products_to_view=[p for p in self.products.values() if p.category==cat]
        elif mode=='2':
            date_str=input("Enter Date (YYYY-MM-DD): ")
            try:
                query_date=datetime.strptime(date_str, "%Y-%m-%d").date()
                products_to_view=[p for p in self.products.values() if p.date_added.date()==query_date]
            except ValueError:
                print("Invalid Date.")
        else:
            products_to_view=self.products.values()
        
        for p in products_to_view:
            warning=" [LOW STOCK WARNING]" if p.quantity < 5 else ""
            print(f"{p}{warning}")

    def order_stocks(self):
        for p in self.products.values():
            if p.quantity < 5:
                choice=input(f"Order 10 items for {p.name}? (y/n): ")
                if choice.lower()=='y':
                    p.quantity += 10
                    print(f"Ordered 10 items for {p.name}. Current: {p.quantity}")
                else:
                    print(f"Not ordering {p.name}")

    def calculate_refill_time(self):
        for p in self.products.values():
            if p.sold_quantity > 0:
                days_active=(datetime.now() - p.date_added).days + 1
                daily_rate=p.sold_quantity / days_active
                days_left=p.quantity / daily_rate if daily_rate > 0 else 999
                print(f"{p.name}: Estimated refill in {days_left:.1f} days.")
            else:
                print(f"{p.name}: No sales data to calculate refill.")

    def record_sale(self):
        view_products(1)
        name=input("Enter Product Sold: ").capitalize()
        if name in self.products:
            qty=int(input("Quantity Sold: "))
            if self.products[name].quantity>=qty:
                self.products[name].quantity -= qty
                self.products[name].sold_quantity += qty
                print("Sale recorded.")
            else:
                print("Insufficient stock.")
        else:
            print("Not found.")

    def recommend_discounts(self):
        for p in self.products.values():
            days_old=(datetime.now() - p.date_added).days
            if days_old > 30 and p.sold_quantity < 5:
                print(f"Recommend discount for {p.name}. Old stock.")

    def sold_products_report(self):
        print("Sold Products Report:")
        for p in self.products.values():
            if p.sold_quantity > 0:
                print(f"{p.name}: Sold {p.sold_quantity}")

    def menu(self):
        while True:
            self.auto_remove_expired_food()
            print("\n=== Inventory Management System ===")

            c=input("1. Add Product\n2. Update Product\n3. Remove Product\n4. View Products\n5. Record Sale\n6. Order Stocks\n7. Calculate Refill\n8. Recommend Discounts\n9. Sales Report\n10. Exit\nEnter choice: ")
            if c=='1': 
                self.add_product()
            elif c=='2': 
                self.update_product()
            elif c=='3': 
                self.remove_product()
            elif c=='4': 
                mode=input("View by (1)Category or (2)Date? ")
                self.view_products(mode)
            elif c=='5': 
                self.record_sale()
            elif c=='6': 
                self.order_stocks()
            elif c=='7': 
                self.calculate_refill_time()
            elif c=='8': 
                self.recommend_discounts()
            elif c=='9': 
                self.sold_products_report()
            elif c=='10': 
                break

if __name__=="__main__":
    manager=Inventory_Manager()
    manager.menu()