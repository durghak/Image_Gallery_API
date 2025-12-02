
from flask import Blueprint,jsonify,request,session
import pymysql
from db import conn
folder_bp = Blueprint('folder', __name__)

@folder_bp.route("/folders/add", methods=['POST'])
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


  



@folder_bp.route("/folders/get/<int:user_id>", methods=["GET"])
def get_folders(user_id):
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            query = "SELECT id, name, created_at FROM folder WHERE user_id=%s"
            cur.execute(query, (user_id,))
            folders = cur.fetchall()
            return jsonify({"folders": folders})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@folder_bp.route("/folders/delete/<int:folder_id>", methods=["DELETE"])
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


@folder_bp.route("/folders/edit/<int:folder_id>", methods=["PATCH"])
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

        return jsonify({"message": "Folder name updated successfully","folder": {"id": folder["id"], "new_name": new_name}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
