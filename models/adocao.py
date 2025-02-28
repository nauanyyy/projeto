from models.database import db

class Adocao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    status = db.Column(db.String(20), default="Pendente") 

    usuario = db.relationship('User', backref='adocoes')
    animal = db.relationship('Animal', backref='adocoes')
