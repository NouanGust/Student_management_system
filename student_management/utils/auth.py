import bcrypt
from typing import Optional
from database.db_manager import DatabaseManager

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def hash_password(self, password: str) -> str:
        """Gera hash da senha"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica se a senha está correta"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def register_user(self, username: str, password: str) -> bool:
        """Registra um novo usuário"""
        password_hash = self.hash_password(password)
        return self.db.create_user(username, password_hash)
    
    def login(self, username: str, password: str) -> bool:
        """Autentica um usuário"""
        user = self.db.get_user(username)
        if user:
            return self.verify_password(password, user['password_hash'])
        return False
    
    def has_users(self) -> bool:
        """Verifica se existe algum usuário cadastrado"""
        return self.db.user_exists()