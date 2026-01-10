import flet as ft
from datetime import datetime
from database.db_manager import DatabaseManager
from utils.reports import generate_daily_report, save_report
from components.common import CustomButton, SnackBarMessage

class ReportsView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager):
        self.page = page
        self.db = db_manager
    
    def generate_daily(self, e):
        """Gera relatório diário"""
        date = datetime.now().strftime('%Y-%m-%d')
        day_name = datetime.now().strftime('%A')  # Nome do dia
        
        # Traduz dia
        days_pt = {
            'Monday': 'Segunda', 'Tuesday': 'Terça',
            'Wednesday': 'Quarta', 'Thursday': 'Quinta',
            'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        day_name = days_pt.get(day_name, day_name)
        
        data = self.db.get_daily_report_data(date, day_name)
        content = generate_daily_report(data)
        
        filename = f"relatorio_diario_{date}.txt"
        filepath = save_report(content, filename)
        
        SnackBarMessage.show(self.page, f"Relatório salvo: {filepath}", True)
    
    def build(self):
        return ft.Column([
            ft.Text("Relatórios", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            CustomButton(
                "Gerar Relatório Diário",
                on_click=self.generate_daily,
                icon=ft.icons.DESCRIPTION,
                width=250
            )
        ])