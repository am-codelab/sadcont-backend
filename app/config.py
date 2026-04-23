import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Clave secreta para la aplicación Flask
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Variables de valores máximos para la carga de archivos
    MAX_CONTENT_LENGTH_FILE = 9 * 1024 * 1024  # 10MB límite para documentos PDF
    MAX_CONTENT_LENGTH_IMAGE = 5 * 1024 * 1024  # 5MB límite para imagenes
    UPLOAD_FOLDER = "uploads"
    ALLOWED_IMAGES = {"jpg", "jpeg", "png"}
    ALLOWED_PDF = {"pdf"}
    
    # Configuración de correo electrónico
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    COMPANY_NAME = os.getenv("COMPANY_NAME", "SAD&CONT")  # Valor por defecto si no está en .env
    # Nombre de la empresa para los correos electrónicos
    
    # Configuración de WhatsApp Business API
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_BUSINESS_NUMBER = os.getenv("WHATSAPP_BUSINESS_NUMBER")
    
    # URL del logo para los correos electrónicos
    LOGO_URL = "cid:logo"
    LOGO_PATH = "source/imgs/logo.jpg"
