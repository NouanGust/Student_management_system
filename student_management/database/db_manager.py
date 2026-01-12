import sqlite3
import os

class DatabaseManager:
    def __init__(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        self.db_name = os.path.join(project_root, "students.db")
        
        print(f"Banco de Dados carregado em: {self.db_name}")
        
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de Usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de Alunos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                course TEXT NOT NULL,
                course_days TEXT NOT NULL,
                class_time TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de Presença
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date DATE NOT NULL,
                present BOOLEAN NOT NULL,
                note TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        # Tabela de Eventos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_date DATE NOT NULL,
                event_type TEXT DEFAULT 'aviso'
            )
        ''')
        
        # Alunos Gratuitos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS free_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                class_time TEXT,
                start_lesson TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Notas do Professor
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute("SELECT count(*) FROM teacher_notes")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO teacher_notes (content) VALUES ('')")

        conn.commit()
        conn.close()

    # --- MÉTODOS DE USUÁRIO (AUTH) ---
    def create_user(self, username, password_hash):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            conn.close()
            print(f"Usuário '{username}' criado com sucesso no DB.")
            return True
        except sqlite3.IntegrityError as e:
            print(f"Erro ao criar usuário: {e}")
            return False

    def get_user(self, username):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def user_exists(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def update_user_password(self, username, new_password_hash):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_password_hash, username))
            if cursor.rowcount == 0:
                conn.close()
                return False
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro DB Update: {e}")
            return False

    # --- MÉTODOS DE ALUNOS ---
    def create_student(self, name, course, days, time):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, course, course_days, class_time) VALUES (?, ?, ?, ?)", 
                      (name, course, days, time))
        conn.commit()
        conn.close()

    def get_all_students(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE active = 1 ORDER BY name")
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return students
    
    def update_student(self, student_id, name, course, days, time):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET name=?, course=?, course_days=?, class_time=? WHERE id=?", 
                      (name, course, days, time, student_id))
        conn.commit()
        conn.close()

    def delete_student(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET active = 0 WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()

    # --- PRESENÇA ---
    def mark_attendance(self, student_id, date, present, note=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM attendance WHERE student_id = ? AND date = ?", (student_id, date))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("UPDATE attendance SET present = ?, note = ? WHERE id = ?", (present, note, existing[0]))
        else:
            cursor.execute("INSERT INTO attendance (student_id, date, present, note) VALUES (?, ?, ?, ?)", 
                          (student_id, date, present, note))
        conn.commit()
        conn.close()
        return True

    def get_attendance_by_date(self, student_id, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT present FROM attendance WHERE student_id = ? AND date = ?", (student_id, date))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_attendance_summary(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND present = 1", (student_id,))
        present = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND present = 0", (student_id,))
        absent = cursor.fetchone()[0]
        conn.close()
        
        total = present + absent
        percentage = (present / total * 100) if total > 0 else 0
        return {"present": present, "absent": absent, "total": total, "percentage": percentage}

    def get_attendance(self, student_id, start_date, end_date):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE student_id = ? AND date BETWEEN ? AND ? ORDER BY date DESC", 
                      (student_id, start_date, end_date))
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return data

    def get_attendance_note(self, student_id, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT note FROM attendance WHERE student_id = ? AND date = ?", (student_id, date))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else ""

    # --- EVENTOS ---
    def create_event(self, title, description, date, event_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (title, description, event_date, event_type) VALUES (?, ?, ?, ?)", 
                      (title, description, date, event_type))
        conn.commit()
        conn.close()
    
    def get_events(self, from_date=None, to_date=None):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if from_date and to_date:
            cursor.execute("SELECT * FROM events WHERE event_date BETWEEN ? AND ? ORDER BY event_date", (from_date, to_date))
        else:
            cursor.execute("SELECT * FROM events ORDER BY event_date")
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return events

    def update_event(self, event_id, title, description, date, event_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET title=?, description=?, event_date=?, event_type=? WHERE id=?", 
                      (title, description, date, event_type, event_id))
        conn.commit()
        conn.close()

    def delete_event(self, event_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE id=?", (event_id,))
        conn.commit()
        conn.close()

    # --- FREE STUDENTS ---
    def create_free_student(self, name, phone, class_time, start_lesson):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO free_students (name, phone, class_time, start_lesson) VALUES (?, ?, ?, ?)", 
                      (name, phone, class_time, start_lesson))
        conn.commit()
        conn.close()

    def get_all_free_students(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM free_students WHERE active = 1 ORDER BY name")
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return students

    def update_free_student(self, student_id, name, phone, class_time, start_lesson):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE free_students SET name=?, phone=?, class_time=?, start_lesson=? WHERE id=?", 
                      (name, phone, class_time, start_lesson, student_id))
        conn.commit()
        conn.close()

    def delete_free_student(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE free_students SET active = 0 WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        
    def promote_free_to_paid(self, free_student_id, course, days):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM free_students WHERE id = ?", (free_student_id,))
        free_s = cursor.fetchone()
        if free_s:
            self.create_student(free_s['name'], course, days, free_s['class_time'])
            self.delete_free_student(free_student_id)
            conn.close()
            return True
        conn.close()
        return False

    # --- TEACHER STATS ---
    def get_teacher_note(self) -> str:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM teacher_notes ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else ""

    def save_teacher_note(self, content: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE teacher_notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = (SELECT id FROM teacher_notes LIMIT 1)", (content,))
        conn.commit()
        conn.close()

    def get_teacher_stats(self) -> dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students WHERE active = 1")
        total_students = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM attendance")
        total_classes_given = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM free_students WHERE active = 1")
        total_free_active = cursor.fetchone()[0]
        conn.close()
        
        xp = (total_students * 50) + (total_classes_given * 10) + (total_free_active * 20)
        level = int(xp / 500) + 1
        next_level_xp = 500 - (xp % 500)
        progress = (xp % 500) / 500
        
        return {
            "students": total_students,
            "classes": total_classes_given,
            "xp": xp,
            "level": level,
            "progress": progress,
            "next_level_xp": next_level_xp
        }

    # --- METÓDOS DE RELATÓRIO ---
    def get_daily_report_data(self, date_str, day_name_fragment):
        """
        Gera o relatório do dia:
        1. Pega todos os alunos que tem aula naquele dia da semana (ex: 'seg').
        2. Cruza com a tabela de presença para ver quem veio, faltou ou não tem registro.
        """
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Busca alunos agendados para este dia da semana
        # O LIKE %fragment% busca 'seg' dentro de 'Seg/Qua', por exemplo.
        cursor.execute("SELECT id, name, course, class_time FROM students WHERE active=1 AND course_days LIKE ?", (f"%{day_name_fragment}%",))
        scheduled_students = [dict(row) for row in cursor.fetchall()]

        report_data = []
        present_count = 0
        absent_count = 0
        pending_count = 0

        for student in scheduled_students:
            # 2. Busca o registro de presença para a data específica
            cursor.execute("SELECT present, note FROM attendance WHERE student_id = ? AND date = ?", (student['id'], date_str))
            record = cursor.fetchone()

            status = "Pendente"
            note = ""

            if record:
                if record['present']:
                    status = "Presente"
                    present_count += 1
                else:
                    status = "Falta"
                    absent_count += 1
                note = record['note']
            else:
                pending_count += 1

            report_data.append({
                "name": student['name'],
                "course": student['course'],
                "time": student['class_time'],
                "status": status,
                "note": note
            })

        conn.close()

        # Ordena por horário
        report_data.sort(key=lambda x: x['time'] or "23:59")

        return {
            "date": date_str,
            "summary": {
                "total": len(scheduled_students),
                "present": present_count,
                "absent": absent_count,
                "pending": pending_count
            },
            "details": report_data
        }

    def get_monthly_report_data(self, month, year):
        """Gera estatísticas gerais do mês"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Formato da data no banco é YYYY-MM-DD
        # Vamos filtrar onde o strftime do mês e ano batem
        start_date = f"{year}-{month:02d}-01"
        # Truque simples para fim do mês: pega o primeiro dia do próximo mês e subtrai um dia, 
        # ou apenas busca pelo prefixo da string 'YYYY-MM'
        month_prefix = f"{year}-{month:02d}"
        
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date LIKE ? AND present = 1", (f"{month_prefix}%",))
        total_presents = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date LIKE ? AND present = 0", (f"{month_prefix}%",))
        total_absents = cursor.fetchone()[0]
        
        # Busca alunos com mais faltas no mês (Top 5)
        cursor.execute('''
            SELECT s.name, COUNT(a.id) as faltas
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.date LIKE ? AND a.present = 0
            GROUP BY s.id
            ORDER BY faltas DESC
            LIMIT 5
        ''', (f"{month_prefix}%",))
        top_absents = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]

        conn.close()
        
        return {
            "month": f"{month}/{year}",
            "presents": total_presents,
            "absents": total_absents,
            "attendance_rate": (total_presents / (total_presents + total_absents) * 100) if (total_presents + total_absents) > 0 else 0,
            "top_absents": top_absents
        }