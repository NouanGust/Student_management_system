import os
from fpdf import FPDF
from components.common import SnackBarMessage
import flet as ft

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Student Manager Pro', 0, 1, 'C')
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def clean_text(text):
    """Remove caracteres que o FPDF padrão não suporta bem"""
    if not text: return ""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def generate_daily_report(page: ft.Page, data: dict):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt=clean_text(data['title']), ln=True, align='L')
        pdf.ln(5)
        
        # Tabela
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 10, "Aluno", 1, 0, 'C', 1)
        pdf.cell(50, 10, "Curso", 1, 0, 'C', 1)
        pdf.cell(30, 10, "Horario", 1, 0, 'C', 1)
        pdf.cell(50, 10, "Status", 1, 1, 'C', 1)
        
        pdf.set_font("Arial", size=10)
        for student in data['students']:
            if student['status'] == "Falta": pdf.set_text_color(200, 0, 0)
            elif student['status'] == "Presente": pdf.set_text_color(0, 120, 0)
            else: pdf.set_text_color(100, 100, 100)

            pdf.cell(60, 10, clean_text(student['name'][:25]), 1)
            pdf.cell(50, 10, clean_text(student['course'][:20]), 1)
            pdf.cell(30, 10, clean_text(student['time']), 1)
            pdf.cell(50, 10, clean_text(student['status']), 1, 1)
            pdf.set_text_color(0, 0, 0)

        open_pdf(page, pdf, "diario")
    except Exception as e:
        print(e)
        SnackBarMessage.show(page, "Erro ao gerar PDF", False)

def generate_monthly_report(page: ft.Page, data: dict):
    try:
        pdf = PDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt=clean_text(data['title']), ln=True, align='L')
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, txt=f"Periodo: {data['period']}", ln=True)
        pdf.ln(5)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(70, 10, "Aluno", 1, 0, 'C', 1)
        pdf.cell(60, 10, "Curso", 1, 0, 'C', 1)
        pdf.cell(20, 10, "Pres.", 1, 0, 'C', 1)
        pdf.cell(20, 10, "Faltas", 1, 0, 'C', 1)
        pdf.cell(20, 10, "%", 1, 1, 'C', 1)
        
        pdf.set_font("Arial", size=10)
        for s in data['students']:
            pdf.cell(70, 10, clean_text(s['name'][:30]), 1)
            pdf.cell(60, 10, clean_text(s['course'][:25]), 1)
            pdf.cell(20, 10, str(s['present']), 1, 0, 'C')
            pdf.cell(20, 10, str(s['absent']), 1, 0, 'C')
            pdf.cell(20, 10, s['percentage'], 1, 1, 'C')
            
        open_pdf(page, pdf, "mensal")
    except Exception as e:
        print(e)
        SnackBarMessage.show(page, "Erro ao gerar PDF Mensal", False)

def generate_financial_report(page: ft.Page, data: dict):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Título
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt=clean_text(data['title']), ln=True, align='C')
        pdf.ln(10)
        
        # 1. Receitas
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(220, 255, 220) # Verde claro
        pdf.cell(0, 10, " RECEITAS (Mensalidades)", 1, 1, 'L', 1)
        
        pdf.set_font("Arial", size=10)
        for item in data['revenue_details']:
            pdf.cell(80, 8, clean_text(item['student']), 0)
            pdf.cell(70, 8, clean_text(item['course']), 0)
            pdf.cell(40, 8, f"R$ {item['value']:.2f}", 0, 1, 'R')
            
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(150, 8, "TOTAL RECEITAS:", 0)
        pdf.set_text_color(0, 150, 0)
        pdf.cell(40, 8, f"R$ {data['total_revenue']:.2f}", 0, 1, 'R')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        # 2. Despesas
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(255, 220, 220) # Vermelho claro
        pdf.cell(0, 10, " DESPESAS OPERACIONAIS", 1, 1, 'L', 1)
        
        pdf.set_font("Arial", size=10)
        for name, value in data['expenses'].items():
            pdf.cell(150, 8, clean_text(name), 0)
            pdf.cell(40, 8, f"- R$ {value:.2f}", 0, 1, 'R')
            
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(150, 8, "TOTAL DESPESAS:", 0)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(40, 8, f"- R$ {data['total_expenses']:.2f}", 0, 1, 'R')
        pdf.set_text_color(0, 0, 0)
        
        # 3. Resumo Final (Lucro)
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_fill_color(200, 200, 200)
        
        # Cor do lucro (Verde se positivo, Vermelho se negativo)
        profit = data['net_profit']
        if profit >= 0:
            pdf.set_text_color(0, 100, 0)
            status = "LUCRO LIQUIDO"
        else:
            pdf.set_text_color(200, 0, 0)
            status = "PREJUIZO"
            
        pdf.cell(150, 12, f"RESULTADO ({status}):", 1, 0, 'R')
        pdf.cell(40, 12, f"R$ {profit:.2f}", 1, 1, 'R')
        
        open_pdf(page, pdf, "financeiro")
    except Exception as e:
        print(f"Erro financeiro: {e}")
        SnackBarMessage.show(page, "Erro ao gerar PDF Financeiro", False)

def open_pdf(page, pdf, prefix):
    filename = f"relatorio_{prefix}.pdf"
    pdf.output(filename)
    try:
        os.startfile(filename)
        SnackBarMessage.show(page, f"Gerado: {filename}", True)
    except AttributeError:
        # Tenta comando universal se não for Windows
        import subprocess
        try:
            subprocess.call(['xdg-open', filename])
        except:
            SnackBarMessage.show(page, f"Salvo: {filename}", True)