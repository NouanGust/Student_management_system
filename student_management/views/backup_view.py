import flet as ft
from utils.backup_manager import BackupManager
from database.db_manager import DatabaseManager
from components.common import CustomButton, SnackBarMessage, ConfirmDialog

class BackupView:
    def __init__(self, page: ft.Page, db_manager: DatabaseManager):
        self.page = page
        self.db = db_manager
        self.backup_manager = BackupManager(db_manager)
        self.backup_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.load_backups()

    def load_backups(self):
        self.backup_list.controls.clear()
        backups = self.backup_manager.get_backups()

        if not backups:
            self.backup_list.controls.append(
                ft.Container(
                    content=ft.Text("Nenhum backup encontrado.", color=ft.colors.ON_SURFACE_VARIANT),
                    alignment=ft.alignment.center, padding=20
                )
            )
        else:
            for backup in backups:
                self.backup_list.controls.append(self.create_backup_item(backup))
        self.page.update()

    def create_backup_item(self, backup):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.SAVE, color=ft.colors.PRIMARY),
                ft.Column([
                    ft.Text(backup['name'], weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    ft.Text(f"{backup['date']} • {backup['size']}", size=12, color=ft.colors.ON_SURFACE_VARIANT)
                ], expand=True),
                ft.IconButton(ft.icons.RESTORE, tooltip="Restaurar", icon_color=ft.colors.TERTIARY, on_click=lambda e: self.confirm_restore(backup)),
                ft.IconButton(ft.icons.DELETE, tooltip="Apagar", icon_color=ft.colors.ERROR, on_click=lambda e: self.confirm_delete(backup))
            ]),
            padding=15,
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=10,
            bgcolor=ft.colors.SURFACE,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=2, color=ft.colors.with_opacity(0.1, ft.colors.SHADOW), offset=ft.Offset(0, 1))
        )

    def handle_create_backup(self, e):
        if self.backup_manager.create_backup():
            SnackBarMessage.show(self.page, "Backup criado!", True)
            self.load_backups()
        else:
            SnackBarMessage.show(self.page, "Erro ao criar backup.", False)

    def confirm_restore(self, backup):
        dialog = ConfirmDialog("Restaurar", f"Isso substituirá os dados atuais pelos de {backup['date']}. Continuar?", 
                             lambda: [self.backup_manager.restore_backup(backup['name']), SnackBarMessage.show(self.page, "Sistema restaurado! Reinicie.", True)])
        self.page.dialog = dialog; dialog.open = True; self.page.update()

    def confirm_delete(self, backup):
        dialog = ConfirmDialog("Excluir", f"Apagar {backup['name']}?", 
                             lambda: [self.backup_manager.delete_backup(backup['name']), self.load_backups(), SnackBarMessage.show(self.page, "Backup apagado.", True)])
        self.page.dialog = dialog; dialog.open = True; self.page.update()

    def build(self):
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text("Gerenciador de Backups", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                    CustomButton("Novo Backup", icon=ft.icons.ADD_TO_PHOTOS, on_click=self.handle_create_backup, width=200, color=ft.colors.GREEN)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.only(bottom=20)
            ),
            ft.Container(content=self.backup_list, expand=True)
        ], expand=True, spacing=0)