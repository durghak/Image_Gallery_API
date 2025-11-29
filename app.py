from flask import Flask,jsonify,request,session
import flask_cors
import pymysql
import bcrypt
from flask_cors import CORS



app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:3000"]}}
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True

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

import bcrypt

@app.route("/register", methods=['POST'])
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
from flask import make_response
@app.route("/login", methods=['POST'])
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

@app.route("/folders/add", methods=['POST'])
def folder():
    # Check if user is logged in by verifying the session
    if 'user_id' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    user_id = session['user_id']  # Get user_id from session
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Folder name is required"}), 400

    try:
        with conn.cursor() as cur:
            # Check if folder already exists
            check_query = "SELECT * FROM folder WHERE name=%s AND user_id=%s"
            cur.execute(check_query, (name, user_id))
            if cur.fetchone():
                return jsonify({"error": "Folder already exists"}), 409

            # Insert the new folder
            query = "INSERT INTO folder (name, user_id) VALUES (%s, %s)"
            cur.execute(query, (name, user_id))
            conn.commit()

        return jsonify({"message": "Folder created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


  



@app.route("/folders/get/<int:user_id>", methods=["GET"])
def get_folders(user_id):
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "SELECT id, name, created_at FROM folder WHERE user_id=%s"
            cur.execute(query, (user_id,))
            folders = cur.fetchall()
            return jsonify({"folders": folders})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/folders/delete/<int:folder_id>", methods=["DELETE"])
def delete_folder(folder_id):
    
    try:
        with conn.cursor() as cur:
            query = "DELETE FROM folder WHERE id=%s"
            cur.execute(query, (folder_id,))
            conn.commit()
            
            if cur.rowcount == 0:
                return jsonify({"error": "Folder not found"}), 404

            return jsonify({"message": "Folder deleted successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/folders/edit/<int:folder_id>", methods=["PATCH"])
def edit_folder(folder_id):
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # First check if folder exists
            select_query = "SELECT id, name FROM folder WHERE id=%s"
            cur.execute(select_query, (folder_id,))
            folder = cur.fetchone()

            if not folder:
                return jsonify({"error": "Folder not found"}), 404
            
            # Get updated name from request
            new_name = request.json.get("new_name", folder["name"])

            # Update folder name
            update_query = "UPDATE folder SET name=%s WHERE id=%s"
            cur.execute(update_query, (new_name, folder["id"]))
            conn.commit()

        return jsonify({"message": "Folder name updated successfully","folder": {"id": folder["id"], "name": new_name}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


