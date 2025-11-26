from flask import Flask,jsonify,request
import flask_cors
import pymysql
from flask_cors import CORS



app = Flask(__name__)
CORS(app)  # Allow all origins

try:
    conn=pymysql.connect(
        host='localhost',
        user='root',
        password='Durgha16!',
        database="photo_gallery")
    print("DataBase Connected successfully")
except :
    print("database not connected")   
@app.route("/")
def home():
    return jsonify({"name":"Durgha"})

@app.route("/register",methods=['POST'])
def register():
    data = request.get_json() 
    username = data.get('username')
    password = data.get('password')
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    try:
        with conn.cursor() as cur:
            query = "INSERT INTO user(username, password) VALUES (%s, %s)"
            cur.execute(query, (username, password))
            conn.commit()
    except pymysql.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

   
   
    return jsonify({"detail":"user added successfully"})

@app.route("/login",methods=['POST'])
def login():
    data = request.get_json() 
    username = data.get('username')
    password = data.get('password')
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    with conn.cursor() as cur:
        query = "SELECT username,password FROM user WHERE username = %s"
        cur.execute(query, (username,))
        result = cur.fetchone()
        if not result:
            return jsonify({"error": "Invalid username or password"}), 401
        if result[1] != password:
            return jsonify({"error": "Invalid username or password"}), 401

        
    return jsonify({"detail":"user login successfully"})




if __name__ == '__main__':
    app.run(debug=True)


