import mysql.connector


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


    def add_item(self, product_name, quantity):
        product = self.database.get_product(product_name)
        if product:
            self.items.append({"product": product, "quantity": quantity})


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


    def print_receipt(self):
        print("===== Receipt =====")
        for item in self.items:
            print(f"{item['product'].name} x{item['quantity']}: ${item['product'].money * item['quantity']}")
        print("===================")
        print(f"Total: ${self.calculate_total()}")
        print("===================")


database = Database()
# 創建一個購物車
cart = ShoppingCart(database)

# 加入商品到購物車

while True:
    i =input("商品名稱")
    if i.lower() == "q":
        break
    cart.add_item(i, 1)

# 列印收據
cart.print_receipt()


# =======================================
# 創建一些商品
# product1 = Product("Laptop", 1000)
# product2 = Product("Phone", 500)
# product3 = Product("Headphones", 100)
# # 移除一個商品
# # cart.remove_item("Phone")
