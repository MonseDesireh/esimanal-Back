from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_PORT"] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'esimanal'

mysql = MySQL(app)

@app.route('/post-news',  methods=['GET', 'POST'])
def postNews():
    try:
        data = request.get_json()
        cursor = mysql.connection.cursor()
        cursor.execute(f"""
                        INSERT INTO noticias (titulo, contenido, created_at, categoria_id, img_id, autor_id)
                        VALUES ('{data['titulo']}', '{data['contenido']}', '2024-01-01 00:00:00', 1, null, 1)
                        """)
        
        mysql.connection.commit()
        
        return data
    except Exception as e:
        return jsonify({"message": f"Error de conexión: {str(e)}"})

    finally:
        cursor.close()
        
@app.route('/get-news', methods=['GET'])
def getNews():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f"""
                    SELECT 
                            n.id as id,
                            n.titulo as titulo,
                            n.contenido as contenido,
                            n.created_at as creacion,
                            u.nombre as nombre_autor,
                            u.contacto as contacto,
                            u.titulo as titulo_autor,
                            descripcion as categoria
                        FROM 
                            noticias as n
                        join users as u on u.id = n.autor_id 
                        join cat_categorias as cc on cc.id = n.categoria_id;
                    """)
        response = cursor.fetchone()
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"message": f"Error de conexión: {str(e)}"})

    finally:
        cursor.close()