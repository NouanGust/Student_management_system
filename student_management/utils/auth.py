import bcrypt
from typing import Optional
from database.db_manager import DatabaseManager

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        # Chave para restaurar senha --> TO DO colocar em um .env
        self.MASTER_KEY = "admin"

    # --- Cria um hash para a senha ---
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    # --- Verifica as hashs de senhas ---
    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            return False
    
    def register_user(self, username: str, password: str) -> bool:
        if self.db.get_user(username):
            return False
            
        password_hash = self.hash_password(password)
        return self.db.create_user(username, password_hash)
    
    def login(self, username: str, password: str) -> bool:
        """Realiza o login"""
        print(f"Tentando logar usuário: {username}") # Debug
        user = self.db.get_user(username)
        
        if not user:
            print("Usuário não encontrado no banco de dados.")
            return False
        
        # Garante o acesso ao hash independente se o banco retorna Tupla ou Dicionário
        try:
            # Tenta acessar como dicionário (sqlite3.Row)
            stored_hash = user['password_hash']
        except (TypeError, IndexError):
            # Se falhar, tenta acessar pelo índice (assumindo que hash é a 3ª coluna: id, username, hash)
            # Se sua tabela for diferente, ajuste o índice [2]
            try:
                stored_hash = user[2] 
            except IndexError:
                print("Erro: Estrutura do usuário retornada pelo banco é inválida.")
                print(f"Dados recebidos: {user}")
                return False

        if self.verify_password(password, stored_hash):
            print("Senha verificada com sucesso!")
            return True
        else:
            print("Senha incorreta.")
            return False
    

    # --- Reset de senha ---
    def reset_password(self, username: str, new_password: str, recovery_key: str):
        if recovery_key != self.MASTER_KEY:
            print("Chave mestra errada!")
            return False
        
        # Cria uma hash nova para nova senha
        new_hash = self.hash_password(new_password)
        return self.db.update_user_password(username, new_password)
    

    def has_users(self) -> bool:
        return self.db.user_exists()