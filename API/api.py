from flask import Flask
from crud import crud_blueprint

app = Flask(__name__)

# Registra il Blueprint delle API CRUD
app.register_blueprint(crud_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
