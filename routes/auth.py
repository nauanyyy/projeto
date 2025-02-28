from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from models.user import User 
    from app import mysql 
    
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        if not email or not senha:
            flash("Preencha todos os campos!", "danger")
            return redirect(url_for("auth.login"))

        user = User.find_by_email(email, mysql)

        if user and user.check_password(senha):
            login_user(user)
            return redirect(url_for("home.home")) 

        flash("E-mail ou senha incorretos!", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "success") 
    return redirect(url_for('auth.login'))

@auth_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    from models.user import User 
    from app import mysql 
    
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        tipo = request.form.get("tipo", "usuario")  

        if not nome or not email or not senha:
            flash("Todos os campos são obrigatórios!", "danger")
            return redirect(url_for("auth.registrar")) 

        if User.find_by_email(email, mysql):
            flash("Este e-mail já está cadastrado!", "danger")
            return redirect(url_for("auth.registrar"))

        User.create(nome, email, senha, tipo, mysql)
        flash("Conta criada com sucesso!", "success")
        return redirect(url_for("auth.login"))

    return render_template("registrar.html")