from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, id, nome, email, senha, tipo):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo = tipo

    @staticmethod
    def create(nome, email, senha, tipo='usuario', mysql=None):
        if mysql is None:
            raise ValueError("É necessário passar a instância do MySQL.")
            
        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO users (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)",
            (nome, email, senha_hash, tipo)
        )
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def find_by_email(email, mysql=None):
        if mysql is None:
            raise ValueError("É necessário passar a instância do MySQL.")
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return User(*user)
        return None

    def check_password(self, senha):
        return bcrypt.check_password_hash(self.senha, senha)
