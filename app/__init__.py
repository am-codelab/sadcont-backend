from flask import Flask
from flask_cors import CORS
from .routes.contacto import contacto_bp
from .routes.webhook import webhook_bp
from .config import Config
from .mail import mail_service
from .loggers import app_logger, email_logger, whatsapp_logger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Configuración de rutas de la API
    CORS(app)
    app.register_blueprint(contacto_bp, url_prefix="/api")
    app.register_blueprint(webhook_bp)
    # Inicialización de servicios como Flask-Mail
    mail_service.init_app(app)
    
    return app