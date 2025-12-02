import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Durgha16!',
        database="photo_gallery"
    )
    print("Database Connected successfully")
except Exception as e:
    print("Database not connected:", e)