import flet as ft
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from components.common import (
    CustomButton, CustomTextField, SnackBarMessage,
    ConfirmDialog, StudentCard
)

class StudentsView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager):
        self.page = page
        self.db = db_manager
        
        # Lista de alunos (com rolagem)
        self.students_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        # Barra de busca estilizada (Seguindo o tema)
        self.search_field = ft.TextField(
            hint_text="Buscar aluno...",
            prefix_icon=ft.icons.SEARCH,
            width=300,
            on_change=self.filter_students,
            border_radius=20,
            filled=True,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_width=0,
            text_size=14,
            content_padding=10
        )
        
        # Carrega dados iniciais
        self.load_students()
    
    def filter_students(self, e):
        """Filtra alunos visualmente sem recarregar do banco"""
        search_term = self.search_field.value.lower()
        for card_container in self.students_list.controls:
            if isinstance(card_container.content, StudentCard):
                card = card_container.content
                student = card.student
                # Lógica de filtro (Nome ou Curso)
                visible = (search_term in student['name'].lower() or 
                          search_term in student['course'].lower())
                card_container.visible = visible
        self.page.update()
    
    def load_students(self):
        """Busca dados do banco e monta a lista"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.students_list.controls.clear()
        
        try:
            students = self.db.get_all_students()
            
            if not students:
                self.students_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.SCHOOL, size=80, color=ft.colors.OUTLINE_VARIANT),
                            ft.Text("Nenhum aluno cadastrado", size=18, color=ft.colors.ON_SURFACE_VARIANT),
                            ft.Text("Clique em 'Novo Aluno' para começar", size=14, color=ft.colors.ON_SURFACE_VARIANT)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        alignment=ft.alignment.center,
                        padding=50
                    )
                )
            else:
                for student in students:
                    attendance_today = self.db.get_attendance_by_date(student['id'], today)
                    
                    # Cria o card passando os métodos callback
                    # O StudentCard já cuida das cores do tema internamente
                    card = StudentCard(
                        student=student,
                        on_edit=self.open_edit_dialog,
                        on_delete=self.confirm_delete,
                        on_attendance=self.open_attendance_dialog,
                        on_history=self.open_history_dialog,
                        show_quick_attendance=True,
                        on_quick_present=self.mark_quick_present,
                        on_quick_absent=self.mark_quick_absent,
                        attendance_marked=attendance_today is not None
                    )
                    self.students_list.controls.append(ft.Container(content=card))
            
            self.page.update()
            
        except Exception as ex:
            print(f"Erro ao carregar alunos: {ex}")
            SnackBarMessage.show(self.page, "Erro ao carregar lista de alunos", False)

    # =========================================================================
    # DIALOG DE ADICIONAR / EDITAR (Lógica Dinâmica + Estilo Novo)
    # =========================================================================
    def open_student_form(self, student=None):
        """Cria e abre o diálogo de formulário (Genérico para Add/Edit)"""
        is_edit = student is not None
        
        # Cria campos NOVOS para evitar travamento
        name_field = CustomTextField("Nome Completo", width=400, value=student['name'] if is_edit else "")
        course_field = CustomTextField("Curso", width=400, value=student['course'] if is_edit else "")
        days_field = CustomTextField("Dias (ex: Seg, Qua)", width=400, value=student['course_days'] if is_edit else "")
        time_field = CustomTextField("Horário (ex: 14:00)", width=400, value=student.get('class_time', "") if is_edit else "")
        
        def save_action(e):
            # Validação
            if not name_field.value or not course_field.value:
                SnackBarMessage.show(self.page, "Nome e Curso são obrigatórios!", False)
                return

            try:
                if is_edit:
                    self.db.update_student(student['id'], name_field.value, course_field.value, days_field.value, time_field.value)
                    msg = "Aluno atualizado!"
                else:
                    self.db.create_student(name_field.value, course_field.value, days_field.value, time_field.value)
                    msg = "Aluno criado!"
                
                self.close_dialog()
                SnackBarMessage.show(self.page, msg, True)
                self.load_students()
                
            except Exception as ex:
                SnackBarMessage.show(self.page, f"Erro ao salvar: {ex}", False)

        # Diálogo estilizado
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Aluno" if is_edit else "Adicionar Aluno"),
            content=ft.Column([
                name_field, course_field, days_field, time_field
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.close_dialog()),
                ft.FilledButton("Salvar", on_click=save_action), # Botão com destaque
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def open_add_dialog(self, e):
        self.open_student_form(None)

    def open_edit_dialog(self, student):
        self.open_student_form(student)

    # =========================================================================
    # DIALOG DE PRESENÇA (Estilizado)
    # =========================================================================
    def open_attendance_dialog(self, student):
        attendance_date = datetime.now()
        
        # Botão de data estilizado
        date_btn = ft.ElevatedButton(
            f"Data: {attendance_date.strftime('%d/%m/%Y')}",
            icon=ft.icons.CALENDAR_MONTH,
            style=ft.ButtonStyle(
                color=ft.colors.PRIMARY,
                bgcolor=ft.colors.SURFACE_VARIANT
            )
        )
        
        def handle_present(present: bool):
            date_str = attendance_date.strftime('%Y-%m-%d')
            if self.db.mark_attendance(student['id'], date_str, present):
                self.close_dialog()
                SnackBarMessage.show(self.page, f"{'Presença' if present else 'Falta'} registrada!", True)
                self.load_students() 

        summary = self.db.get_attendance_summary(student['id'])
        
        # Painel de resumo com cores semânticas
        content_col = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Column([ft.Text("Presenças", size=12), ft.Text(str(summary['present']), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN)]),
                    ft.Column([ft.Text("Faltas", size=12), ft.Text(str(summary['absent']), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ERROR)]),
                    ft.Column([ft.Text("Freq.", size=12), ft.Text(f"{summary['percentage']:.0f}%", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY)]),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                padding=15,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=10
            ),
            ft.Divider(),
            ft.Text("Selecione a data:", size=12),
            date_btn, 
            ft.Row([
                CustomButton("Presente", on_click=lambda e: handle_present(True), icon=ft.icons.CHECK, color=ft.colors.GREEN, width=130),
                CustomButton("Falta", on_click=lambda e: handle_present(False), icon=ft.icons.CLOSE, color=ft.colors.ERROR, width=130),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        ], tight=True, spacing=15)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Frequência - {student['name']}"),
            content=content_col,
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.close_dialog())]
        )
        
        # Lógica do DatePicker
        def open_picker_clean(e):
            self.page.overlay.clear()
            def on_date_change(evt):
                if evt.control.value:
                    nonlocal attendance_date
                    attendance_date = evt.control.value
                    date_btn.text = f"Data: {attendance_date.strftime('%d/%m/%Y')}"
                    self.page.update()

            dp = ft.DatePicker(
                on_change=on_date_change,
                first_date=datetime(2023, 1, 1),
                last_date=datetime.now() + timedelta(days=365)
            )
            self.page.overlay.append(dp)
            self.page.update()
            dp.pick_date()
            
        date_btn.on_click = open_picker_clean

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    # =========================================================================
    # DIALOG DE HISTÓRICO (Com Filtros e Ações)
    # =========================================================================
    def open_history_dialog(self, student):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        history_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=400)
        date_range_label = ft.Text("", size=12, color=ft.colors.ON_SURFACE_VARIANT)

        def refresh_list(start, end):
            history_list.controls.clear()
            date_range_label.value = f"Período: {start.strftime('%d/%m')} a {end.strftime('%d/%m')}"
            
            data = self.db.get_attendance(student['id'], start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
            att_map = {d['date']: d['present'] for d in data}
            
            curr = start
            while curr <= end:
                d_str = curr.strftime('%Y-%m-%d')
                status = att_map.get(d_str)
                row = self.build_history_row(student, d_str, curr, status, lambda: refresh_list(start, end))
                history_list.controls.append(row)
                curr += timedelta(days=1)
            self.page.update()

        # Botões de filtro rápidos
        filter_row = ft.Row([
            ft.TextButton("7 dias", on_click=lambda e: refresh_list(datetime.now()-timedelta(days=7), datetime.now())),
            ft.TextButton("30 dias", on_click=lambda e: refresh_list(datetime.now()-timedelta(days=30), datetime.now())),
        ], alignment=ft.MainAxisAlignment.CENTER)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Histórico: {student['name']}"),
            content=ft.Column([filter_row, date_range_label, ft.Divider(), history_list], tight=True, width=500),
            actions=[ft.TextButton("Fechar", on_click=lambda e: self.close_dialog())]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
        # Carrega inicial
        refresh_list(start_date, end_date)

    def build_history_row(self, student, date_str, date_obj, status, refresh_callback):
        """Cria uma linha do histórico com ações"""
        if status is None:
            icon, color = ft.icons.CIRCLE_OUTLINED, ft.colors.OUTLINE
        elif status:
            icon, color = ft.icons.CHECK_CIRCLE, ft.colors.GREEN
        else:
            icon, color = ft.icons.CANCEL, ft.colors.ERROR

        def set_att(present):
            self.db.mark_attendance(student['id'], date_str, present)
            refresh_callback() 
        
        def del_att():
            # Acesso direto para remover (poderia estar no db_manager, mas ok por simplicidade)
            conn = self.db.get_connection() 
            conn.cursor().execute("DELETE FROM attendance WHERE student_id=? AND date=?", (student['id'], date_str))
            conn.commit()
            conn.close()
            refresh_callback()

        note_text = self.db.get_attendance_note(student['id'], date_str)
        
        row_content = ft.Row([
            ft.Icon(icon, color=color, size=20),
            ft.Text(date_obj.strftime("%d/%m - %a"), size=14, expand=True, color=ft.colors.ON_SURFACE),
            
            # Botões mini
            ft.IconButton(ft.icons.CHECK, icon_color=ft.colors.GREEN, icon_size=18, on_click=lambda e: set_att(True), tooltip="Presente"),
            ft.IconButton(ft.icons.CLOSE, icon_color=ft.colors.ERROR, icon_size=18, on_click=lambda e: set_att(False), tooltip="Falta"),
            ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.OUTLINE, icon_size=18, on_click=lambda e: del_att(), tooltip="Limpar"),
        ], spacing=2)

        return ft.Container(
            content=ft.Column([
                row_content,
                ft.Text(f"Obs: {note_text}", size=11, italic=True, color=ft.colors.PRIMARY) if note_text else ft.Container()
            ], spacing=2),
            padding=5,
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.OUTLINE_VARIANT))
        )

    # =========================================================================
    # UTILITÁRIOS
    # =========================================================================
    def close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def confirm_delete(self, student):
        def delete_action():
            self.db.delete_student(student['id'])
            self.load_students()
            SnackBarMessage.show(self.page, "Aluno removido", True)

        dialog = ConfirmDialog("Excluir", f"Remover {student['name']}?", delete_action)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def mark_quick_present(self, student):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.db.get_attendance_by_date(student['id'], today) is not None:
            SnackBarMessage.show(self.page, "Já marcado hoje!", False)
        else:
            self.db.mark_attendance(student['id'], today, True)
            SnackBarMessage.show(self.page, f"Presença: {student['name']}", True)
            self.load_students() 

    def mark_quick_absent(self, student):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.db.get_attendance_by_date(student['id'], today) is not None:
            SnackBarMessage.show(self.page, "Já marcado hoje!", False)
        else:
            self.db.mark_attendance(student['id'], today, False)
            SnackBarMessage.show(self.page, f"Falta: {student['name']}", False)
            self.load_students()

    def open_date_picker(self, on_change_callback):
        pass

    # =========================================================================
    # BUILD (INTERFACE)
    # =========================================================================
    def build(self):
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    self.search_field,
                    CustomButton(
                        "Novo Aluno",
                        on_click=self.open_add_dialog,
                        icon=ft.icons.ADD,
                        width=180
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.only(bottom=20)
            ),
            ft.Container(
                content=self.students_list,
                expand=True,
                # Fundo transparente/suave para integrar com o tema da página
                border_radius=10,
                padding=5
            )
        ], expand=True, spacing=0)