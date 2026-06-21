# backend/app.py
import threading
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import JWT_SECRET_KEY, JWT_EXPIRATION, MAX_UPLOAD_SIZE
from core.database import init_db
from network.pubsub import pubsub_listener
from routes.auth import auth_bp
from routes.vault import vault_bp

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_EXPIRATION
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE

jwt = JWTManager(app)

# Registrar Módulos
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(vault_bp, url_prefix="/api/network")

if __name__ == "__main__":
    init_db()
    
    # Iniciar el Centinela en segundo plano
    threading.Thread(target=pubsub_listener, daemon=True).start()
    
    app.run(host="127.0.0.1", port=5000, debug=False)