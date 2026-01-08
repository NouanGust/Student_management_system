import flet as ft
from database.db_manager import DatabaseManager
from components.common import CustomButton, SnackBarMessage

class TeacherProfileView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager, username: str):
        self.page = page
        self.db = db_manager
        self.username = username
        self.stats = self.db.get_teacher_stats()
        
        # Componentes de estado
        self.note_field = ft.TextField(
            label="Brain Dump (Esvazie sua mente aqui)",
            multiline=True,
            min_lines=8,
            max_lines=12,
            value=self.db.get_teacher_note(),
            border_color=ft.colors.OUTLINE_VARIANT,
            bgcolor=ft.colors.SURFACE,
            on_change=self.auto_save_note,
            hint_text="Ideias, lembretes rápidos, coisas para não esquecer..."
        )
        
    def auto_save_note(self, e):
        """Salva automaticamente ao digitar"""
        self.db.save_teacher_note(self.note_field.value)

    def get_rank_title(self, level):
        """Define o título baseado no nível"""
        if level <= 5: return "Instrutor Iniciante"
        if level <= 10: return "Professor Dedicado"
        if level <= 20: return "Mentor Experiente"
        if level <= 30: return "Mestre do Ensino"
        if level <= 50: return "Lenda da Educação"
        return "Grão-Mestre Supremo"

    def show_xp_rules(self, e):
        """Mostra como ganhar XP"""
        dialog = ft.AlertDialog(
            title=ft.Text("Como ganhar XP?"),
            content=ft.Column([
                ft.ListTile(leading=ft.Icon(ft.icons.PERSON_ADD), title=ft.Text("Novo Aluno"), subtitle=ft.Text("+50 XP")),
                ft.ListTile(leading=ft.Icon(ft.icons.CLASS_), title=ft.Text("Aula Ministrada"), subtitle=ft.Text("+10 XP")),
                ft.ListTile(leading=ft.Icon(ft.icons.ROCKET_LAUNCH), title=ft.Text("Aula Gratuita"), subtitle=ft.Text("+10 XP")),
                ft.Divider(),
                ft.Text("Dica: Mantenha a constância para subir de nível!", size=12, italic=True)
            ], tight=True, width=300),
            actions=[ft.TextButton("Entendi", on_click=lambda e: setattr(self.page.dialog, 'open', False) or self.page.update())]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def build_achievement_badge(self, icon, title, condition, color_active):
        """Cria uma medalha que se ilumina se a condição for verdadeira"""
        is_unlocked = condition
        
        icon_color = color_active if is_unlocked else ft.colors.OUTLINE
        bg_color = ft.colors.with_opacity(0.1, color_active) if is_unlocked else ft.colors.SURFACE_VARIANT
        opacity = 1.0 if is_unlocked else 0.5
        
        return ft.Container(
            content=ft.Icon(icon, size=30, color=icon_color),
            padding=15,
            bgcolor=bg_color,
            border_radius=50, # Circular
            border=ft.border.all(2, icon_color),
            opacity=opacity,
            tooltip=f"{title} ({'Desbloqueado' if is_unlocked else 'Bloqueado'})"
        )

    def build_level_card(self):
        """Card principal com Nível e Barra de Progresso"""
        level = self.stats['level']
        rank = self.get_rank_title(level)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.icons.AUTO_AWESOME, size=40, color=ft.colors.ON_PRIMARY),
                        padding=15,
                        bgcolor=ft.colors.PRIMARY,
                        border_radius=50
                    ),
                    ft.Column([
                        ft.Text(f"Nível {level}", size=14, color=ft.colors.PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Text(rank, size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    ], spacing=0),
                ], spacing=15, alignment=ft.MainAxisAlignment.START),
                
                ft.Container(height=20),
                
                # Barra de XP e Info
                ft.Row([
                    ft.Text("Progresso para o próximo nível", size=12, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.IconButton(ft.icons.INFO_OUTLINE, icon_size=16, icon_color=ft.colors.PRIMARY, tooltip="Ver regras de XP", on_click=self.show_xp_rules)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.ProgressBar(value=self.stats['progress'], color=ft.colors.PRIMARY, bgcolor=ft.colors.SURFACE_VARIANT, height=12, border_radius=6),
                
                ft.Row([
                    ft.Text(f"{int(self.stats['xp'])} XP Total", size=11, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Faltam {int(self.stats['next_level_xp'])} XP", size=11, color=ft.colors.ON_SURFACE_VARIANT)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ]),
            padding=25,
            bgcolor=ft.colors.SURFACE_VARIANT, # Destaque suave
            border_radius=15,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.colors.with_opacity(0.1, ft.colors.SHADOW))
        )

    def build_stat_box(self, icon, value, label, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=30, color=color),
                ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ft.Text(label, size=12, color=ft.colors.ON_SURFACE_VARIANT)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            bgcolor=ft.colors.SURFACE,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=12,
            expand=True
        )

    def build(self):
        # Define conquistas baseadas nos stats reais
        total_aulas = self.stats['classes']
        total_alunos = self.stats['students']
        
        achievements_row = ft.Row([
            self.build_achievement_badge(ft.icons.PLAY_ARROW, "Primeiros Passos (1ª Aula)", total_aulas >= 1, ft.colors.GREEN),
            self.build_achievement_badge(ft.icons.GROUPS, "Turma Cheia (10 Alunos)", total_alunos >= 10, ft.colors.BLUE),
            self.build_achievement_badge(ft.icons.WORKSPACE_PREMIUM, "Veterano (50 Aulas)", total_aulas >= 50, ft.colors.ORANGE),
            self.build_achievement_badge(ft.icons.DIAMOND, "Lendário (100 Aulas)", total_aulas >= 100, ft.colors.PURPLE),
            self.build_achievement_badge(ft.icons.ROCKET_LAUNCH, "Influenciador (50 Alunos)", total_alunos >= 50, ft.colors.RED),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15, wrap=True)

        # CORREÇÃO: Envolvemos a Column em um Container para usar padding
        return ft.Container(
            content=ft.Column([
                ft.Text("Meu Perfil & Conquistas", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                
                # 1. Card de Nível
                self.build_level_card(),
                
                ft.Container(height=5),
                
                # 2. Estatísticas
                ft.Row([
                    self.build_stat_box(ft.icons.GROUPS, self.stats['students'], "Alunos Ativos", ft.colors.BLUE),
                    self.build_stat_box(ft.icons.CLASS_, self.stats['classes'], "Aulas Ministradas", ft.colors.GREEN),
                    self.build_stat_box(ft.icons.STAR, int(self.stats['xp']), "XP Total", ft.colors.AMBER),
                ], spacing=10),
                
                ft.Container(height=10),
                
                # 3. Área de Conquistas (Visual Rewards)
                ft.Container(
                    content=ft.Column([
                        ft.Text("Galeria de Conquistas", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                        achievements_row
                    ]),
                    padding=20,
                    bgcolor=ft.colors.SURFACE,
                    border_radius=12,
                    border=ft.border.all(1, ft.colors.OUTLINE_VARIANT)
                ),
                
                ft.Container(height=10),
                
                # 4. Brain Dump
                ft.Text("Brain Dump - Notas Rápidas", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                self.note_field,
                
            ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=15),
            
            # Aqui aplicamos o padding para evitar corte no final da rolagem
            padding=ft.padding.only(bottom=20),
            expand=True
        )