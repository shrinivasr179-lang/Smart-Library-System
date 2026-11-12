
import getpass

from werkzeug.security import generate_password_hash
from backend.database.db import get_connection, create_tables


def create_admin():
    create_tables()

    print("\n===== CREATE LIBRARY ADMIN =====")

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip().lower()
    password = getpass.getpass("Create password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if not name or not email or not password:
        print("Error: All fields are required.")
        return

    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    if len(password) < 8:
        print("Error: Password must contain at least 8 characters.")
        return

    password_hash = generate_password_hash(password)

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, password_hash, "admin")
        )

        conn.commit()
        print("\nAdmin account created successfully!")

    except Exception as error:
        print("\nUnable to create admin:", error)

    finally:
        conn.close()


if __name__ == "__main__":
    create_admin()
