import os
import sqlite3
import json
from flask import Blueprint, request, jsonify

crud_blueprint = Blueprint("crud", __name__)

# Configurazione database
current_dir_path = os.getcwd()
db_name = "Database.db"
db_path = os.path.join(current_dir_path, db_name)

# Creazione file DB se non esiste
if not os.path.exists(db_path):
    open(db_path, "w").close()

# Creazione tabella se non esiste
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)
    conn.commit()

# Funzione per connessione al DB
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Rotta Home
@crud_blueprint.route("/")
def home():
    return "API CRUD Flask con SQLite"

# CREATE
@crud_blueprint.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Tutti i campi sono obbligatori"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, password)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Utente creato con successo"}), 201

# READ (tutti)
@crud_blueprint.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    #Usa un template HTML e passa i dati dove serve per visualizzare l'html
    return f"<p>{users[0]['email']}</p>"

    #jsonify ritorna un oggetto di tipo Responce
    # return jsonify([dict(row) for row in users])

# READ (singolo)
@crud_blueprint.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if user is None:
        return jsonify({"error": "Utente non trovato"}), 404   
    
    return jsonify(dict(user))

# UPDATE
@crud_blueprint.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET username = ?, email = ?, password = ?
        WHERE id = ?
    """, (username, email, password, user_id))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Utente non trovato"}), 404

    return jsonify({"message": "Utente aggiornato con successo"})

# DELETE
@crud_blueprint.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Utente non trovato"}), 404

    return jsonify({"message": "Utente eliminato con successo"})
