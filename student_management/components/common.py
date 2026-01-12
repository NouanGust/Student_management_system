import flet as ft

class CustomAppBar(ft.AppBar):
    def __init__(self, title: str, username: str = "", on_logout=None):
        user_pill = ft.Container(
            content = ft.Row([
                ft.CircleAvatar(
                    content=ft.Text(username[0].upper() if username else "U"),
                    bgcolor = ft.colors.PRIMARY,
                    radius=16,
                ),
                ft.Column([
                    ft.Text(username, weight=ft.FontWeight.BOLD, size =12),
                    ft.Text("Online", size=10, color=ft.colors.GREEN, weight=ft.FontWeight.W_500)
                ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.START, spacing=10),

            padding=ft.padding.only(left=5, right=15, top=5, bottom=5),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=30,
            border = ft.border.all(1, ft.colors.OUTLINE_VARIANT),

            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        actions = []
        if username:
            actions.append(user_pill)
            actions.append(ft.VerticalDivider(width=20, color=ft.colors.TRANSPARENT)) # Espaçamento
            
        if on_logout:
            actions.append(
                ft.IconButton(
                    ft.icons.LOGOUT_ROUNDED,
                    tooltip="Sair",
                    icon_color=ft.colors.ERROR,
                    on_click=on_logout,
                    style=ft.ButtonStyle(
                        bgcolor={"": ft.colors.with_opacity(0.1, ft.colors.ERROR)},
                        shape=ft.CircleBorder(),
                    )
                )
            )
            actions.append(ft.VerticalDivider(width=10, color=ft.colors.TRANSPARENT))
        
        super().__init__(
            title=ft.Row([
                ft.Icon(ft.icons.SCHOOL_ROUNDED, color=ft.colors.PRIMARY, size=28),
                ft.Text(title, size=20, weight=ft.FontWeight.W_600, color=ft.colors.ON_SURFACE, font_family="Poppins"),
            ], spacing=15),

            center_title=False,

            bgcolor=ft.colors.SURFACE,
            elevation=0,
            shape=ft.Border(
                bottom=ft.BorderSide(1, ft.colors.OUTLINE_VARIANT)
            ),

            actions=actions,
            toolbar_height=70,
            
        )

class CustomButton(ft.ElevatedButton):
    def __init__(self, text: str, on_click=None, icon=None, width=None, color=None):
        bg_color = color or ft.colors.PRIMARY
        text_color = ft.colors.ON_PRIMARY if not color else ft.colors.WHITE 
        
        super().__init__(
            text=text.upper(), # Texto em caixa alta fica mais profissional em botões
            icon=icon,
            on_click=on_click,
            width=width or 200,
            height=45,
            style=ft.ButtonStyle(
                color=text_color,
                bgcolor=bg_color,
                shape=ft.RoundedRectangleBorder(radius=12), # Mais arredondado
                elevation=2, # Sombra leve
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, letter_spacing=0.5), # Tipografia forte
                icon_color=text_color
            )
        )

class CustomTextField(ft.TextField):
    def __init__(self, label: str, value: str = "", password: bool = False, width=None, hint_text=None, multiline=False, on_submit=None):
        super().__init__(
            label=label,
            value=value,
            password=password,
            can_reveal_password=password,
            width=width or 300,
            hint_text=hint_text,
            multiline=multiline,
            border_radius=8,
            on_submit=on_submit
        )

class ConfirmDialog(ft.AlertDialog):
    def __init__(self, title: str, content: str, on_confirm=None):
        super().__init__(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.close()),
                ft.FilledButton(
                    "Confirmar",
                    on_click=lambda e: [on_confirm() if on_confirm else None, self.close()]
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def close(self):
        self.open = False
        if self.page:
            self.page.update()

class SnackBarMessage:
    @staticmethod
    def show(page: ft.Page, message: str, success: bool = True):
        bg_color = ft.colors.GREEN if success else ft.colors.ERROR
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=bg_color,
            duration=3000,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=10,
            dismiss_direction=ft.DismissDirection.HORIZONTAL
        )
        page.snack_bar.open = True
        page.update()

class LoadingDialog(ft.AlertDialog):
    def __init__(self, message: str = "Carregando..."):
        super().__init__(
            modal=True,
            content=ft.Column(
                [ft.ProgressRing(), ft.Text(message)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True
            )
        )

class StudentCard(ft.Card):
    def __init__(self, student: dict, on_edit=None, on_delete=None, on_attendance=None, 
                 show_quick_attendance=False, on_quick_present=None, on_quick_absent=None, 
                 attendance_marked=False, on_history=None):
        self.student = student
        
        subtitle_items = [
            ft.Text(f"Curso: {student['course']}", size=14, color=ft.colors.ON_SURFACE),
            ft.Text(f"Dias: {student['course_days']}", size=12, color=ft.colors.ON_SURFACE_VARIANT),
        ]
        
        if student.get('class_time'):
            subtitle_items.append(
                ft.Text(f"Horário: {student['class_time']}", size=13, color=ft.colors.PRIMARY, weight=ft.FontWeight.BOLD)
            )
        
        if attendance_marked:
            subtitle_items.append(
                ft.Text("Registro feito hoje", size=11, color=ft.colors.TERTIARY, weight=ft.FontWeight.BOLD)
            )
        
        action_buttons = []
        
        if show_quick_attendance and not attendance_marked:
            if on_quick_present:
                action_buttons.append(ft.IconButton(
                    icon=ft.icons.CHECK_CIRCLE,
                    tooltip="Presença",
                    icon_color=ft.colors.GREEN,
                    on_click=lambda e: on_quick_present(student)
                ))
            if on_quick_absent:
                action_buttons.append(ft.IconButton(
                    icon=ft.icons.CANCEL,
                    tooltip="Falta",
                    icon_color=ft.colors.ERROR,
                    on_click=lambda e: on_quick_absent(student)
                ))

        if attendance_marked:
             action_buttons.append(ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, color=ft.colors.OUTLINE))

        action_buttons.append(ft.IconButton(icon=ft.icons.CALENDAR_MONTH, tooltip="Frequência", icon_color=ft.colors.PRIMARY, on_click=lambda e: on_attendance(student) if on_attendance else None))
        
        if on_history:
             action_buttons.append(ft.IconButton(icon=ft.icons.HISTORY, tooltip="Histórico", icon_color=ft.colors.SECONDARY, on_click=lambda e: on_history(student)))
        
        action_buttons.append(ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar", icon_color=ft.colors.ON_SURFACE_VARIANT, on_click=lambda e: on_edit(student) if on_edit else None))
        action_buttons.append(ft.IconButton(icon=ft.icons.DELETE, tooltip="Excluir", icon_color=ft.colors.ERROR, on_click=lambda e: on_delete(student) if on_delete else None))
        
        card_color = ft.colors.SURFACE_VARIANT if attendance_marked else ft.colors.SURFACE
        
        super().__init__(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.PERSON, size=40, color=ft.colors.PRIMARY),
                        title=ft.Text(student['name'], weight=ft.FontWeight.BOLD, size=16, color=ft.colors.ON_SURFACE),
                        subtitle=ft.Column(subtitle_items, spacing=2)
                    ),
                    ft.Row(action_buttons, alignment=ft.MainAxisAlignment.END)
                ], spacing=5),
                padding=10,
                bgcolor=card_color,
                border_radius=12
            ),
            elevation=1 if attendance_marked else 3
        )

class EventCard(ft.Card):
    def __init__(self, event: dict, on_delete=None, on_edit=None):
        self.event = event
        
        icon_map = {
            "aviso": (ft.icons.NOTIFICATIONS, ft.colors.TERTIARY),
            "compromisso": (ft.icons.EVENT, ft.colors.PRIMARY),
            "feriado": (ft.icons.CELEBRATION, ft.colors.SECONDARY),
        }
        icon, color = icon_map.get(event['event_type'], (ft.icons.INFO, ft.colors.OUTLINE))
        
        super().__init__(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(icon, size=30, color=color),
                        title=ft.Text(event['title'], weight=ft.FontWeight.BOLD, size=14, color=ft.colors.ON_SURFACE),
                        subtitle=ft.Column([
                            ft.Text(event['description'] or "", size=12, color=ft.colors.ON_SURFACE),
                            ft.Text(f"Data: {event['event_date']}", size=11, color=ft.colors.ON_SURFACE_VARIANT),
                        ], spacing=2),
                        trailing=ft.Row([
                            ft.IconButton(icon=ft.icons.EDIT_OUTLINED, icon_color=ft.colors.PRIMARY, tooltip="Editar", on_click=lambda e: on_edit(event) if on_edit else None),
                            ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=ft.colors.ERROR, tooltip="Excluir", on_click=lambda e: on_delete(event) if on_delete else None),
                        ], spacing=0, tight=True)
                    ),
                ]),
                padding=5,
                bgcolor=ft.colors.SURFACE,
            ),
            elevation=2
        )

class FreeStudentCard(ft.Card):
    def __init__(self, student: dict, on_edit=None, on_delete=None, on_promote=None):
        self.student = student
        
        lesson = student.get('start_lesson', 'Não definido')
        phone = student.get('phone', 'Sem telefone')
        
        subtitle_items = [
            ft.Text(f"Aula Inicial: {lesson}", size=14, color=ft.colors.ON_SURFACE),
            ft.Text(f"Dias: Sextas-feiras", size=12, color=ft.colors.ON_SURFACE_VARIANT),
        ]
        
        if student.get('class_time'):
            subtitle_items.append(
                ft.Text(f"Horário: {student['class_time']}", size=13, color=ft.colors.PRIMARY, weight=ft.FontWeight.BOLD)
            )
            
        subtitle_items.append(
            ft.Text(f"Telefone: {phone}", size=12, color=ft.colors.ON_SURFACE_VARIANT)
        )
        
        super().__init__(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.PERSON_OUTLINE, size=40, color=ft.colors.SECONDARY),
                        title=ft.Text(student['name'], weight=ft.FontWeight.BOLD, size=16, color=ft.colors.ON_SURFACE),
                        subtitle=ft.Column(subtitle_items, spacing=2)
                    ),
                    ft.Row([
                        ft.IconButton(icon=ft.icons.UPGRADE, tooltip="Promover", icon_color=ft.colors.GREEN, on_click=lambda e: on_promote(student) if on_promote else None),
                        ft.IconButton(icon=ft.icons.EDIT, tooltip="Editar", icon_color=ft.colors.PRIMARY, on_click=lambda e: on_edit(student) if on_edit else None),
                        ft.IconButton(icon=ft.icons.DELETE, tooltip="Excluir", icon_color=ft.colors.ERROR, on_click=lambda e: on_delete(student) if on_delete else None),
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=5),
                padding=10,
                bgcolor=ft.colors.SECONDARY_CONTAINER 
            ),
            elevation=2
        )