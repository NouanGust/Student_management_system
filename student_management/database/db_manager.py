import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_name: str = "students.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.init_database()
    
    def get_connection(self):
        """Cria uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa o banco de dados com todas as tabelas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de usuários (para login)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de alunos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                course TEXT NOT NULL,
                course_days TEXT NOT NULL,
                class_time TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # Tabela de alunos gratuitos (período experimental)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS free_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                class_time TEXT NOT NULL,
                start_lesson TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # Tabela de presenças
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                present INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students (id),
                UNIQUE(student_id, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS free_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                lesson TEXT NOT NULL,
                present INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES free_students (id),
                UNIQUE(student_id, date)
            )
        ''')
        
        # Tabela de avisos e compromissos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_date TEXT NOT NULL,
                event_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                note TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id),
                UNIQUE(student_id, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Garante que existe pelo menos uma nota vazia para o usuário
        cursor.execute("SELECT count(*) FROM teacher_notes")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO teacher_notes (content) VALUES ('')")
            
        
        conn.commit()
        conn.close()
    
    # ==================== MÉTODOS DO PERFIL DO PROFESSOR ====================

    def get_teacher_note(self) -> str:
        """Pega a anotação do professor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM teacher_notes ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else ""

    def save_teacher_note(self, content: str):
        """Salva a anotação (atualiza a única nota existente para simplificar)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Atualiza a primeira nota encontrada ou insere
        cursor.execute("UPDATE teacher_notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = (SELECT id FROM teacher_notes LIMIT 1)", (content,))
        conn.commit()
        conn.close()

    def get_teacher_stats(self) -> dict:
        """Calcula estatísticas para gamificação"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total Alunos
        cursor.execute("SELECT COUNT(*) FROM students WHERE active = 1")
        total_students = cursor.fetchone()[0]
        
        # Total Aulas Dadas (Presenças marcadas)
        cursor.execute("SELECT COUNT(*) FROM attendance")
        total_classes_given = cursor.fetchone()[0]
        
        # Total Aulas Gratuitas
        cursor.execute("SELECT COUNT(*) FROM free_attendance")
        total_free_classes = cursor.fetchone()[0]
        
        conn.close()
        
        # Cálculo de XP (Exemplo: 10xp por aluno, 5xp por aula)
        xp = (total_students * 50) + (total_classes_given * 10) + (total_free_classes * 10)
        
        # Lógica simples de nível: Nível = Raiz quadrada do XP (ajuste conforme gosto)
        # Ou a cada 500xp sobe um nível
        level = int(xp / 500) + 1
        next_level_xp = (level * 500)
        progress = (xp % 500) / 500
        
        return {
            "students": total_students,
            "classes": total_classes_given + total_free_classes,
            "xp": xp,
            "level": level,
            "progress": progress,
            "next_level_xp": 500 - (xp % 500) # Quanto falta
        }
    
    # ==================== MÉTODOS DE USUÁRIO ====================
    
    def create_user(self, username: str, password_hash: str) -> bool:
        """Cria um novo usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Busca um usuário pelo nome"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "password_hash": row[2]
            }
        return None
    
    def user_exists(self) -> bool:
        """Verifica se existe algum usuário cadastrado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    # ==================== MÉTODOS DE ALUNOS ====================
    
    def create_student(self, name: str, course: str, course_days: str, class_time: str = "") -> int:
        """Cria um novo aluno"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, course, course_days, class_time) VALUES (?, ?, ?, ?)",
            (name, course, course_days, class_time)
        )
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return student_id
    
    def get_all_students(self, active_only: bool = True) -> List[Dict]:
        """Retorna todos os alunos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, name, course, course_days, class_time, created_at, active FROM students"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY class_time, name"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "course": row[2],
                "course_days": row[3],
                "class_time": row[4] or "",
                "created_at": row[5],
                "active": row[6]
            }
            for row in rows
        ]
    
    def get_student(self, student_id: int) -> Optional[Dict]:
        """Busca um aluno pelo ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, course, course_days, class_time, created_at, active FROM students WHERE id = ?",
            (student_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "course": row[2],
                "course_days": row[3],
                "class_time": row[4] or "",
                "created_at": row[5],
                "active": row[6]
            }
        return None
    
    def update_student(self, student_id: int, name: str, course: str, course_days: str, class_time: str = "") -> bool:
        """Atualiza os dados de um aluno"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET name = ?, course = ?, course_days = ?, class_time = ? WHERE id = ?",
            (name, course, course_days, class_time, student_id)
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_student(self, student_id: int) -> bool:
        """Desativa um aluno (soft delete)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET active = 0 WHERE id = ?", (student_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # ==================== MÉTODOS DE PRESENÇA ====================
    
    def mark_attendance(self, student_id: int, date: str, present: bool) -> bool:
        """Marca presença/falta de um aluno"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO attendance (student_id, date, present) VALUES (?, ?, ?)",
                (student_id, date, 1 if present else 0)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    
    def get_attendance(self, student_id: int, start_date: str, end_date: str) -> List[Dict]:
        """Busca presenças de um aluno em um período"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT date, present FROM attendance 
               WHERE student_id = ? AND date BETWEEN ? AND ?
               ORDER BY date""",
            (student_id, start_date, end_date)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [{"date": row[0], "present": bool(row[1])} for row in rows]
    
    def get_attendance_summary(self, student_id: int) -> Dict:
        """Retorna resumo de presenças de um aluno"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT 
                COUNT(*) as total,
                SUM(present) as present_count,
                SUM(CASE WHEN present = 0 THEN 1 ELSE 0 END) as absent_count
               FROM attendance WHERE student_id = ?""",
            (student_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total": row[0],
            "present": row[1],
            "absent": row[2],
            "percentage": (row[1] / row[0] * 100) if row[0] > 0 else 0
        }
    
    # ==================== MÉTODOS DE EVENTOS ====================
    
    def create_event(self, title: str, description: str, event_date: str, event_type: str) -> int:
        """Cria um novo evento/aviso"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (title, description, event_date, event_type) VALUES (?, ?, ?, ?)",
            (title, description, event_date, event_type)
        )
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def update_event(self, event_id: int, title: str, description: str, event_date: str, event_type: str) -> bool:
        """Atualiza um evento existente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE events SET title = ?, description = ?, event_date = ?, event_type = ? WHERE id = ?",
            (title, description, event_date, event_type, event_id)
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_events(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Busca eventos em um período"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute(
                """SELECT id, title, description, event_date, event_type, created_at 
                   FROM events WHERE event_date BETWEEN ? AND ?
                   ORDER BY event_date""",
                (start_date, end_date)
            )
        else:
            cursor.execute(
                """SELECT id, title, description, event_date, event_type, created_at 
                   FROM events ORDER BY event_date DESC LIMIT 50"""
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "event_date": row[3],
                "event_type": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]
    
    def delete_event(self, event_id: int) -> bool:
        """Deleta um evento"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # ==================== MÉTODOS DE ALUNOS GRATUITOS ====================
    
    def create_free_student(self, name: str, phone: str, class_time: str, start_lesson: str) -> int:
        """Cria um novo aluno gratuito"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO free_students (name, phone, class_time, start_lesson) VALUES (?, ?, ?, ?)",
            (name, phone, class_time, start_lesson)
        )
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return student_id
    
    def get_all_free_students(self, active_only: bool = True) -> List[Dict]:
        """Retorna todos os alunos gratuitos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, name, phone, class_time, start_lesson, created_at, active FROM free_students"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY class_time, name"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "phone": row[2],
                "class_time": row[3],
                "start_lesson": row[4],
                "created_at": row[5],
                "active": row[6]
            }
            for row in rows
        ]
    
    def get_free_student(self, student_id: int) -> Optional[Dict]:
        """Busca um aluno gratuito pelo ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, course, course_days, class_time, phone, start_date, end_date, created_at, active FROM free_students WHERE id = ?",
            (student_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "course": row[2],
                "course_days": row[3],
                "class_time": row[4] or "",
                "phone": row[5],
                "start_date": row[6],
                "end_date": row[7],
                "created_at": row[8],
                "active": row[9]
            }
        return None
    
    def update_free_student(self, student_id: int, name: str, phone: str, class_time: str, start_lesson: str) -> bool:
        """Atualiza os dados de um aluno gratuito"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE free_students SET name = ?, phone = ?, class_time = ?, start_lesson = ? WHERE id = ?",
            (name, phone, class_time, start_lesson, student_id)
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def delete_free_student(self, student_id: int) -> bool:
        """Desativa um aluno gratuito (soft delete)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE free_students SET active = 0 WHERE id = ?", (student_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    
    def mark_free_attendance(self, student_id: int, date: str, lesson: str, present: bool) -> bool:
        """Marca presença de aluno gratuito"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO free_attendance (student_id, date, lesson, present) VALUES (?, ?, ?, ?)",
                (student_id, date, lesson, 1 if present else 0)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False

    def get_attendance_by_date(self, student_id: int, date: str):
        """Busca a presença pelo dia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT present FROM attendance WHERE student_id = ? AND date = ?", 
            (student_id, date)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    
    def get_free_attendance_by_date(self, student_id: int, date: str):
        """Busca presença de aluno gratuito por data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT lesson, present FROM free_attendance WHERE student_id = ? AND date = ?",
            (student_id, date)
        )
        row = cursor.fetchone()
        conn.close()
        return {"lesson": row[0], "present": bool(row[1])} if row else None

    def get_free_attendance_summary(self, student_id: int) -> Dict:
        """Resumo de presenças de aluno gratuito"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT 
                COUNT(*) as total,
                SUM(present) as present_count,
                SUM(CASE WHEN present = 0 THEN 1 ELSE 0 END) as absent_count
            FROM free_attendance WHERE student_id = ?""",
            (student_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total": row[0],
            "present": row[1] or 0,
            "absent": row[2] or 0,
            "percentage": (row[1] / row[0] * 100) if row[0] > 0 else 0
        }
    
    def promote_free_to_paid(self, free_student_id: int, course: str, course_days: str) -> bool:
        """Promove aluno gratuito para pago"""
        free_student = self.get_free_student(free_student_id)
        if not free_student:
            return False
        
        self.create_student(
            name=free_student['name'],
            course=course,
            course_days=course_days,
            class_time=free_student['class_time']
        )
        
        self.delete_free_student(free_student_id)
        return True
    
    def add_attendance_note(self, student_id: int, date: str, note: str) -> bool:
        """Adiciona observação à presença"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO attendance_notes (student_id, date, note) VALUES (?, ?, ?)",
                (student_id, date, note)
            )
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False

    def get_attendance_note(self, student_id: int, date: str) -> str:
        """Busca observação de uma data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT note FROM attendance_notes WHERE student_id = ? AND date = ?",
            (student_id, date)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else ""

    def get_daily_report_data(self, date: str, day_name: str) -> Dict:
        """Dados do relatório diário"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Busca alunos do dia
        students = self.get_all_students(active_only=True)
        
        day_map = {
            'Segunda':  ['seg', 'mon'],
            'Terça': ['ter', 'tue'],
            'Quarta': ['qua', 'wed'],
            'Quinta': ['qui', 'tur'],
            'Sexta': ['sex', 'fri'],
            'Sábado': ['sab', 'sat'],
            'Domingo': ['dom', 'sun']
        }
        search_terms = day_map.get(day_name, [day_name.lower()[:3]])
        day_students = []
        
        for s in students:
            db_days = s['course_days'].lower()
            if any(term in db_days for term in search_terms):
                day_students.append(s)
            
        
        # Busca presenças do dia
        cursor.execute(
            """SELECT student_id, present FROM attendance WHERE date = ?""",
            (date,)
        )
        attendance_dict = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Busca observações
        cursor.execute(
            """SELECT student_id, note FROM attendance_notes WHERE date = ?""",
            (date,)
        )
        notes_dict = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        result = []
        for student in day_students:
            result.append({
                'name': student['name'],
                'course': student['course'],
                'time': student.get('class_time', ''),
                'present': attendance_dict.get(student['id']),
                'note': notes_dict.get(student['id'], '')
            })
        result.sort(key=lambda x: (x['time'] or 'zz', x['name']))
        
        return {'date': date, 'day_name': day_name, 'students': result}