from flask import Flask,jsonify,request,session
import flask_cors
from Routes.user_routes import user_bp
from Routes.photo_routes import photo_bp
from Routes.folder_routes import folder_bp

from flask_cors import CORS
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.register_blueprint(user_bp)
app.register_blueprint(photo_bp)
app.register_blueprint(folder_bp)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:3000"]}}
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True

app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



@app.route("/")
def home():
    return jsonify({"name":"Durgha"})

if __name__ == '__main__':
    app.run(debug=True)


