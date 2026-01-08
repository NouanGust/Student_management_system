import flet as ft

class KeyboardHandler:
    def __init__(self, main_view):
        self.main_view = main_view
        self.page = main_view.page

    def handle_global_shortcuts(self, e: ft.KeyboardEvent):
        # 1. Atalho GLOBAL: ESC
        if e.key == "Escape":
            # Verifica se EXISTE um diálogo E se ele está ABERTO
            if self.page.dialog and self.page.dialog.open:
                self.try_close_view_dialog()
            else:
                # Se nenhum diálogo estiver aberto, chama o logout
                self.main_view.confirm_logout()
            return

        # 2. Atalho GLOBAL: Navegação (Ctrl + 1 a 7)
        if e.ctrl:
            try:
                if e.key == "1": self.main_view.navigate_to_index(0)
                elif e.key == "2": self.main_view.navigate_to_index(1)
                elif e.key == "3": self.main_view.navigate_to_index(2)
                elif e.key == "4": self.main_view.navigate_to_index(3)
                elif e.key == "5": self.main_view.navigate_to_index(4)
                elif e.key == "6": self.main_view.navigate_to_index(5)
                elif e.key == "7": self.main_view.navigate_to_index(6)
                
                elif e.key.lower() == "n": self.handle_new_item()
                elif e.key.lower() == "s": self.handle_save()
            except Exception as ex:
                print(f"Erro no atalho: {ex}")

    def try_close_view_dialog(self):
        """Fecha o diálogo usando o método da view para limpar estados internos"""
        view_name = self.main_view.current_view
        
        # Mapeia qual view estamos
        current_view_obj = None
        if view_name == "students":
            current_view_obj = self.main_view.students_view
        elif view_name == "free_students":
            current_view_obj = self.main_view.free_students_view
        elif view_name == "calendar":
            current_view_obj = self.main_view.calendar_view
            
        # Tenta usar o método close_dialog da view se existir
        if current_view_obj and hasattr(current_view_obj, "close_dialog"):
            current_view_obj.close_dialog(None)
        else:
            # Fallback genérico (para logout dialog, etc)
            self.page.dialog.open = False
            self.page.update()

    def handle_new_item(self):
        view = self.main_view.current_view
        if view == "students": self.main_view.students_view.open_add_dialog(None)
        elif view == "free_students": self.main_view.free_students_view.open_add_dialog(None)
        elif view == "calendar": self.main_view.calendar_view.open_add_dialog(None)
        elif view == "daily_summary": self.main_view.daily_summary_view.load_daily_summary()

    def handle_save(self):
        if self.page.dialog and self.page.dialog.open:
            view = self.main_view.current_view
            if view == "students": self.main_view.students_view.save_student(None)
            elif view == "free_students": self.main_view.free_students_view.save_student(None)
            elif view == "calendar": self.main_view.calendar_view.save_event(None)