import os
import sqlite3

current_dir_path = os.getcwd()
db_name = "Database.db"

if not os.path.exists(os.path.join(current_dir_path, db_name)):
    with open(os.path.join(current_dir_path, db_name), "w") as file:
        pass

connection = sqlite3.connect(db_name)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password TEXT
)
""")

cursor.close()
connection.close()