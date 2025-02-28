from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
@login_required
def home():
    from app import mysql
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT id, nome, especie, raca, idade, unidade_idade, descricao, localizacao, status FROM animais WHERE status = 'disponivel'")
    animais = cursor.fetchall()
    cursor.close()

    return render_template("home.html", animais=animais)

@home_bp.route("/cadastrar-animal", methods=["GET", "POST"])
@login_required
def cadastrar_animal():
    if current_user.tipo != 'admin':
        return redirect(url_for('home.home'))  

    if request.method == "POST":
        nome = request.form.get("nome")
        especie = request.form.get("especie")
        raca = request.form.get("raca")
        idade = request.form.get("idade")
        unidade_idade = request.form.get("unidade_idade") 
        descricao = request.form.get("descricao")
        localizacao = request.form.get("localizacao")
        status = request.form.get("status")

        if not all([nome, especie, raca, idade, unidade_idade, descricao, localizacao, status]):
            flash("Todos os campos são obrigatórios!", "danger")
            return render_template("cadastrar_animal.html")

        try:
            idade = int(idade)
            from app import mysql
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO animais (nome, especie, raca, idade, unidade_idade, descricao, localizacao, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, especie, raca, idade, unidade_idade, descricao, localizacao, status)) 
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for("home.home"))

        except Exception as e:
            flash("Erro ao cadastrar animal: {}".format(str(e)), "danger")

    return render_template("cadastrar_animal.html")

@home_bp.route("/animais-cadastrados")
@login_required
def animais_cadastrados():
    if current_user.tipo != 'admin':
        return redirect(url_for('home.home'))  
    
    from app import mysql
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT * FROM animais") 
    animais = cursor.fetchall()
    cursor.close()

    return render_template("animais_cadastrados.html", animais=animais)

@home_bp.route("/editar-animal/<int:id>", methods=["GET", "POST"])
@login_required
def editar_animal(id):
    if current_user.tipo != 'admin':
        return redirect(url_for('home.home'))  

    from app import mysql
    cursor = mysql.connection.cursor()

    if request.method == "POST":
        nome = request.form.get("nome")
        especie = request.form.get("especie")
        raca = request.form.get("raca")
        idade = request.form.get("idade")
        unidade_idade = request.form.get("unidade_idade")
        descricao = request.form.get("descricao")
        localizacao = request.form.get("localizacao")
        status = request.form.get("status")

        if not all([nome, especie, raca, idade, unidade_idade, descricao, localizacao, status]):
            flash("Todos os campos são obrigatórios!", "danger")
        else:
            try:
                idade = int(idade)
                cursor.execute("""
                    UPDATE animais SET nome=%s, especie=%s, raca=%s, idade=%s, unidade_idade=%s, descricao=%s,  localizacao=%s, status=%s
                    WHERE id=%s
                """, (nome, especie, raca, idade, unidade_idade, descricao, localizacao, status, id))
                mysql.connection.commit()
                return redirect(url_for("home.home"))
            except Exception as e:
                flash("Erro ao editar animal: {}".format(str(e)), "danger")

    cursor.execute("SELECT id, nome, especie, raca, idade, unidade_idade, descricao, localizacao, status FROM animais WHERE id = %s", (id,))
    animal = cursor.fetchone()
    cursor.close()

    print(animal)

    return render_template("editar_animal.html", animal=animal)

@home_bp.route("/solicitar-adocao/<int:animal_id>", methods=["GET", "POST"])
@login_required
def solicitar_adocao(animal_id):
    from app import mysql

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT * FROM adocoes 
        WHERE usuario_id = %s AND animal_id = %s AND status = 'pendente'
    """, (current_user.id, animal_id))
    existing_request = cursor.fetchone()

    if existing_request:
        flash("Você já possui uma solicitação pendente para este animal! Por favor, aguarde a análise.", "warning")
        cursor.close() 
        return redirect(url_for("home.home"))

    if request.method == "POST":
        usuario_id = current_user.id

        try:
            cursor.execute(
                "INSERT INTO adocoes (usuario_id, animal_id, status, mensagem) VALUES (%s, %s, 'pendente', 'Pendente')",
                (usuario_id, animal_id),
            )
            mysql.connection.commit()
            flash("Sua solicitação foi enviada para análise!", "success")
            return redirect(url_for("home.home"))

        except Exception:
            flash("Erro ao solicitar adoção!", "danger")

    cursor.execute("SELECT * FROM animais WHERE id = %s", (animal_id,))
    animal = cursor.fetchone()
    cursor.close()

    return render_template("solicitar_adocao.html", animal=animal)

@home_bp.route("/solicitacoes-adocao")
@login_required
def solicitacoes_adocao():
    if current_user.tipo != "admin":
        return redirect(url_for("home.home"))  

    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT adocoes.id, users.nome AS usuario_nome, users.email, 
               animais.nome AS animal_nome, animais.especie, animais.raca, 
               animais.localizacao, adocoes.status, animais.id AS animal_id
        FROM adocoes
        JOIN users ON adocoes.usuario_id = users.id
        JOIN animais ON adocoes.animal_id = animais.id
        WHERE adocoes.status = 'pendente'
    """)
    
    solicitacoes = cursor.fetchall()
    cursor.close()

    return render_template("solicitacoes_adocao.html", solicitacoes=solicitacoes)

@home_bp.route("/confirmar-adocao/<int:solicitacao_id>/<int:animal_id>", methods=["POST"])
@login_required
def confirmar_adocao(solicitacao_id, animal_id):
    if current_user.tipo != "admin":
        return redirect(url_for("home.home"))  

    from app import mysql
    cursor = mysql.connection.cursor()

    try:
        mensagem = "Parabéns! Sua solicitação de adoção foi aprovada. Que seu pet traga muita alegria para o seu lar!"
        cursor.execute("UPDATE adocoes SET status = 'Aprovado', mensagem = %s WHERE id = %s", (mensagem, solicitacao_id))
        cursor.execute("UPDATE animais SET status = 'Adotado' WHERE id = %s", (animal_id,))
        mysql.connection.commit()
        flash("Adoção aprovada com sucesso!", "success")
    except Exception:
        flash("Erro ao aprovar adoção!", "danger")

    cursor.close()
    return redirect(url_for("home.solicitacoes_adocao"))

@home_bp.route("/recusar-adocao/<int:solicitacao_id>", methods=["POST"])
@login_required
def recusar_adocao(solicitacao_id):
    if current_user.tipo != "admin":
        return redirect(url_for("home.home"))  

    from app import mysql
    cursor = mysql.connection.cursor()

    try:
        mensagem = "Infelizmente, sua solicitação de adoção foi recusada. Não desista, há muitos outros animaizinhos esperando por um lar!"
        cursor.execute("UPDATE adocoes SET status = 'Rejeitado', mensagem = %s WHERE id = %s", (mensagem, solicitacao_id))
        mysql.connection.commit()
        flash("Adoção rejeitada com sucesso!", "warning")
    except Exception:
        flash("Erro ao rejeitar adoção!", "danger")

    cursor.close()
    return redirect(url_for("home.solicitacoes_adocao"))

@home_bp.route("/minhas-solicitacoes")
@login_required
def minhas_solicitacoes():
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT adocoes.status, adocoes.mensagem, animais.nome 
        FROM adocoes
        JOIN animais ON adocoes.animal_id = animais.id
        WHERE adocoes.usuario_id = %s
    """, (current_user.id,))
    
    solicitacoes = cursor.fetchall()
    cursor.close()

    return render_template("minhas_solicitacoes.html", solicitacoes=solicitacoes)