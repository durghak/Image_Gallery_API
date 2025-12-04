from flask import Blueprint,jsonify,request,session
import bcrypt
import pymysql

from db import conn
 


user_bp = Blueprint('auth', __name__)

@user_bp.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Hashing password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        with conn.cursor() as cur:
            query = "INSERT INTO user(username, password) VALUES (%s, %s)"
            cur.execute(query, (username, hashed_password.decode('utf-8')))
            conn.commit()
    except pymysql.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

    return jsonify({"detail": "User added successfully"}), 201

@user_bp.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    with conn.cursor() as cur:
        query = "SELECT id, password FROM user WHERE username = %s"
        cur.execute(query, (username,))
        result = cur.fetchone()
        if not result:
            return jsonify({"error": "Invalid username or password"}), 401
        
        user_id,stored_hash= result
        

    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return jsonify({"error": "Invalid username or password"}), 401
    
    session['user_id'] = str(user_id)  # This automatically triggers flask cookie

    return jsonify({"detail": "User login successful","user_id":user_id}), 200


@user_bp.route("/logout", methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"detail": "User logged out successfully"}), 200
   