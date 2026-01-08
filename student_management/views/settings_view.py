import flet as ft
from utils.themes import ThemeManager

class SettingsView:
    def __init__(self, page: ft.Page, on_theme_change):
        self.page = page
        self.on_theme_change = on_theme_change # Callback que vem do App
        
    def create_theme_card(self, title, description, color, theme_code, icon):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=40, color=color),
                ft.Column([
                    ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(description, size=12, color=ft.colors.ON_SURFACE_VARIANT),
                ], expand=True),
                ft.Radio(value=theme_code, fill_color=color)
            ]),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            on_click=lambda e: self.change_theme(theme_code),
            ink=True
        )

    def change_theme(self, theme_code):
        # Atualiza visualmente o Radio Group
        self.theme_group.value = theme_code
        # Chama a função principal do App para mudar tudo
        self.on_theme_change(theme_code)
        
    def build(self):
        # Grupo de opções
        self.theme_group = ft.RadioGroup(
            content=ft.Column([
                self.create_theme_card(
                    "Studio Dark", 
                    "Modo escuro, ideal para ambientes de criação e foco.", 
                    ft.colors.DEEP_PURPLE_200, 
                    "dark", 
                    ft.icons.DARK_MODE
                ),
                self.create_theme_card(
                    "Tech Clean", 
                    "Visual limpo, claro e minimalista.", 
                    ft.colors.INDIGO, 
                    "light", 
                    ft.icons.LIGHT_MODE
                ),
                self.create_theme_card(
                    "Creative Energy", 
                    "Vibrante e energético com tons quentes.", 
                    ft.colors.ORANGE, 
                    "creative", 
                    ft.icons.PALETTE
                ),
            ], spacing=10),
            on_change=lambda e: self.on_theme_change(e.control.value)
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.SETTINGS, size=28),
                    ft.Text("Configurações & Aparência", size=24, weight=ft.FontWeight.BOLD),
                ]),
                ft.Divider(),
                ft.Text("Escolha o tema do sistema:", weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                self.theme_group,
                
                ft.Divider(height=40),
                ft.Text("Sobre o Sistema", weight=ft.FontWeight.BOLD),
                ft.Text("Versão 1.1 - Com controle financeiro e backups.", size=12, color=ft.colors.GREY_500),
            ]),
            padding=20,
            expand=True
        )