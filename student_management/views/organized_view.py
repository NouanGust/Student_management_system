import flet as ft
from datetime import datetime
from database.db_manager import DatabaseManager
from components.common import SnackBarMessage
from collections import defaultdict

class OrganizedStudentsView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager):
        self.page = page
        self.db = db_manager
        self.organized_view = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)
        self.load_organized_students()
    
    def organize_students_by_day_time(self, students):
        organized = defaultdict(lambda: defaultdict(list))
        days_order = {
            'segunda': 1, 'seg': 1, 'terça': 2, 'ter': 2,
            'quarta': 3, 'qua': 3, 'quinta': 4, 'qui': 4,
            'sexta': 5, 'sex': 5, 'sábado': 6, 'sáb': 6, 'sab': 6,
            'domingo': 7, 'dom': 7
        }
        
        for student in students:
            days_text = student['course_days'].lower()
            time_text = student.get('class_time', 'Sem horário')
            found_days = set()
            for day_name, day_num in days_order.items():
                if day_name in days_text:
                    found_days.add(day_num)
            
            if not found_days:
                found_days.add(99)
            
            for day_num in found_days:
                if student not in organized[day_num][time_text]:
                    organized[day_num][time_text].append(student)
        return organized
    
    def load_organized_students(self):
        self.organized_view.controls.clear()
        students = self.db.get_all_students()
        
        if not students:
            self.organized_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.INBOX, size=100, color=ft.colors.OUTLINE),
                        ft.Text("Nenhum aluno cadastrado", size=18, color=ft.colors.ON_SURFACE_VARIANT),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=50
                )
            )
            self.page.update()
            return
        
        organized = self.organize_students_by_day_time(students)
        day_names = {
            1: 'Segunda-feira', 2: 'Terça-feira', 3: 'Quarta-feira',
            4: 'Quinta-feira', 5: 'Sexta-feira', 6: 'Sábado', 7: 'Domingo', 99: 'Outros'
        }
        
        tabs = []
        for day_num in sorted(organized.keys()):
            tab_content = self.build_times_for_day(organized[day_num])
            tabs.append(
                ft.Tab(
                    text=day_names.get(day_num, f'Dia {day_num}'),
                    content=ft.Container(content=tab_content, padding=15)
                )
            )
        
        self.organized_view.controls.append(
            ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=tabs,
                expand=True,
                indicator_color=ft.colors.PRIMARY, # Indicador segue o tema
                label_color=ft.colors.PRIMARY,
                unselected_label_color=ft.colors.ON_SURFACE_VARIANT
            )
        )
        self.page.update()
    
    def build_times_for_day(self, times_dict):
        times_column = ft.Column(spacing=15)
        sorted_times = sorted(times_dict.keys())
        
        for time in sorted_times:
            students_in_time = times_dict[time]
            
            # Header do horário com cor do tema (Secondary Container)
            time_header = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.ACCESS_TIME, color=ft.colors.ON_SECONDARY_CONTAINER, size=20),
                    ft.Text(
                        f"{time}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SECONDARY_CONTAINER
                    ),
                    ft.Text(
                        f"({len(students_in_time)} alunos)",
                        size=14,
                        color=ft.colors.ON_SECONDARY_CONTAINER,
                        opacity=0.7
                    )
                ], spacing=10),
                padding=10,
                bgcolor=ft.colors.SECONDARY_CONTAINER, # Adapta ao dark/light
                border_radius=8
            )
            
            times_column.controls.append(time_header)
            
            for student in students_in_time:
                student_card = self.build_student_mini_card(student)
                times_column.controls.append(
                    ft.Container(
                        content=student_card,
                        padding=ft.padding.only(left=20) # Indentação leve
                    )
                )
        
        return times_column
    
    def build_student_mini_card(self, student):
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        attendance_today = self.db.get_attendance_by_date(student['id'], today)
        
        if attendance_today is not None:
            if attendance_today == 1:
                icon = ft.icons.CHECK_CIRCLE
                icon_color = ft.colors.GREEN
                bg_color = ft.colors.SURFACE_VARIANT # Destaque suave
                disabled = True
            else:
                icon = ft.icons.CANCEL
                icon_color = ft.colors.ERROR
                bg_color = ft.colors.SURFACE_VARIANT
                disabled = True
        else:
            icon = ft.icons.CHECK_CIRCLE_OUTLINE
            icon_color = ft.colors.OUTLINE
            bg_color = ft.colors.SURFACE # Fundo padrão
            disabled = False
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.PERSON, size=30, color=ft.colors.PRIMARY),
                ft.Column([
                    ft.Text(student['name'], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    ft.Text(student['course'], size=12, color=ft.colors.ON_SURFACE_VARIANT),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=icon,
                    icon_color=icon_color,
                    on_click=None if disabled else lambda e, s=student: self.mark_quick_present(s),
                    disabled=disabled
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=bg_color,
            padding=10,
            border_radius=8,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT)
        )
    
    def mark_quick_present(self, student):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.db.mark_attendance(student['id'], today, True):
            SnackBarMessage.show(self.page, f"Presença marcada!", True)
            self.load_organized_students()
    
    def build(self):
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Alunos por Dia e Horário",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE
                    ),
                    ft.IconButton(
                        icon=ft.icons.REFRESH,
                        tooltip="Atualizar",
                        icon_color=ft.colors.PRIMARY,
                        on_click=lambda e: self.load_organized_students()
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.only(bottom=15)
            ),
            ft.Container(
                content=self.organized_view,
                expand=True,
                border_radius=10,
                padding=10
            )
        ], expand=True, spacing=0)