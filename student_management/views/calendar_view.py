import flet as ft
from datetime import datetime, timedelta
from calendar import monthrange
from database.db_manager import DatabaseManager
from components.common import CustomButton, CustomTextField, SnackBarMessage, EventCard

class CalendarView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager):
        self.page = page
        self.db = db_manager
        self.current_date = datetime.now()
        self.events_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        # Estado do diálogo
        self.dialog_mode = "add"
        self.current_event = None
        
        # Componentes do Formulário
        self.title_field = CustomTextField("Título", width=400)
        self.description_field = CustomTextField("Descrição", width=400, multiline=True, hint_text="Detalhes do evento")
        self.event_type_dropdown = ft.Dropdown(
            label="Tipo",
            width=400,
            options=[
                ft.dropdown.Option("aviso", "Aviso"),
                ft.dropdown.Option("compromisso", "Compromisso"),
                ft.dropdown.Option("feriado", "Feriado"),
            ],
            value="aviso",
            border_radius=8,
            filled=True,
            bgcolor=ft.colors.SURFACE_VARIANT
        )
        
        self.event_date = datetime.now()
        self.date_button = ft.ElevatedButton(
            f"Data: {self.event_date.strftime('%d/%m/%Y')}",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda e: self.open_date_picker(),
            style=ft.ButtonStyle(
                color=ft.colors.PRIMARY,
                bgcolor=ft.colors.SURFACE
            )
        )
        
        # Diálogo (agora recriado dinamicamente para evitar travamentos)
        self.event_dialog = None 
        
        # Componentes do Calendário
        self.calendar_grid = ft.Column(spacing=5)
        self.month_year_text = ft.Text(
            self.get_month_year_text(),
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.ON_SURFACE
        )
        
        self.build_calendar()
        self.load_events()
    
    def get_month_year_text(self):
        months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        return f"{months[self.current_date.month - 1]} {self.current_date.year}"
    
    def build_calendar(self):
        self.calendar_grid.controls.clear()
        
        # Cabeçalho dos dias
        days_header = ft.Row(
            [
                ft.Container(
                    content=ft.Text(day, weight=ft.FontWeight.BOLD, size=12, color=ft.colors.ON_SURFACE_VARIANT),
                    width=40,
                    alignment=ft.alignment.center
                )
                for day in ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
            ],
            spacing=2
        )
        self.calendar_grid.controls.append(days_header)
        
        year, month = self.current_date.year, self.current_date.month
        first_day, num_days = monthrange(year, month)
        first_day = (first_day + 1) % 7
        
        week = [ft.Container(width=40, height=40) for _ in range(first_day)]
        
        for day in range(1, num_days + 1):
            date = datetime(year, month, day)
            is_today = date.date() == datetime.now().date()
            day_events = self.get_events_for_date(date)
            has_events = len(day_events) > 0
            
            # Lógica de Cores do Tema
            if is_today:
                bg_color = ft.colors.PRIMARY
                text_color = ft.colors.ON_PRIMARY
                border = None
            elif has_events:
                bg_color = ft.colors.TERTIARY_CONTAINER
                text_color = ft.colors.ON_TERTIARY_CONTAINER
                border = ft.border.all(1, ft.colors.TERTIARY)
            else:
                bg_color = ft.colors.SURFACE
                text_color = ft.colors.ON_SURFACE
                border = ft.border.all(1, ft.colors.OUTLINE_VARIANT)

            day_container = ft.Container(
                content=ft.Text(str(day), size=12, weight=ft.FontWeight.BOLD if is_today else ft.FontWeight.NORMAL, color=text_color),
                width=40, height=40,
                border=border,
                border_radius=20 if is_today else 8, # Hoje = Círculo, Outros = Quadrado arredondado
                bgcolor=bg_color,
                alignment=ft.alignment.center,
                on_click=lambda e, d=date: self.quick_add_event_for_date(d),
                ink=True,
                tooltip=f"{len(day_events)} eventos" if has_events else "Adicionar evento"
            )
            week.append(day_container)
            
            if len(week) == 7:
                self.calendar_grid.controls.append(ft.Row(week, spacing=2))
                week = []
        
        if week:
            self.calendar_grid.controls.append(ft.Row(week + [ft.Container(width=40, height=40)]*(7-len(week)), spacing=2))
        
        self.month_year_text.value = self.get_month_year_text()
        self.page.update()
    
    def get_events_for_date(self, date):
        date_str = date.strftime('%Y-%m-%d')
        return [e for e in self.db.get_events() if e['event_date'] == date_str]
    
    def previous_month(self, e):
        first = self.current_date.replace(day=1)
        self.current_date = (first - timedelta(days=1)).replace(day=1)
        self.build_calendar()
    
    def next_month(self, e):
        last_day = monthrange(self.current_date.year, self.current_date.month)[1]
        self.current_date = (self.current_date.replace(day=last_day) + timedelta(days=1))
        self.build_calendar()
    
    def load_events(self):
        self.events_list.controls.clear()
        events = self.db.get_events() # Pode filtrar por mês aqui se quiser
        
        if not events:
            self.events_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.EVENT_BUSY, size=60, color=ft.colors.OUTLINE),
                        ft.Text("Sem eventos recentes", size=14, color=ft.colors.ON_SURFACE_VARIANT)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            # Ordena por data decrescente
            events.sort(key=lambda x: x['event_date'], reverse=True)
            for event in events:
                self.events_list.controls.append(EventCard(event, self.confirm_delete_event, self.edit_event))
        self.page.update()

    # --- LÓGICA DE DIÁLOGOS E FORMULÁRIOS (Similar ao padrão anterior) ---
    def open_add_dialog(self, e):
        self.dialog_mode = "add"
        self.title_field.value = ""
        self.description_field.value = ""
        self.event_type_dropdown.value = "aviso"
        self.event_date = datetime.now()
        self.show_form_dialog("Novo Evento")

    def edit_event(self, event):
        self.dialog_mode = "edit"
        self.current_event = event
        self.title_field.value = event['title']
        self.description_field.value = event['description']
        self.event_type_dropdown.value = event['event_type']
        self.event_date = datetime.strptime(event['event_date'], '%Y-%m-%d')
        self.show_form_dialog("Editar Evento")

    def quick_add_event_for_date(self, date):
        self.dialog_mode = "add"
        self.title_field.value = ""
        self.description_field.value = ""
        self.event_type_dropdown.value = "compromisso"
        self.event_date = date
        self.show_form_dialog("Novo Evento")

    def show_form_dialog(self, title):
        self.date_button.text = f"Data: {self.event_date.strftime('%d/%m/%Y')}"
        
        self.event_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Column([self.title_field, self.description_field, self.event_type_dropdown, self.date_button], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.close_dialog()),
                ft.FilledButton("Salvar", on_click=self.save_event)
            ]
        )
        self.page.dialog = self.event_dialog
        self.event_dialog.open = True
        self.page.update()

    def close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def open_date_picker(self):
        self.page.overlay.clear()
        dp = ft.DatePicker(
            on_change=lambda e: [setattr(self, 'event_date', e.control.value), setattr(self.date_button, 'text', f"Data: {e.control.value.strftime('%d/%m/%Y')}"), self.page.update()],
            first_date=datetime(2023,1,1)
        )
        self.page.overlay.append(dp)
        self.page.update()
        dp.pick_date()

    def save_event(self, e):
        if not self.title_field.value:
            SnackBarMessage.show(self.page, "Título obrigatório!", False)
            return
        
        date_str = self.event_date.strftime('%Y-%m-%d')
        if self.dialog_mode == "add":
            self.db.create_event(self.title_field.value, self.description_field.value, date_str, self.event_type_dropdown.value)
            SnackBarMessage.show(self.page, "Evento criado!", True)
        else:
            self.db.update_event(self.current_event['id'], self.title_field.value, self.description_field.value, date_str, self.event_type_dropdown.value)
            SnackBarMessage.show(self.page, "Evento atualizado!", True)
        
        self.close_dialog()
        self.load_events()
        self.build_calendar()

    def confirm_delete_event(self, event):
        from components.common import ConfirmDialog
        dialog = ConfirmDialog("Excluir", f"Apagar '{event['title']}'?", lambda: [self.db.delete_event(event['id']), self.load_events(), self.build_calendar(), SnackBarMessage.show(self.page, "Excluído!", True)])
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def build(self):
        return ft.Row([
            # Painel Calendário
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.IconButton(ft.icons.CHEVRON_LEFT, on_click=self.previous_month, icon_color=ft.colors.PRIMARY),
                        self.month_year_text,
                        ft.IconButton(ft.icons.CHEVRON_RIGHT, on_click=self.next_month, icon_color=ft.colors.PRIMARY),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(),
                    self.calendar_grid
                ], spacing=10),
                padding=20,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=12,
                width=320 # Largura fixa para o calendário ficar elegante
            ),
            # Lista de Eventos
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Agenda", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                        CustomButton("Novo", on_click=self.open_add_dialog, icon=ft.icons.ADD, width=120)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    self.events_list
                ], spacing=10, expand=True),
                padding=20,
                # Fundo transparente ou sutil para integrar com a página
                expand=True
            )
        ], expand=True, spacing=30, vertical_alignment=ft.CrossAxisAlignment.START)