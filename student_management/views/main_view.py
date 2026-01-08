import flet as ft
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from views.students_view import StudentsView
from views.free_students_view import FreeStudentsView
from views.organized_view import OrganizedStudentsView
from views.calendar_view import CalendarView
from views.reports_view import ReportsView
from views.daily_summary_view import DailySummaryView
from views.backup_view import BackupView
from views.settings_view import SettingsView
from views.profile_view import TeacherProfileView
from utils.keyboard_shortcuts import KeyboardHandler
from components.common import ConfirmDialog

class MainView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager, username: str, on_logout, on_theme_change):
        self.page = page
        self.db = db_manager
        self.username = username
        self.on_logout = on_logout
        
        # Inicializa Views
        self.students_view = StudentsView(page, db_manager)
        self.free_students_view = FreeStudentsView(page, db_manager)
        self.organized_view = OrganizedStudentsView(page, db_manager)
        self.calendar_view = CalendarView(page, db_manager)
        self.reports_view = ReportsView(page, db_manager)
        self.daily_summary_view = DailySummaryView(page, db_manager)
        self.backup_view = BackupView(page, db_manager)
        self.settings_view = SettingsView(page, on_theme_change)
        self.profile_view = TeacherProfileView(page, db_manager, username)
        
        # Atalhos
        self.keyboard_handler = KeyboardHandler(self)
        self.page.on_keyboard_event = self.keyboard_handler.handle_global_shortcuts
        
        # Navegação
        self.current_view = "daily_summary"
        self.content_container = ft.Container(expand=True)
        self.nav_rail = None
        
        self.update_content()
    
    def navigate_to(self, view_name: str):
        self.current_view = view_name
        self.update_content()
        self.page.update()

    def navigate_to_index(self, index: int):
        views_map = [
            "daily_summary", "dashboard", "organized", 
            "students", "free_students", "calendar", 
            "reports", "backup", "settings", "profile"
        ]
        if 0 <= index < len(views_map):
            if self.nav_rail:
                self.nav_rail.selected_index = index
                self.nav_rail.update()
            self.navigate_to(views_map[index])

    def confirm_logout(self):
        dialog = ConfirmDialog(
            title="Sair do Sistema",
            content="Deseja realmente desconectar?",
            on_confirm=lambda: self.on_logout(None)
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def update_content(self):
        self.page.dialog = None
        
        if self.current_view == "daily_summary":
            self.content_container.content = self.daily_summary_view.build()
        elif self.current_view == "dashboard":
            self.content_container.content = self.build_dashboard()
        elif self.current_view == "organized":
            self.content_container.content = self.organized_view.build()
        elif self.current_view == "students":
            self.content_container.content = self.students_view.build()
        elif self.current_view == "free_students":
            self.content_container.content = self.free_students_view.build()
        elif self.current_view == "calendar":
            self.content_container.content = self.calendar_view.build()
        elif self.current_view == "reports":
            self.content_container.content = self.reports_view.build()
        elif self.current_view == "backup":
            self.content_container.content = self.backup_view.build()
        elif self.current_view == "settings":
            self.content_container.content = self.settings_view.build()
        elif self.current_view == "profile":
            self.profile_view = TeacherProfileView(self.page, self.db, self.username)
            self.content_container.content = self.profile_view.build()
        
        self.page.update()
    
    def build_dashboard(self):
        """Constrói a tela de dashboard completa"""
        # 1. Busca Dados Gerais
        students = self.db.get_all_students()
        total_students = len(students)
        free_students = self.db.get_all_free_students()
        total_free_students = len(free_students)
        
        # 2. Calcula Presença Média
        total_percentage = 0
        count_active = 0
        for student in students:
            summary = self.db.get_attendance_summary(student['id'])
            if summary['total'] > 0:
                total_percentage += summary['percentage']
                count_active += 1
        
        avg_attendance = (total_percentage / count_active) if count_active > 0 else 0
        
        # 3. Busca Eventos Próximos (30 dias)
        today = datetime.now().strftime('%Y-%m-%d')
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        events = self.db.get_events(today, future_date)
        
        return ft.Column([
            # Cabeçalho
            ft.Container(
                content=ft.Column([
                    ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    ft.Text(f"Bem-vindo de volta, {self.username}!", size=16, color=ft.colors.ON_SURFACE_VARIANT),
                ]),
                margin=ft.margin.only(bottom=20)
            ),
            
            # Linha de Estatísticas (Cards Coloridos)
            ft.Row([
                self.create_stat_card("Total de Alunos", str(total_students), ft.icons.PEOPLE, ft.colors.PRIMARY),
                self.create_stat_card("Alunos Gratuitos", str(total_free_students), ft.icons.PEOPLE, ft.colors.TERTIARY),
                self.create_stat_card("Presença Média", f"{avg_attendance:.1f}%", ft.icons.TIMELINE, ft.colors.SECONDARY),
                self.create_stat_card("Eventos Próximos", str(len(events)), ft.icons.EVENT_NOTE, ft.colors.ERROR),
            ], spacing=20, wrap=True, alignment=ft.MainAxisAlignment.START),
            
            ft.Divider(height=40, color=ft.colors.OUTLINE_VARIANT),
            
            # Seção de Acesso Rápido
            ft.Container(
                content=ft.Column([
                    ft.Text("Acesso Rápido", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ]),
                margin=ft.margin.only(bottom=15)
            ),
            
            ft.Row([
                self.create_quick_access_card(
                    "Visão Organizada", 
                    "Ver grade de horários", 
                    ft.icons.VIEW_AGENDA, 
                    ft.colors.PRIMARY, 
                    lambda e: self.navigate_to("organized")
                ),
                self.create_quick_access_card(
                    "Gerenciar Alunos", 
                    "Adicionar ou editar", 
                    ft.icons.SCHOOL, 
                    ft.colors.SECONDARY, 
                    lambda e: self.navigate_to("students")
                ),
                self.create_quick_access_card(
                    "Alunos Gratuitos", 
                    "Funil de conversão", 
                    ft.icons.PERSON_ADD_ALT, 
                    ft.colors.TERTIARY, 
                    lambda e: self.navigate_to("free_students")
                ),
                self.create_quick_access_card(
                    "Calendário", 
                    "Agenda e avisos", 
                    ft.icons.CALENDAR_MONTH, 
                    ft.colors.ERROR, 
                    lambda e: self.navigate_to("calendar")
                ),
            ], spacing=20, wrap=True, alignment=ft.MainAxisAlignment.START),
            
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    def create_stat_card(self, title: str, value: str, icon, color):
        """Cria um card de estatística estilizado"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=30, color=color),
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(title, size=13, color=ft.colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500),
            ], spacing=5),
            width=240, 
            height=110, 
            bgcolor=ft.colors.SURFACE_VARIANT, # Cor de fundo adaptável (cinza escuro no dark mode)
            border_radius=16, 
            padding=20,
            # Sombra sutil
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color=ft.colors.with_opacity(0.1, ft.colors.SHADOW), offset=ft.Offset(0, 2))
        )
    
    def create_quick_access_card(self, title: str, description: str, icon, color, on_click):
        """Cria um card de navegação rápida"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, size=32, color=color),
                    padding=10,
                    bgcolor=ft.colors.with_opacity(0.1, color), # Fundo do ícone com opacidade
                    border_radius=10
                ),
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ft.Text(description, size=12, color=ft.colors.ON_SURFACE_VARIANT),
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            width=200, 
            height=160, 
            bgcolor=ft.colors.SURFACE, # Fundo padrão (branco ou preto)
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT), # Borda sutil
            border_radius=16, 
            padding=20,
            ink=True, 
            on_click=on_click
        )
    
    def build(self):
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(icon=ft.icons.TODAY_OUTLINED, selected_icon=ft.icons.TODAY, label="Hoje"),
                ft.NavigationRailDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD, label="Dashboard"),
                ft.NavigationRailDestination(icon=ft.icons.VIEW_AGENDA_OUTLINED, selected_icon=ft.icons.VIEW_AGENDA, label="Organizada"),
                ft.NavigationRailDestination(icon=ft.icons.PEOPLE_OUTLINED, selected_icon=ft.icons.PEOPLE, label="Alunos"),
                ft.NavigationRailDestination(icon=ft.icons.PERSON_ADD_ALT_OUTLINED, selected_icon=ft.icons.PERSON_ADD_ALT, label="Gratuitos"),
                ft.NavigationRailDestination(icon=ft.icons.CALENDAR_MONTH_OUTLINED, selected_icon=ft.icons.CALENDAR_MONTH, label="Calendário"),
                ft.NavigationRailDestination(icon=ft.icons.ASSESSMENT_OUTLINED, selected_icon=ft.icons.ASSESSMENT, label="Relatórios"),
                ft.NavigationRailDestination(icon=ft.icons.BACKUP_OUTLINED, selected_icon=ft.icons.BACKUP, label="Backup"),
                ft.NavigationRailDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label="Configurações"),
                ft.NavigationRailDestination(icon=ft.icons.ACCOUNT_CIRCLE_OUTLINED, selected_icon=ft.icons.ACCOUNT_CIRCLE, label="Perfil"),
            ],
            on_change=lambda e: self.navigate_to_index(e.control.selected_index)
        )
        
        view_indices = {
            "daily_summary": 0, "dashboard": 1, "organized": 2, 
            "students": 3, "free_students": 4, "calendar": 5, 
            "reports": 6, "backup": 7, "settings": 8, "profile": 9,
        }
        self.nav_rail.selected_index = view_indices.get(self.current_view, 0)

        return ft.Column([
            ft.Container(
                content=ft.Row([
                    self.nav_rail,
                    ft.VerticalDivider(width=1, color=ft.colors.OUTLINE_VARIANT),
                    self.content_container,
                ], expand=True),
                expand=True,
            )
        ], spacing=0, expand=True)