
from flask import Blueprint, jsonify, request
import sqlite3
import os
from pathlib import Path
from datetime import date, timedelta

# CREATE BLUEPRINT
library_bp = Blueprint("library", __name__)

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = Path(
    os.environ.get("DATABASE_PATH", BASE_DIR / "backend" / "database" / "library.db")
)


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# GET ALL STUDENTS
@library_bp.route("/api/students", methods=["GET"])
def get_students():
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM students ORDER BY student_id DESC"
        ).fetchall()
        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


# ADD STUDENT
@library_bp.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    department = str(data.get("department", "")).strip()

    if not name or not email or not department:
        return jsonify({"error": "All student fields are required"}), 400

    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO students (name, email, department)
            VALUES (?, ?, ?)
        """, (name, email, department))

        conn.commit()
        return jsonify({"message": "Student added successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409

    finally:
        conn.close()


# GET CATEGORIES
@library_bp.route("/api/categories", methods=["GET"])
def get_categories():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT * FROM categories
            ORDER BY category_name
        """).fetchall()

        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


# GET ALL BOOKS
@library_bp.route("/api/books", methods=["GET"])
def get_books():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT books.*, categories.category_name
            FROM books
            LEFT JOIN categories
            ON books.category_id = categories.category_id
            ORDER BY books.book_id DESC
        """).fetchall()

        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


# SEARCH BOOKS
@library_bp.route("/api/books/search", methods=["GET"])
def search_books():
    search = request.args.get("q", "").strip()

    if not search:
        return jsonify({"error": "Enter a search term"}), 400

    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT books.*, categories.category_name
            FROM books
            LEFT JOIN categories
            ON books.category_id = categories.category_id
            WHERE books.title LIKE ? OR books.author LIKE ?
        """, (f"%{search}%", f"%{search}%")).fetchall()

        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


# ADD BOOK
@library_bp.route("/api/books", methods=["POST"])
def add_book():
    data = request.get_json(silent=True) or {}

    title = str(data.get("title", "")).strip()
    author = str(data.get("author", "")).strip()

    try:
        category_id = int(data.get("category_id"))
        copies = int(data.get("total_copies", 1))
    except (TypeError, ValueError):
        return jsonify({
            "error": "Choose a category and valid copy count"
        }), 400

    if not title or not author or copies < 1:
        return jsonify({"error": "Enter valid book details"}), 400

    conn = get_db()
    try:
        category = conn.execute("""
            SELECT category_id FROM categories
            WHERE category_id = ?
        """, (category_id,)).fetchone()

        if not category:
            return jsonify({"error": "Category not found"}), 400

        conn.execute("""
            INSERT INTO books
            (title, author, category_id, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?)
        """, (title, author, category_id, copies, copies))

        conn.commit()
        return jsonify({"message": "Book added successfully"}), 201

    finally:
        conn.close()


# ISSUE BOOK
@library_bp.route("/api/issue", methods=["POST"])
def issue_book():
    data = request.get_json(silent=True) or {}

    try:
        student_id = int(data.get("student_id"))
        book_id = int(data.get("book_id"))
    except (TypeError, ValueError):
        return jsonify({
            "error": "Select a valid student and book"
        }), 400

    conn = get_db()

    try:
        conn.execute("BEGIN IMMEDIATE")

        student = conn.execute("""
            SELECT * FROM students WHERE student_id = ?
        """, (student_id,)).fetchone()

        book = conn.execute("""
            SELECT * FROM books WHERE book_id = ?
        """, (book_id,)).fetchone()

        if not student or not book:
            conn.rollback()
            return jsonify({"error": "Student or book not found"}), 404

        active_count = conn.execute("""
            SELECT COUNT(*) AS total
            FROM issue_records
            WHERE student_id = ? AND status = 'Issued'
        """, (student_id,)).fetchone()["total"]

        if active_count >= student["max_books"]:
            conn.rollback()
            return jsonify({
                "error": "Student has reached the borrowing limit"
            }), 400

        if book["available_copies"] < 1:
            conn.rollback()
            return jsonify({"error": "No copies available"}), 400

        issue_date = date.today()
        due_date = issue_date + timedelta(days=14)

        conn.execute("""
            INSERT INTO issue_records
            (student_id, book_id, issue_date, due_date, status)
            VALUES (?, ?, ?, ?, 'Issued')
        """, (
            student_id,
            book_id,
            issue_date.isoformat(),
            due_date.isoformat()
        ))

        conn.execute("""
            UPDATE books
            SET available_copies = available_copies - 1
            WHERE book_id = ?
        """, (book_id,))

        conn.commit()

        return jsonify({
            "message": "Book issued successfully",
            "due_date": due_date.isoformat()
        }), 201

    except sqlite3.Error:
        conn.rollback()
        return jsonify({
            "error": "Database error while issuing book"
        }), 500

    finally:
        conn.close()


# VIEW ISSUE RECORDS
@library_bp.route("/api/issues", methods=["GET"])
def get_issues():
    conn = get_db()

    try:
        rows = conn.execute("""
            SELECT
                issue_records.*,
                students.name AS student_name,
                books.title AS book_title
            FROM issue_records
            JOIN students
                ON issue_records.student_id = students.student_id
            JOIN books
                ON issue_records.book_id = books.book_id
            ORDER BY issue_records.issue_id DESC
        """).fetchall()

        return jsonify([dict(row) for row in rows])

    finally:
        conn.close()


# RETURN BOOK
@library_bp.route("/api/return/<int:issue_id>", methods=["POST"])
def return_book(issue_id):
    conn = get_db()

    try:
        conn.execute("BEGIN IMMEDIATE")

        issue = conn.execute("""
            SELECT * FROM issue_records
            WHERE issue_id = ? AND status = 'Issued'
        """, (issue_id,)).fetchone()

        if not issue:
            conn.rollback()
            return jsonify({
                "error": "Active issue record not found"
            }), 404

        conn.execute("""
            UPDATE issue_records
            SET status = 'Returned', return_date = ?
            WHERE issue_id = ?
        """, (date.today().isoformat(), issue_id))

        conn.execute("""
            UPDATE books
            SET available_copies = available_copies + 1
            WHERE book_id = ?
        """, (issue["book_id"],))

        conn.commit()

        return jsonify({
            "message": "Book returned successfully"
        })

    except sqlite3.Error:
        conn.rollback()
        return jsonify({
            "error": "Database error while returning book"
        }), 500

    finally:
        conn.close()


# DASHBOARD STATISTICS API
@library_bp.route("/api/dashboard-stats", methods=["GET"])
def dashboard_stats():

    conn = get_db()

    try:
        total_students = conn.execute("""
            SELECT COUNT(*) AS total
            FROM students
        """).fetchone()["total"]

        book_stats = conn.execute("""
            SELECT
                COUNT(*) AS total_titles,
                COALESCE(SUM(total_copies), 0) AS total_books,
                COALESCE(SUM(available_copies), 0) AS available_books
            FROM books
        """).fetchone()

        issued_books = conn.execute("""
            SELECT COUNT(*) AS total
            FROM issue_records
            WHERE status = 'Issued'
        """).fetchone()["total"]

        returned_books = conn.execute("""
            SELECT COUNT(*) AS total
            FROM issue_records
            WHERE status = 'Returned'
        """).fetchone()["total"]

        category_data = conn.execute("""
            SELECT
                COALESCE(categories.category_name, 'Uncategorized')
                    AS category_name,
                COALESCE(SUM(books.total_copies), 0) AS total_books
            FROM books
            LEFT JOIN categories
                ON books.category_id = categories.category_id
            GROUP BY books.category_id, categories.category_name
            ORDER BY category_name
        """).fetchall()

        return jsonify({
            "total_students": total_students,
            "total_titles": book_stats["total_titles"],
            "total_books": book_stats["total_books"],
            "available_books": book_stats["available_books"],
            "issued_books": issued_books,
            "returned_books": returned_books,
            "categories": [
                dict(row) for row in category_data
            ]
        })

    finally:
        conn.close()


# OVERDUE BOOKS API
@library_bp.route("/api/overdue-books", methods=["GET"])
def get_overdue_books():

    conn = get_db()

    try:
        rows = conn.execute("""
            SELECT
                issue_records.issue_id,
                issue_records.due_date,
                students.name AS student_name,
                books.title AS book_title
            FROM issue_records
            JOIN students
                ON issue_records.student_id = students.student_id
            JOIN books
                ON issue_records.book_id = books.book_id
            WHERE issue_records.status = 'Issued'
            AND date(issue_records.due_date) < date('now')
            ORDER BY issue_records.due_date ASC
        """).fetchall()

        return jsonify({
            "total_overdue": len(rows),
            "overdue_books": [dict(row) for row in rows]
        })

    finally:
        conn.close()
# LOW STOCK BOOKS API
@library_bp.route("/api/low-stock-books", methods=["GET"])
def get_low_stock_books():
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT
                book_id,
                title,
                total_copies,
                available_copies
            FROM books
            WHERE available_copies <= 2
            ORDER BY available_copies ASC
        """).fetchall()

        return jsonify({
            "total_low_stock": len(rows),
            "low_stock_books": [dict(row) for row in rows]
        })
    finally:
        conn.close()

# =====================================
# BOOK RESERVATION API
# =====================================

from datetime import date


@library_bp.route("/api/reservations", methods=["GET"])
def get_reservations():
    conn = get_db()

    try:
        rows = conn.execute("""
            SELECT
                reservations.reservation_id,
                reservations.reservation_date,
                reservations.status,
                students.name AS student_name,
                books.title AS book_title
            FROM reservations
            JOIN students
                ON reservations.student_id = students.student_id
            JOIN books
                ON reservations.book_id = books.book_id
            ORDER BY reservations.reservation_id DESC
        """).fetchall()

        return jsonify({
            "total_reservations": len(rows),
            "reservations": [dict(row) for row in rows]
        })

    finally:
        conn.close()


@library_bp.route("/api/reservations", methods=["POST"])
def add_reservation():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    student_id = data.get("student_id")
    book_id = data.get("book_id")

    if not student_id or not book_id:
        return jsonify({
            "error": "Student ID and Book ID are required"
        }), 400

    conn = get_db()

    try:
        book = conn.execute("""
            SELECT available_copies
            FROM books
            WHERE book_id = ?
        """, (book_id,)).fetchone()

        student = conn.execute("""
            SELECT student_id
            FROM students
            WHERE student_id = ?
        """, (student_id,)).fetchone()

        if not book or not student:
            return jsonify({
                "error": "Student or book not found"
            }), 404

        if book["available_copies"] > 0:
            return jsonify({
                "error": "This book is available. You can issue it directly."
            }), 400

        existing = conn.execute("""
            SELECT reservation_id
            FROM reservations
            WHERE student_id = ?
            AND book_id = ?
            AND status = 'Pending'
        """, (student_id, book_id)).fetchone()

        if existing:
            return jsonify({
                "error": "You already have a pending reservation for this book."
            }), 400

        conn.execute("""
            INSERT INTO reservations (
                student_id,
                book_id,
                reservation_date,
                status
            )
            VALUES (?, ?, ?, 'Pending')
        """, (
            student_id,
            book_id,
            date.today().isoformat()
        ))

        conn.commit()

        return jsonify({
            "message": "Book reserved successfully!"
        }), 201

    finally:
        conn.close()

# =====================================
# UPDATE RESERVATION STATUS API
# =====================================

@library_bp.route("/api/reservations/<int:reservation_id>", methods=["PUT"])
def update_reservation_status(reservation_id):
    data = request.get_json()

    if not data or not data.get("status"):
        return jsonify({"error": "Status is required"}), 400

    status = data["status"]

    allowed_statuses = ["Pending", "Ready", "Completed", "Cancelled"]

    if status not in allowed_statuses:
        return jsonify({"error": "Invalid reservation status"}), 400

    conn = get_db()

    try:
        reservation = conn.execute("""
            SELECT reservation_id
            FROM reservations
            WHERE reservation_id = ?
        """, (reservation_id,)).fetchone()

        if not reservation:
            return jsonify({"error": "Reservation not found"}), 404

        conn.execute("""
            UPDATE reservations
            SET status = ?
            WHERE reservation_id = ?
        """, (status, reservation_id))

        conn.commit()

        return jsonify({
            "message": "Reservation status updated successfully!",
            "status": status
        })

    finally:
        conn.close()

# ======================================
# STUDENT ATTENDANCE API
# ======================================

from datetime import date


@library_bp.route("/api/attendance", methods=["GET"])
def get_attendance():
    conn = get_db()

    try:
        attendance_date = request.args.get(
            "date", date.today().isoformat()
        )

        rows = conn.execute("""
            SELECT
                attendance.attendance_id,
                attendance.student_id,
                students.name AS student_name,
                students.department,
                attendance.attendance_date,
                attendance.status,
                attendance.remarks
            FROM attendance
            JOIN students
                ON attendance.student_id = students.student_id
            WHERE attendance.attendance_date = ?
            ORDER BY students.name
        """, (attendance_date,)).fetchall()

        return jsonify([dict(row) for row in rows])

    finally:
        conn.close()


@library_bp.route("/api/attendance", methods=["POST"])
def mark_attendance():
    conn = get_db()

    try:
        data = request.get_json() or {}

        student_id = data.get("student_id")
        attendance_date = data.get("attendance_date")
        status = data.get("status")
        remarks = data.get("remarks", "")

        if not student_id or not attendance_date or status not in [
            "Present", "Absent", "Late"
        ]:
            return jsonify({
                "error": "Student, date and valid status are required."
            }), 400

        student = conn.execute(
            "SELECT student_id FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        if not student:
            return jsonify({"error": "Student not found."}), 404

        conn.execute("""
            INSERT INTO attendance
                (student_id, attendance_date, status, remarks)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, attendance_date)
            DO UPDATE SET
                status = excluded.status,
                remarks = excluded.remarks
        """, (student_id, attendance_date, status, remarks))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Attendance saved successfully."
        })

    finally:
        conn.close()


# ======================================
# LIBRARY CALENDAR API
# ======================================

@library_bp.route("/api/events", methods=["GET"])
def get_library_events():
    conn = get_db()

    try:
        rows = conn.execute("""
            SELECT *
            FROM library_events
            ORDER BY event_date ASC
        """).fetchall()

        return jsonify([dict(row) for row in rows])

    finally:
        conn.close()


@library_bp.route("/api/events", methods=["POST"])
def add_library_event():
    conn = get_db()

    try:
        data = request.get_json() or {}

        title = (data.get("event_title") or "").strip()
        description = data.get("description", "")
        event_date = data.get("event_date")
        event_type = data.get("event_type", "General")

        if not title or not event_date:
            return jsonify({
                "error": "Event title and date are required."
            }), 400

        conn.execute("""
            INSERT INTO library_events
                (event_title, description, event_date, event_type)
            VALUES (?, ?, ?, ?)
        """, (title, description, event_date, event_type))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Library event added successfully."
        }), 201

    finally:
        conn.close()


@library_bp.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_library_event(event_id):
    conn = get_db()

    try:
        cursor = conn.execute("""
            DELETE FROM library_events
            WHERE event_id = ?
        """, (event_id,))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Event not found."}), 404

        return jsonify({
            "success": True,
            "message": "Event deleted successfully."
        })

    finally:
        conn.close()
