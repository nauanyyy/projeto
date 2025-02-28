from flask import Flask, redirect, url_for
from flask_mysqldb import MySQL
from flask_login import LoginManager
from config import Config
from routes.auth import auth_bp 
from routes.home import home_bp 


app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app) 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login" 

@login_manager.user_loader
def load_user(user_id):
    from models.user import User 
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(*user)
    return None

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(home_bp, url_prefix="/home") 

@app.route('/')
def index():
    return redirect(url_for('auth.login')) 


if __name__ == "__main__":
    app.run(debug=True)
