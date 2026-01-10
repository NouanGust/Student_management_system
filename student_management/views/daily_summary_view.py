import flet as ft
from datetime import datetime
from database.db_manager import DatabaseManager
from components.common import StudentCard, SnackBarMessage

class DailySummaryView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager):
        self.page = page
        self.db = db_manager
        self.summary_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.load_daily_summary()
    
    def load_daily_summary(self):
        self.summary_column.controls.clear()
        
        now = datetime.now()
        today_str = now.strftime('%Y-%m-%d')
        days_map = {0: 'seg', 1: 'ter', 2: 'qua', 3: 'qui', 4: 'sex', 5: 'sab', 6: 'dom'}
        today_key = days_map[now.weekday()]
        
        all_students = self.db.get_all_students()
        todays_students = [
            s for s in all_students 
            if today_key in s['course_days'].lower()
        ]
        todays_students.sort(key=lambda x: x.get('class_time', 'zz'))
        
        total = len(todays_students)
        present_count = 0
        absent_count = 0
        
        student_cards = []
        for student in todays_students:
            attendance = self.db.get_attendance_by_date(student['id'], today_str)
            if attendance is not None:
                if attendance == 1: present_count += 1
                else: absent_count += 1
            
            card = StudentCard(
                student=student,
                on_edit=None,
                on_delete=None,
                on_attendance=None,
                show_quick_attendance=True,
                attendance_marked=(attendance is not None),
                on_quick_present=self.mark_quick_present,
                on_quick_absent=self.mark_quick_absent
            )
            student_cards.append(card)

        header = ft.Container(
            content=ft.Row([
                self.create_stat("Total", total, ft.colors.ON_PRIMARY_CONTAINER),
                self.create_stat("Presentes", present_count, ft.colors.GREEN),
                self.create_stat("Faltas", absent_count, ft.colors.ERROR),
                self.create_stat("Pendentes", total - (present_count + absent_count), ft.colors.TERTIARY),
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            padding=20,
            bgcolor=ft.colors.PRIMARY_CONTAINER, 
            border_radius=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT)
        )
        
        self.summary_column.controls.append(header)
        
        if not todays_students:
            self.summary_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.BEDTIME, size=50, color=ft.colors.OUTLINE),
                        ft.Text("Nenhum aluno hoje. Bom descanso!", color=ft.colors.ON_SURFACE_VARIANT)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )
        else:
            self.summary_column.controls.extend([ft.Container(c) for c in student_cards])
            
        self.page.update()

    def create_stat(self, label, value, color):
        return ft.Column([
            ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color),
            ft.Text(label, size=12, color=ft.colors.ON_PRIMARY_CONTAINER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def mark_quick_present(self, student):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.db.mark_attendance(student['id'], today, True):
            SnackBarMessage.show(self.page, f"Presença: {student['name']}", True)
            self.load_daily_summary()

    def mark_quick_absent(self, student):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.db.mark_attendance(student['id'], today, False):
            SnackBarMessage.show(self.page, f"Falta: {student['name']}", False)
            self.load_daily_summary()

    def build(self):
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text("Visão de Hoje", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    ft.IconButton(ft.icons.REFRESH, on_click=lambda e: self.load_daily_summary(), icon_color=ft.colors.PRIMARY)
                ]),
                padding=ft.padding.only(bottom=10)
            ),
            ft.Container(
                content=self.summary_column,
                expand=True,
                border_radius=10,
                padding=5
            )
        ], expand=True)