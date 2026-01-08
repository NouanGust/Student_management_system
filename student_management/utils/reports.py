from datetime import datetime

def generate_daily_report(data: dict) -> str:
    """Gera relatorio diario em formato TXT"""
    students = data['students']
    
    # --- CALCULOS DO RESUMO ---
    total = len(students)
    present_count = sum(1 for s in students if s['present'] == 1)
    absent_count = sum(1 for s in students if s['present'] == 0)
    pending_count = sum(1 for s in students if s['present'] is None)
    
    date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
    date_fmt = date_obj.strftime('%d/%m/%Y')
    
    lines = []
    
    # --- 1. CABECALHO E RESUMO (NO TOPO) ---
    lines.append("=" * 60)
    lines.append(f"RELATORIO DIARIO - {date_fmt} ({data['day_name']})")
    lines.append("=" * 60)
    lines.append(f"TOTAL DE ALUNOS: {total}")
    lines.append("-" * 60)
    lines.append(f"[+] Presentes:    {present_count}")
    lines.append(f"[x] Faltas:       {absent_count}")
    lines.append(f"[ ] Pendentes:    {pending_count}")
    lines.append("=" * 60)
    lines.append("")
    
    if not students:
        lines.append(">> Nenhum aluno agendado para hoje.")
        return "\n".join(lines)
    
    # --- 2. LISTAGEM DE ALUNOS ---
    
    # Ordena a lista: Primeiro por horario, depois por nome
    # (Assim a lista fica organizada visualmente mesmo sem os cabecalhos de grupo)
    students.sort(key=lambda x: (x['time'] or "ZZ", x['name']))
    
    for student in students:
        # Preparacao dos dados
        time = student['time'] if student['time'] else "Sem horario"
        course = student['course']
        name = student['name']
        
        # Define o texto da presenca
        if student['present'] == 1:
            status = "SITUACAO: PRESENTE [+]"
        elif student['present'] == 0:
            status = "SITUACAO: FALTA [x]"
        else:
            status = "SITUACAO: PENDENTE [ ]"
            
        # LINHA 1: Nome - Curso - Turma
        lines.append(f"ALUNO: {name} | CURSO: {course} | TURMA: {time}")
        
        # LINHA 2: Presenca
        lines.append(status)
        
        # LINHA 3: Observacao (se houver)
        if student['note']:
            lines.append(f"OBS: {student['note']}")
            
        # Separador entre alunos
        lines.append("-" * 60)
    
    lines.append("")
    lines.append("Gerado automaticamente pelo Sistema de Alunos")
    
    return "\n".join(lines)

def save_report(content: str, filename: str) -> str:
    """Salva relatorio em arquivo"""
    import os
    
    folder = "relatorios"
    os.makedirs(folder, exist_ok=True)
    
    filepath = os.path.join(folder, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath