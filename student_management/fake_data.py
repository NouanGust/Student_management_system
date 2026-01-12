import sqlite3
import os
import random
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

# Lista de dados falsos para parecer real
NAMES = [
    "Ana Silva", "Bruno Souza", "Carla Mendes", "Daniel Oliveira", 
    "Eduarda Lima", "Felipe Santos", "Gabriela Rocha", "Hugo Martins",
    "Isabela Costa", "João Pedro", "Lucas Pereira", "Mariana Alves"
]

COURSES = ["Desenvolvimento de Jogos 2D", "Python para Dados", "Unity 3D Avançado", "Design de Games", "Lógica de Programação"]
DAYS_OPTIONS = ["Seg/Qua", "Ter/Qui", "Sexta", "Sábado"]
TIMES = ["09:00", "10:30", "14:00", "15:30", "19:00"]

def seed_database():
    print("Iniciando o plantio de dados falsos...")
    
    # Inicializa o gerenciador (que já acha o banco certo)
    db = DatabaseManager()
    
    # 1. Limpar dados antigos (Mantendo Usuários)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM attendance")
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM free_students")
    cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='students'") # Resetar IDs
    conn.commit()
    conn.close()
    print("Dados antigos limpos (Usuários mantidos).")

    # 2. Criar Alunos
    students_ids = []
    for name in NAMES:
        course = random.choice(COURSES)
        days = random.choice(DAYS_OPTIONS)
        time = random.choice(TIMES)
        
        # Usando método direto do DB Manager
        db.create_student(name, course, days, time)
        print(f"Aluno criado: {name}")

    # Recuperar IDs para gerar presença
    all_students = db.get_all_students()
    
    # 3. Gerar Presença (Histórico de 30 dias atrás até hoje)
    today = datetime.now()
    for student in all_students:
        # Gera ~8 aulas para trás
        for i in range(8):
            days_ago = (i * 3) + 1 # A cada 3 dias
            date = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            # 80% de chance de presença, 20% de falta (para ficar realista)
            present = random.random() > 0.2
            note = "" if present else "Atestado médico" if random.random() > 0.8 else "Sem justificativa"
            
            db.mark_attendance(student['id'], date, present, note)
    
    print("Histórico de presença gerado.")

    # 4. Criar Eventos Futuros (Calendário)
    event_titles = [
        ("Reunião de Pais", "aviso"), 
        ("Entrega de Projetos", "compromisso"), 
        ("Feriado Escolar", "feriado"),
        ("Workshop de Unity", "compromisso"),
        ("Manutenção dos PCs", "aviso")
    ]
    
    for i, (title, evt_type) in enumerate(event_titles):
        future_date = (today + timedelta(days=(i*4) + 2)).strftime('%Y-%m-%d')
        db.create_event(title, "Evento importante para o cronograma.", future_date, evt_type)
        
    print("Eventos do calendário criados.")

    # 5. Criar Alunos Gratuitos (Funil)
    free_names = ["Pedro H.", "Luana K.", "Marcos V.", "Júlia T."]
    for name in free_names:
        db.create_free_student(name, "1199999-9999", "14:00", "Aula 01 - Construct")
        
    print("Alunos gratuitos criados.")

    # 6. Atualizar Nota do Professor
    note_content = """- Lembrar de corrigir os exercícios da turma de Python.
- Comprar licença nova do Assets Store.
- Preparar material para o Workshop de sábado.
- Falar com a Ana sobre a reposição de aula."""
    db.save_teacher_note(note_content)
    
    print("\nBANCO DE DADOS POPULADO COM SUCESSO!")
    print("Agora abra o app e tire seus prints!")

if __name__ == "__main__":
    seed_database()
