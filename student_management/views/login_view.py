import flet as ft
from utils.auth import AuthManager
from components.common import SnackBarMessage

class LoginView:
    def __init__(self, page: ft.Page, auth_manager: AuthManager, on_login_success):
        self.page = page
        self.auth = auth_manager
        self.on_login_success = on_login_success
        
        # Campos de texto estilizados
        self.username_field = ft.TextField(
            label="Usuário",
            width=300,
            prefix_icon=ft.icons.PERSON_OUTLINE,
            border_radius=12,
            bgcolor=ft.colors.WHITE,
            border_color=ft.colors.TRANSPARENT,
            filled=True,
            text_size=14,
            content_padding=20
        )
        
        self.password_field = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            width=300,
            prefix_icon=ft.icons.LOCK_OUTLINE,
            border_radius=12,
            bgcolor=ft.colors.WHITE,
            border_color=ft.colors.TRANSPARENT,
            filled=True,
            text_size=14,
            content_padding=20,
            on_submit=self.handle_login # Enter para logar
        )
        
        # Texto de erro animado
        self.error_text = ft.Text(
            "", 
            color=ft.colors.RED_200, 
            size=12, 
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )

    def handle_login(self, e):
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.show_error("Por favor, preencha todos os campos.")
            return
            
        if self.auth.verify_login(username, password):
            self.on_login_success(username)
        else:
            self.show_error("Usuário ou senha incorretos.")

    def handle_register(self, e):
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.show_error("Preencha usuário e senha para cadastrar.")
            return

        if self.auth.register_user(username, password):
            SnackBarMessage.show(self.page, "Conta criada! Faça login.", True)
        else:
            self.show_error("Este usuário já existe.")

    def show_error(self, message):
        self.error_text.value = message
        self.error_text.update()
        # Pequena animação de "tremor" ou flash poderia ser adicionada aqui

    def build(self):
        # Container do Formulário (O Cartão Branco)
        form_card = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(ft.icons.SCHOOL, size=60, color=ft.colors.BLUE_600),
                    padding=ft.padding.only(bottom=10)
                ),
                ft.Text("Bem-vindo", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_GREY_900),
                ft.Text("Gerencie seus alunos com maestria", size=14, color=ft.colors.GREY_500),
                
                ft.Container(height=20),
                
                self.username_field,
                ft.Container(height=5),
                self.password_field,
                
                ft.Container(content=self.error_text, height=20), # Espaço reservado para erro
                
                ft.Container(height=10),
                
                ft.ElevatedButton(
                    "ENTRAR",
                    on_click=self.handle_login,
                    width=300,
                    height=50,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_600,
                        shape=ft.RoundedRectangleBorder(radius=12),
                        elevation=5, # Sombra no botão
                    )
                ),
                
                ft.TextButton(
                    "Criar nova conta",
                    on_click=self.handle_register,
                    style=ft.ButtonStyle(color=ft.colors.BLUE_GREY_400)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            
            width=400,
            padding=40,
            bgcolor=ft.colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=30,
                color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                offset=ft.Offset(0, 10)
            ),
            # Animação de entrada
            offset=ft.transform.Offset(0, 0),
            animate_offset=ft.animation.Animation(600, ft.AnimationCurve.ELASTIC_OUT),
        )

        # Fundo Gradiente Elegante
        background = ft.Container(
            content=ft.Row([
                # Coluna vazia apenas para centralizar o card no meio da tela
                form_card
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            expand=True,
            alignment=ft.alignment.center,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    "#4158D0", # Azul Vibrante
                    "#C850C0", # Roxo/Rosa
                    "#FFCC70", # Amarelo Suave (dá um toque de luz)
                ],
                rotation=0.8
            )
        )
        
        return background