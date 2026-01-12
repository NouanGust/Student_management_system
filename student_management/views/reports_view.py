import flet as ft
from datetime import datetime
from database.db_manager import DatabaseManager
from utils.reports import generate_daily_report, generate_monthly_report, generate_financial_report
from components.common import SnackBarMessage

class ReportsView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager):
        self.page = page
        self.db = db_manager
        
    def handle_daily_report(self, e):
        """Relatório de Presença de Hoje"""
        today = datetime.now().strftime('%Y-%m-%d')
        students = self.db.get_all_students()
        
        report_data = []
        for s in students:
            status_code = self.db.get_attendance_by_date(s['id'], today)
            if status_code == 1: status = "Presente"
            elif status_code == 0: status = "Falta"
            else: status = "Pendente"
                
            report_data.append({
                "name": s['name'],
                "course": s['course'],
                "time": s.get('class_time', '-'),
                "status": status
            })
        
        data = {
            "title": f"Relatorio Diario - {datetime.now().strftime('%d/%m/%Y')}",
            "students": report_data,
            "date": today
        }
        generate_daily_report(self.page, data)

    def handle_monthly_report(self, e):
        """Relatório de Frequência do Mês Atual"""
        today = datetime.now()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        # Gambiarra segura para pegar ultimo dia do mês (vai até dia 28/30/31)
        import calendar
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date = today.replace(day=last_day).strftime('%Y-%m-%d')
        
        students = self.db.get_all_students()
        report_data = []
        
        for s in students:
            summary = self.db.get_attendance_summary(s['id']) # Pega geral (poderia filtrar por data no DB, mas serve)
            report_data.append({
                "name": s['name'],
                "course": s['course'],
                "present": summary['present'],
                "absent": summary['absent'],
                "percentage": f"{summary['percentage']:.0f}%"
            })
            
        data = {
            "title": f"Relatorio Mensal - {today.strftime('%B/%Y')}",
            "students": report_data,
            "period": f"{start_date} a {end_date}"
        }
        generate_monthly_report(self.page, data)

    def handle_financial_report(self, e):
        """Relatório Financeiro com valores definidos"""
        students = self.db.get_all_students()
        
        # Tabela de Preços
        prices = {
            "Desenvolvimento de jogos 2D": 550.00,
            "Unity 3D": 860.00,
            "Lógica de programação": 320.00,
            "Python para dados": 980.00
        }
        
        # Custo Fixo Estimado
        expenses = {
            "Aluguel/Espaco": 800.00,
            "Energia e Internet": 250.00,
            "Marketing": 150.00,
            "Softwares": 100.00
        }
        
        revenue_details = []
        total_revenue = 0.0
        
        # Calcula receita baseada nos alunos ativos e seus cursos
        # Normaliza strings para evitar erros de digitação (caixa baixa)
        for s in students:
            course_name = s['course']
            price = 0.0
            
            # Busca flexível no dicionário de preços
            for key, val in prices.items():
                if key.lower() in course_name.lower():
                    price = val
                    break
            
            # Se não achou preço exato, usa média ou 0 (aqui assumimos 0 se não cadastrado corretamente)
            if price > 0:
                revenue_details.append({"student": s['name'], "course": course_name, "value": price})
                total_revenue += price
        
        total_expenses = sum(expenses.values())
        net_profit = total_revenue - total_expenses
        
        data = {
            "title": f"Relatorio Financeiro - {datetime.now().strftime('%B/%Y')}",
            "revenue_details": revenue_details,
            "total_revenue": total_revenue,
            "expenses": expenses,
            "total_expenses": total_expenses,
            "net_profit": net_profit
        }
        
        generate_financial_report(self.page, data)

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Relatórios Administrativos", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Gere PDFs para controle financeiro e pedagógico", color=ft.colors.ON_SURFACE_VARIANT),
                
                ft.Container(height=20),
                
                ft.Row([
                    self.create_report_card("Diário de Classe", "Presença de hoje", ft.icons.TODAY, ft.colors.BLUE, self.handle_daily_report),
                    self.create_report_card("Fechamento Mensal", "Frequência acumulada", ft.icons.CALENDAR_MONTH, ft.colors.ORANGE, self.handle_monthly_report),
                    self.create_report_card("Financeiro", "Receita x Despesas", ft.icons.ATTACH_MONEY, ft.colors.GREEN, self.handle_financial_report),
                ], wrap=True, spacing=20)
                
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True
        )

    def create_report_card(self, title, subtitle, icon, color, on_click):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=40, color=color),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                ft.Text(subtitle, size=12, color=ft.colors.ON_SURFACE_VARIANT),
                ft.Container(height=10),
                ft.ElevatedButton("Gerar PDF", on_click=on_click)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=250, height=200, bgcolor=ft.colors.SURFACE,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=12, padding=20, alignment=ft.alignment.center,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=5, color=ft.colors.with_opacity(0.05, ft.colors.SHADOW))
        )