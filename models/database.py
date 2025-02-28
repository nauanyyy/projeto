import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import mysql, app

def criar_tabelas():
    with app.app_context():
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            tipo ENUM('admin', 'usuario') NOT NULL DEFAULT 'usuario'
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS animais (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            especie VARCHAR(255) NOT NULL,
            raca VARCHAR(255) NOT NULL,
            idade INT NOT NULL,
            unidade_idade ENUM('anos', 'meses') NOT NULL DEFAULT 'anos',  -- Nova coluna
            descricao TEXT NOT NULL,
            status ENUM('disponivel', 'adotado') NOT NULL DEFAULT 'disponivel',
            localizacao VARCHAR(255) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS adocoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            animal_id INT NOT NULL,
            status ENUM('pendente', 'aprovado', 'rejeitado') NOT NULL DEFAULT 'pendente',
            mensagem TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (animal_id) REFERENCES animais(id) ON DELETE CASCADE
        );
        """)

        mysql.connection.commit()
        cursor.close()
        print("Tabelas criadas com sucesso!")

def adicionar_admin():
    with app.app_context():
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM users WHERE tipo = 'admin'")
        admin = cursor.fetchone()

        if not admin:
            from models.user import User  
            User.create("Administrador", "nauany@gmail.com", "admin123", "admin", mysql)
            print("Administrador criado com sucesso!")
        else:
            print("Já existe um administrador cadastrado.")

        cursor.close()

if __name__ == "__main__":
    criar_tabelas()
    adicionar_admin() 
