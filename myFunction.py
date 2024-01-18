import pandas as pd
import pymysql as pm
import pandas as pd

def read_CSV(path):
    """輸入CSV檔的路徑 return其內容的df"""
    data = pd.read_csv(path, encoding="utf-8")
    df = pd.DataFrame(data)
    return df



def read_SQL(mydb, table):
    """輸入db,table, return 全部內容(不含column)"""
    conn = pm.connect(host="localhost", port=3306, user="Ted", password="123456", charset="utf8", db=mydb)
    cursor = conn.cursor()
    sql = "select * from {}".format(table)
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return data



def update_faces(mydb,table,id,name):
    conn = pm.connect(host="localhost", port=3306, user="Ted", password="123456", charset="utf8", db=mydb)
    cursor = conn.cursor()
    sql = f"insert into {table} (id,name) values ({id},'{name}')"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def update_person(mydb,table,account,password,email,phone):
    conn = pm.connect(host="localhost", port=3306, user="Ted", password="123456", charset="utf8", db=mydb)
    cursor = conn.cursor()
    sql = f"insert into {table} (account,password,email,phone) values ('{account}','{password}','{email}','{phone}')"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def update_balance(balance, cost, username):
    conn = pm.connect(host="localhost", port=3306, user="Ted", password="123456", charset="utf8", db='topics')
    cursor = conn.cursor()
    new_balance = int(balance) - int(cost)
    sql = f"UPDATE account_info SET balance = '{new_balance}' WHERE name = '{username}';"
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


    
