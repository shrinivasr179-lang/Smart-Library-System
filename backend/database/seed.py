
from db import get_connection, create_tables

def insert_sample_data():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # Categories
    categories = [
        "Computer Science",
        "Artificial Intelligence",
        "Mathematics",
        "Programming",
        "Blockchain",
        "Electronics"
    ]

    for category in categories:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (category_name) VALUES (?)",
            (category,)
        )

    # Students
    students = [
        ("Rahul Kumar", "rahul@gmail.com", "CSE", 3),
        ("Priya Sharma", "priya@gmail.com", "AIML", 3),
        ("Arun Kumar", "arun@gmail.com", "ECE", 3),
        ("Sneha Rao", "sneha@gmail.com", "CSE", 3),
        ("Kiran Patil", "kiran@gmail.com", "AIML", 3)
    ]

    for student in students:
        cursor.execute("""
            INSERT OR IGNORE INTO students
            (name, email, department, max_books)
            VALUES (?, ?, ?, ?)
        """, student)

    # Get category IDs
    cursor.execute("SELECT * FROM categories")
    category_map = {
        row["category_name"]: row["category_id"]
        for row in cursor.fetchall()
    }

    # Books
    books = [
        ("Python Programming", "Mark Lutz", "Programming", 5),
        ("Artificial Intelligence", "Stuart Russell", "Artificial Intelligence", 4),
        ("Discrete Mathematics", "Kenneth Rosen", "Mathematics", 6),
        ("Data Structures", "Reema Thareja", "Computer Science", 5),
        ("Blockchain Basics", "Daniel Drescher", "Blockchain", 3),
        ("Machine Learning", "Tom Mitchell", "Artificial Intelligence", 4),
        ("Database Systems", "Raghu Ramakrishnan", "Computer Science", 3),
        ("C Programming", "Dennis Ritchie", "Programming", 5),
        ("Digital Electronics", "Morris Mano", "Electronics", 3),
        ("Graph Theory", "Douglas West", "Mathematics", 4)
    ]

    for title, author, category, copies in books:
        cursor.execute("""
            INSERT INTO books
            (title, author, category_id, total_copies, available_copies)
            SELECT ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM books WHERE title = ? AND author = ?
            )
        """, (
            title, author, category_map[category],
            copies, copies, title, author
        ))

    conn.commit()
    conn.close()

    print("Sample data inserted successfully!")


if __name__ == "__main__":
    insert_sample_data()
