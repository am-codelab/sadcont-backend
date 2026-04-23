from app.utils.logger import setup_logger

# Configuración de loggers
app_logger = setup_logger("app_logger", "logs/app.log")
whatsapp_logger = setup_logger("whatsapp_logger", "logs/whatsapp.log")
email_logger = setup_logger("email_logger", "logs/email.log")