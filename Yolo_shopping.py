from ultralytics import YOLO
import mysql.connector
from time import time


####################################
class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',           # 連線主機名稱
            user='root',                # 登入帳號
            password='123456',  # 登入密碼
            database='shore items',
        )
        self.cursor = self.conn.cursor()

    def add_product(self, product):
        query = "INSERT INTO items (ID, name, money) VALUES (%s, %s, %s)"
        values = (product.ID, product.name, product.money)
        self.cursor.execute(query, values)
        self.conn.commit()

    def get_product(self, product_name):
        query = "SELECT * FROM items WHERE name = %s"
        values = (product_name,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result:
            ID, name, money = result
            return Product(ID, name, money)
        else:
            return None
# ================================
    def close_connection(self):
        self.cursor.close()
        self.conn.close()
# ================================
class Product:
    def __init__(self, ID, name, money):
        self.ID = ID
        self.name = name
        self.money = money
# ================================

class ShoppingCart:
    def __init__(self, database):
        self.items = []
        self.database = database

# ==========將商品加入購物車=====================
    def add_item(self, product_name, quantity):
        product = self.database.get_product(product_name)
        if product:
            for item in self.items:
                if item["product"].name == product_name:
                    # Update the quantity if the product is already in the cart
                    item["quantity"] += quantity
                    break
            else:
                # If the product is not in the cart, add a new entry
                self.items.append({"product": product, "quantity": quantity})

# ==========將商品移出購物車=====================
    def remove_item(self, product_name):
        for item in self.items:
            if item["product"].name == product_name:
                self.items.remove(item)
                break


    def calculate_total(self):
        total = 0
        for item in self.items:
            total += item["product"].money * item["quantity"]
        return total

# =============列印收據===========
    def print_receipt(self):
        print("===== Receipt =====")
        for item in self.items:
            print(f"{item['product'].name} x{item['quantity']}: ${item['product'].money * item['quantity']}")
        print("===================")
        print(f"Total: ${self.calculate_total()}")
        print("===================")



####################################
model = YOLO('shop_v3.pt') 


database = Database() # 創建資料庫

cart = ShoppingCart(database) # 創建購物車

results= model(source=0,show=True,conf=0.75,save=True,verbose=False, stream=True)
names = model.names
display_threshold = 20
frame_count = 0
start_time = time()

# =========辨識商品後去資料庫抓取商品名稱及價格=========
for r in results:
    for c in r.boxes.cls:
        frame_count+=1
        print(frame_count)
        
        if frame_count == display_threshold:
            n=names[int(c)]
            frame_count = 0 
            database.cursor.execute("SELECT * FROM items WHERE name = %s", (n,))
            data = database.cursor.fetchone()
            if data:
                product = database.get_product(n)
                if product:
                    print(f"商品名稱: {product.name}")
                    print(f"價錢: {product.money}")
                    
                    while True:
                        i = input(f"商品名稱 {product.name} (q to quit, c to checkout): ")
                        cart.add_item(product.name, 1)
                        if i.lower() == "q":
                            break  # Break out of the loop when 'q' is entered
                        elif i.lower() == "c":
                            # Print the receipt and reset the shopping cart
                            cart.print_receipt()
                            cart = ShoppingCart(database)
                            break



# ==========超過5秒沒辨識物品歸零============
        if time() - start_time > 5:
            frame_count = 0
            start_time = time()

# 列印收據
cart.print_receipt()

database.close_connection()