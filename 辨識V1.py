from ultralytics import YOLO
import mysql.connector
from time import time

model = YOLO('shop_v3.pt')  
# ================================
conn = mysql.connector.connect(
    host='localhost',           # 連線主機名稱
    user='root',                # 登入帳號
    password='123456',  # 登入密碼
    database='shore items',
)
cursor = conn.cursor()
# ================================
results= model(source=0,show=True,conf=0.8,save=True,verbose=False, stream=True)
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
            cursor.execute("SELECT * FROM items WHERE name = %s", (n,))
            data = cursor.fetchone()
            if data:
                if data[1] == n: 
                    # id = data[0]
                    name = data[1]
                    money = data[2]
                    # print(f"ID: {id}")
                    print(f"商品名稱: {name}")
                    print(f"價錢: {money}")

# ==========超過3秒沒辨識物品歸零============
        if time() - start_time > 3:
            frame_count = 0
            start_time = time()