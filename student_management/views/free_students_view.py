import flet as ft
from database.db_manager import DatabaseManager
from components.common import CustomButton, CustomTextField, SnackBarMessage, ConfirmDialog, FreeStudentCard

class FreeStudentsView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager):
        self.page = page
        self.db = db_manager
        self.students_list = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)
        self.load_students()
    
    def load_students(self):
        self.students_list.controls.clear()
        students = self.db.get_all_free_students()
        
        if not students:
            self.students_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.PERSON_OFF, size=80, color=ft.colors.OUTLINE),
                        ft.Text("Nenhum aluno gratuito ativo", size=16, color=ft.colors.ON_SURFACE_VARIANT),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=50
                )
            )
        else:
            turmas = {}
            for s in students:
                turmas.setdefault(s['class_time'], []).append(s)
            
            for time in sorted(turmas.keys()):
                self.students_list.controls.append(self.build_turma_card(time, turmas[time]))
        
        self.page.update()
    
    def build_turma_card(self, time, students):
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.ACCESS_TIME_FILLED, color=ft.colors.ON_SECONDARY_CONTAINER),
                ft.Text(f"Turma {time}", weight=ft.FontWeight.BOLD, color=ft.colors.ON_SECONDARY_CONTAINER, size=16),
                ft.Text(f"({len(students)})", color=ft.colors.ON_SECONDARY_CONTAINER)
            ]),
            bgcolor=ft.colors.SECONDARY_CONTAINER,
            padding=10,
            border_radius=ft.border_radius.only(top_left=10, top_right=10)
        )
        
        cards = [FreeStudentCard(s, self.open_edit, self.confirm_delete, self.promote_student) for s in students]
        
        return ft.Column([
            header,
            ft.Container(
                content=ft.Column(cards, spacing=5),
                padding=10,
                border=ft.border.all(1, ft.colors.SECONDARY_CONTAINER),
                border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10)
            )
        ], spacing=0)

    def open_add_dialog(self, e):
        self.show_form()

    def open_edit(self, student):
        self.show_form(student)

    def show_form(self, student=None):
        is_edit = student is not None
        name_field = CustomTextField("Nome", value=student['name'] if is_edit else "")
        phone_field = CustomTextField("Telefone", value=student['phone'] if is_edit else "")
        
        time_dd = ft.Dropdown(
            label="Horário",
            options=[ft.dropdown.Option(t) for t in ["08:00 - 10:00", "10:00 - 12:00", "14:00 - 16:00"]],
            value=student['class_time'] if is_edit else None,
            filled=True, bgcolor=ft.colors.SURFACE_VARIANT
        )
        lesson_dd = ft.Dropdown(
            label="Aula Inicial",
            options=[ft.dropdown.Option(l) for l in ["2D", "3D", "Design", "Programação"]],
            value=student['start_lesson'] if is_edit else None,
            filled=True, bgcolor=ft.colors.SURFACE_VARIANT
        )

        def save(e):
            if not name_field.value: return
            if is_edit:
                self.db.update_free_student(student['id'], name_field.value, phone_field.value, time_dd.value, lesson_dd.value)
            else:
                self.db.create_free_student(name_field.value, phone_field.value, time_dd.value, lesson_dd.value)
            
            self.page.dialog.open = False
            self.page.update()
            self.load_students()
            SnackBarMessage.show(self.page, "Salvo com sucesso!", True)

        info_box = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.INFO, size=16, color=ft.colors.ON_TERTIARY_CONTAINER),
                    ft.Text("Regras do Curso Gratuito:", weight=ft.FontWeight.BOLD, color=ft.colors.ON_TERTIARY_CONTAINER),
                ]),
                ft.Text("- Duração de 4 aulas (Sextas-feiras)", size=12, color=ft.colors.ON_TERTIARY_CONTAINER),
            ], spacing=2),
            bgcolor=ft.colors.TERTIARY_CONTAINER,
            padding=10, border_radius=8
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Aluno" if is_edit else "Novo Aluno Gratuito"),
            content=ft.Column([name_field, phone_field, time_dd, lesson_dd, info_box], tight=True, spacing=15),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: setattr(self.page.dialog, 'open', False) or self.page.update()), ft.FilledButton("Salvar", on_click=save)]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def confirm_delete(self, student):
        dialog = ConfirmDialog("Excluir", f"Remover {student['name']}?", lambda: [self.db.delete_free_student(student['id']), self.load_students()])
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def promote_student(self, student):
        course_field = CustomTextField("Curso", width=300)
        days_field = CustomTextField("Dias (ex: Seg, Qua, Sex)", width=300)
        
        def confirm_promote(e):
            if not course_field.value or not days_field.value:
                SnackBarMessage.show(self.page, "Preencha curso e dias!", False)
                return
            
            if self.db.promote_free_to_paid(student['id'], course_field.value, days_field.value):
                SnackBarMessage.show(self.page, f"{student['name']} promovido!", True)
                self.page.dialog.open = False
                self.load_students()
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Promover {student['name']}"),
            content=ft.Column([
                ft.Text("Informe os dados do curso pago:"),
                course_field,
                days_field,
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(self.page.dialog, 'open', False) or self.page.update()),
                ft.TextButton("Promover", on_click=confirm_promote),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def build(self):
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Text("Alunos Gratuitos", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    ]),
                    CustomButton("Adicionar", on_click=self.open_add_dialog, icon=ft.icons.PERSON_ADD, width=150)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.only(bottom=15)
            ),
            ft.Container(content=self.students_list, expand=True)
        ], expand=True)