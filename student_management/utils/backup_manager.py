import shutil
import os
from datetime import datetime
from database.db_manager import DatabaseManager

class BackupManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        # Define a pasta de backup relativa ao local do script
        self.backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
        self.ensure_backup_dir()

    def ensure_backup_dir(self):
        """Garante que a pasta de backups exista"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self) -> str:
        """Cria uma copia do banco de dados atual"""
        try:
            # Garante que o banco exista
            if not os.path.exists(self.db_manager.db_path):
                return None

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"students_backup_{timestamp}.db"
            destination = os.path.join(self.backup_dir, filename)
            
            # Copia o arquivo
            shutil.copy2(self.db_manager.db_path, destination)
            return filename
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
            return None

    def get_backups(self) -> list:
        """Lista todos os arquivos de backup ordenados por data (mais recente primeiro)"""
        if not os.path.exists(self.backup_dir):
            return []

        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.endswith(".db") and filename.startswith("students_backup_"):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                
                # Extrai data do nome ou do arquivo
                created_at = datetime.fromtimestamp(stat.st_mtime)
                size_kb = stat.st_size / 1024
                
                backups.append({
                    "name": filename,
                    "path": filepath,
                    "date": created_at.strftime("%d/%m/%Y %H:%M:%S"),
                    "size": f"{size_kb:.1f} KB"
                })
        
        # Ordena por nome (que contem data) decrescente
        backups.sort(key=lambda x: x['name'], reverse=True)
        return backups

    def restore_backup(self, filename: str) -> bool:
        """Restaura um backup especifico sobrescrevendo o atual"""
        try:
            source = os.path.join(self.backup_dir, filename)
            if not os.path.exists(source):
                return False
            
            # Fecha a conexao atual se possivel (SQLite lida bem, mas eh bom garantir)
            # A sobrescrita do arquivo fisico eh o metodo mais bruto mas eficaz para SQLite
            shutil.copy2(source, self.db_manager.db_path)
            return True
        except Exception as e:
            print(f"Erro ao restaurar: {e}")
            return False

    def delete_backup(self, filename: str) -> bool:
        """Remove um arquivo de backup"""
        try:
            path = os.path.join(self.backup_dir, filename)
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except:
            return False