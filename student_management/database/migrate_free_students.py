import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Cria nova tabela
cursor.execute('''
    CREATE TABLE IF NOT EXISTS free_students_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        class_time TEXT NOT NULL,
        start_lesson TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        active INTEGER DEFAULT 1
    )
''')

# Copia dados existentes (adapte conforme necessário)
cursor.execute('''
    INSERT INTO free_students_new (id, name, phone, class_time, created_at, active)
    SELECT id, name, phone, class_time, created_at, active 
    FROM free_students
''')

# Remove tabela antiga e renomeia
cursor.execute('DROP TABLE free_students')
cursor.execute('ALTER TABLE free_students_new RENAME TO free_students')

conn.commit()
conn.close()
print("✅ Tabela migrada!")