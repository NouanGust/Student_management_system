# fix_db.py
import sqlite3

# Use o caminho completo do banco correto
conn = sqlite3.connect('database/students.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE students ADD COLUMN class_time TEXT DEFAULT ''")
    print("✅ class_time adicionada em students")
except sqlite3.OperationalError as e:
    print(f"⚠️ students: {e}")

try:
    cursor.execute("ALTER TABLE free_students ADD COLUMN class_time TEXT DEFAULT ''")
    print("✅ class_time adicionada em free_students")
except sqlite3.OperationalError as e:
    print(f"⚠️ free_students: {e}")

conn.commit()
conn.close()
print("✅ Pronto!")