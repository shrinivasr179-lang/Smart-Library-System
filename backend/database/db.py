
import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = Path(
    os.environ.get("DATABASE_PATH", BASE_DIR / "backend" / "database" / "library.db")
)


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def create_tables():
    conn = get_connection()

    conn.executescript("""
        -- STUDENTS TABLE
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            max_books INTEGER DEFAULT 3
        );

        -- CATEGORIES TABLE
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        );

        -- BOOKS TABLE
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category_id INTEGER,
            total_copies INTEGER NOT NULL DEFAULT 1,
            available_copies INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        );

        -- ISSUE RECORDS TABLE
        CREATE TABLE IF NOT EXISTS issue_records (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            book_id INTEGER,
            issue_date TEXT,
            due_date TEXT,
            return_date TEXT,
            status TEXT DEFAULT 'Issued',
            FOREIGN KEY (student_id)
                REFERENCES students(student_id),
            FOREIGN KEY (book_id)
                REFERENCES books(book_id)
        );

        -- RESERVATIONS TABLE
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            book_id INTEGER,
            reservation_date TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (student_id)
                REFERENCES students(student_id),
            FOREIGN KEY (book_id)
                REFERENCES books(book_id)
        );

        -- USERS TABLE
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- STUDENT ATTENDANCE TABLE
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL
                CHECK(status IN ('Present', 'Absent', 'Late')),
            remarks TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id)
                REFERENCES students(student_id),
            UNIQUE(student_id, attendance_date)
        );

        -- LIBRARY CALENDAR EVENTS TABLE
        CREATE TABLE IF NOT EXISTS library_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_title TEXT NOT NULL,
            description TEXT,
            event_date TEXT NOT NULL,
            event_type TEXT DEFAULT 'General',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()
