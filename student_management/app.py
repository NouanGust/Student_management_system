import flet as ft
from database.db_manager import DatabaseManager
from utils.auth import AuthManager
from views.login_view import LoginView
from views.main_view import MainView
from components.common import CustomAppBar 
from utils.themes import ThemeManager

class StudentManagementApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Sistema de Controle de Alunos"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.padding = 0
        
        # Fontes
        self.page.fonts = {
            "Poppins": "https://fonts.gstatic.com/s/poppins/v20/pxiByp8kv8JHgFVrLGT9Z1xlFQ.woff2",
            "Poppins-Bold": "https://fonts.gstatic.com/s/poppins/v20/pxiByp8kv8JHgFVrLCz7Z1xlFQ.woff2"
        }
        
        self.page.theme = ft.Theme(font_family="Poppins")
        
        # Inicializa o tema padrão (Tech Clean)
        ThemeManager.apply_theme(self.page, "light")
        
        # Inicializa banco de dados e autenticação
        self.db = DatabaseManager()
        self.auth = AuthManager(self.db)
        self.username = ""
        
        # Estado
        self.current_user = None
        self.current_view = None
        
        # Inicia na tela de login
        self.show_login()
    
    def change_theme_callback(self, theme_name):
        ThemeManager.apply_theme(self.page, theme_name)
        self.page.theme.font_family = "Poppins"
        self.page.update()
    
    def show_login(self):
        self.page.controls.clear()
        self.page.appbar = None 
        
        login_view = LoginView(
            page=self.page,
            auth_manager=self.auth,
            on_login_success=self.on_login_success
        )
        self.current_view = login_view
        self.page.add(login_view.build())
        self.page.update()
    
    def on_login_success(self, username: str):
        self.current_user = username
        self.show_main()
    
    def show_main(self):
        """Exibe a tela principal"""
        self.page.controls.clear()
        
    
        main_view = MainView(
            page=self.page, 
            db_manager=self.db, 
            username=self.current_user, 
            on_logout=self.on_logout,
            on_theme_change=self.change_theme_callback
        )
        
        # Configura AppBar
        self.page.appbar = CustomAppBar(
            title="Sistema de Controle de Alunos",
            username=self.current_user,
            on_logout=self.on_logout
        )
        
        self.current_view = main_view
        self.page.add(main_view.build())
        self.page.update()
    
    def on_logout(self, e):
        self.current_user = None
        self.show_login()

def main(page: ft.Page):
    app = StudentManagementApp(page)

if __name__ == "__main__":
    ft.app(target=main)