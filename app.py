
from flask import (
    Flask, send_from_directory, request,
    jsonify, session, redirect
)
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from pathlib import Path
import os

from backend.routes.library_routes import library_bp
from backend.database.db import create_tables, get_connection

app = Flask(__name__)

secret_key = os.environ.get("SECRET_KEY")
if not secret_key and os.environ.get("RENDER"):
    raise RuntimeError("SECRET_KEY must be configured for Render.")
app.config["SECRET_KEY"] = (
    secret_key or "library-project-dev-secret-change-before-deployment"
)

CORS(app, supports_credentials=True)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Register library API routes
app.register_blueprint(library_bp)


def initialize_database():
    create_tables()

    admin_name = os.environ.get("ADMIN_NAME")
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    admin_values = (admin_name, admin_email, admin_password)

    if any(admin_values) and not all(admin_values):
        raise RuntimeError(
            "ADMIN_NAME, ADMIN_EMAIL, and ADMIN_PASSWORD must all be configured together."
        )

    if not all(admin_values):
        return
    if len(admin_password) < 8:
        raise RuntimeError("ADMIN_PASSWORD must contain at least 8 characters.")

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                admin_name.strip(),
                admin_email.strip().lower(),
                generate_password_hash(admin_password),
                "admin",
            ),
        )
        conn.commit()
    finally:
        conn.close()


initialize_database()


# Protect dashboard and library APIs
@app.before_request
def require_login():
    allowed_paths = [
        "/login",
        "/api/login",
        "/api/session",
        "/api/logout"
    ]

    if request.path in allowed_paths:
        return None

    # Allow frontend CSS, JavaScript and image files
    if not request.path.startswith("/api/") and request.path != "/":
        return None

    if "user_id" not in session:
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "message": "Please login first."
            }), 401

        return redirect("/login")


# Login page
@app.route("/login")
def login_page():
    if "user_id" in session:
        return redirect("/")

    return send_from_directory(FRONTEND_DIR, "login.html")


# Admin login API
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Enter your email and password."
        }), 400

    conn = get_connection()

    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
    finally:
        conn.close()

    if user is None or not check_password_hash(
        user["password_hash"], password
    ):
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    session.clear()
    session["user_id"] = user["user_id"]
    session["user_name"] = user["name"]
    session["user_role"] = user["role"]

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "name": user["name"]
    })


# Check login status
@app.route("/api/session")
def session_status():
    if "user_id" not in session:
        return jsonify({"logged_in": False})

    return jsonify({
        "logged_in": True,
        "name": session.get("user_name"),
        "role": session.get("user_role")
    })


# Admin logout API
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })


# Dashboard
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


# Frontend CSS, JavaScript, images and other files
@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == "__main__":
    print("Intelligent Library Management System Started!")
    print("Open: http://127.0.0.1:5000")

    app.run(debug=True)
