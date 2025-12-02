from flask import Blueprint, jsonify, request,send_from_directory
import os
from werkzeug.utils import secure_filename
from db import conn
from config import ALLOWED_EXTENSIONS
from flask import current_app

photo_bp = Blueprint('photo', __name__)

@photo_bp.route("/photo/upload/<int:folder_id>", methods=["POST"])
def upload_photo(folder_id):
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "File type not allowed"}), 415
    
    filename = secure_filename(file.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_folder, filename)

    # Save file
    file.save(filepath)
    print("Upload route hit!")

    # Convert to relative path for frontend
    relative_path = f"uploads/{filename}"
    filename = filename.strip() 
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM folder WHERE id=%s", (folder_id,))
            if cur.fetchone() is None:
                return jsonify({"error": "Folder does not exist"}), 404

            cur.execute(
                "INSERT INTO photo (image_path, folder_id) VALUES (%s, %s)",
                (relative_path, folder_id),
            )
            conn.commit()

        return jsonify({
            "message": "Photo uploaded successfully",
            "image_url": f"http://localhost:5000/{relative_path}"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@photo_bp.route("/photo/get/<filename>", methods=["GET"])
def get_photo(filename):
    # Sanitize filename
    filename = secure_filename(filename.strip())
    
    # Get the absolute uploads folder
    uploads_dir = os.path.join(current_app.root_path, current_app.config.get('UPLOAD_FOLDER', 'uploads'))
    
    file_path = os.path.join(uploads_dir, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Send the file, auto-detecting MIME type
    return send_from_directory(uploads_dir, filename, as_attachment=False)


  # your database connection

@photo_bp.route("/photo/delete/<filename>", methods=["DELETE"])
def delete_photo(filename):
    # Sanitize the filename
    filename = secure_filename(filename.strip())
    
    # Get upload folder path
    uploads_dir = os.path.join(current_app.root_path, current_app.config.get('UPLOAD_FOLDER', 'uploads'))
    file_path = os.path.join(uploads_dir, filename)

    # Check if file exists in filesystem
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Delete file from filesystem
    os.remove(file_path)

    # Delete record from database
    cursor = conn.cursor()
    cursor.execute("DELETE FROM photo WHERE image_path=%s", (f"uploads/{filename}",))
    conn.commit()
    cursor.close()

    return jsonify({"message": "File and database record deleted successfully"}), 200
