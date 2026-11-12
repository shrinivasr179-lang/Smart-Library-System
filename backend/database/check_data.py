
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

tables = ["students", "categories", "books"]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count} records")

conn.close()