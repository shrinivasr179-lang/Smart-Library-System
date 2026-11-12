from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    AND name NOT LIKE 'sqlite_%'
    ORDER BY name
""")

tables = cursor.fetchall()

for table in tables:
    print("-", table["name"])

print("Total project tables:", len(tables))

conn.close()