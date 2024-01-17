from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost:3306/esimanal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50), nullable=False)
    user = db.relationship('User', backref='Role', lazy=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion
        }

class CatCategoria(db.Model):
    __tablename__ = 'cat_categorias'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50), nullable=False)
    noticia = db.relationship('Noticias', backref='categorias', lazy=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion
        }
    
class imgSubmissions(db.Model):
    __tablename__ = 'img_submissions'
    id = db.Column(db.Integer, primary_key=True)
    ruta = db.Column(db.String(255), nullable=False)
    noticia = db.relationship('Noticias', backref='imagenes', lazy=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'ruta': self.ruta
        }
    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    contacto = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(50), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='usuarios_role', lazy=True)
    noticia = db.relationship('Noticias', backref='usuarios', lazy=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'contacto': self.contacto,
            'titulo': self.titulo,
            'role_id': self.role_id,
            'role': {
                'id': self.role.id,
                'descripcion': self.role.descripcion
            }
        }
    

class Noticias(db.Model):
    __tablename__ = 'noticias'
    id = db.Column(db.Integer, primary_key = True)
    titulo = db.Column(db.String(50), nullable = False)
    contenido = db.Column(db.String(255), nullable = False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('cat_categorias.id'))
    categoria = db.relationship('CatCategoria', backref='categoria', lazy=True)
    img_id = db.Column(db.Integer, db.ForeignKey('img_submissions.id'))
    img = db.relationship('imgSubmissions', backref='img', lazy=True)
    autor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    autor = db.relationship('User', backref='noticias_autor', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable = False)
    
    def serialize(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'contenido': self.contenido,
            'categoria_id': self.categoria_id,
            'img_id': self.img_id,
            'autor_id': self.autor_id,
            'created_at': self.created_at,
            'categoria': {
                'id': self.categoria.id,
                'descripcion': self.categoria.descripcion
            },
            'autor': {
                'id': self.autor.id,
                'nombre': self.autor.nombre,
                'contacto': self.autor.contacto,
                'titulo': self.autor.titulo,
                'role_id': self.autor.role_id,
                'role': {
                    'id': self.autor.role.id,
                    'descripcion': self.autor.role.descripcion
                }
            },
        }
        
with app.app_context():
    db.create_all()

@app.route('/post-news',  methods=['GET', 'POST'])
def postNews():
    try:
        data = request.get_json()
        
        nueva_noticia = Noticias(
            titulo = data['titulo'],
            contenido = data['contenido'],
            categoria_id = 1,
            img_id = None,
            autor_id = 1,
            created_at = datetime.utcnow()
        )
        
        db.session.add(nueva_noticia)
        db.session.commit()
        
        return data
    except Exception as e:
        return jsonify({"message": f"Error de conexión: {str(e)}"})
        
@app.route('/get-news', methods=['GET'])
def getNews():
    try:
        users = Noticias.query.options(db.joinedload(Noticias.autor)).all()
        
        return jsonify([user.serialize() for user in users])
    except Exception as e:
        return jsonify({"message": f"Error de conexión: {str(e)}"})