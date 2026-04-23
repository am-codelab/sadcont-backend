import requests
from flask import current_app
from app.loggers import whatsapp_logger

def build_summary(data):
    return f"""
📌 NUEVA SOLICITUD
DATOS DEL CLIENTE:
👤 Nombre: {data['nombres']}
🆔 {data['tipoIdentificacion']}: {data['identificacion']}
📞 Teléfono: {data['celular']}
📧 Correo: {data['correo']}

DATOS DEL SERVICIO:
🛠 Servicio: {data['servicio']}
📌 Tipo: {data['tipoPersona']}
📌 Vigencia: {data['vigencia']}
📌 Precio: {data['precio']}
"""

def notify_company(data, files):
    # Arreglo para almacenar los IDs de los archivos subidos a WhatsApp, para eliminarlos después
    ids_archivos = []
    try:
        send_text(build_summary(data))
        # Cargar y enviar archivos a WhatsApp
        for key, file in files.items():
            media_id = upload_media(key, file[0], file[1])
            ids_archivos.append(media_id)
            # Identificar tipo de archivo para enviarlo correctamente (documento o imagen)
            if file[1] == "application/pdf":
                send_document(media_id, key+".pdf")
            else:
                send_image(media_id)
        # Eliminar archivos de WhatsApp después de enviarlos
        for media_id in ids_archivos:
            delete_media(media_id)
    except Exception as e:
        whatsapp_logger.error(f"Error en notificación WhatsApp: {str(e)}", exc_info=True)
        return {"status": "notification_error", "error": str(e)}
    
    return {"status": "ok"}

def send_text(message):
    token = current_app.config["WHATSAPP_TOKEN"]
    phone_number_id = current_app.config["WHATSAPP_PHONE_NUMBER_ID"]
    numero_empresa = current_app.config["WHATSAPP_BUSINESS_NUMBER"]
    
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": numero_empresa,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def upload_media(fileName, fileUrl, fileType):
    try:
        token = current_app.config["WHATSAPP_TOKEN"]
        phone_number_id = current_app.config["WHATSAPP_PHONE_NUMBER_ID"]
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/media"

        headers = {
            "Authorization": f"Bearer {token}"
        }
        data = {
            "messaging_product": "whatsapp"
        }
        files = {
            "file": (fileName, open(fileUrl, "rb"), fileType)
        }
        # Enviar la solicitud POST
        response = requests.post(url, headers=headers, data=data, files=files)
        # Guardar datos relevantes en el logger de WhatsApp
        whatsapp_logger.info({"event" : "upload_media", "file": fileName, "id_media": response.json()["id"], "status_code": response.status_code, "response": response.json()})
        
        return response.json()["id"]
    except Exception as e: 
        whatsapp_logger.error(f"Error subiendo media a WhatsApp: {str(e)}", exc_info=True)
        raise e

def send_document(media_id, filename):
    try:
        token = current_app.config["WHATSAPP_TOKEN"]
        phone_number_id = current_app.config["WHATSAPP_PHONE_NUMBER_ID"]
        numero_empresa = current_app.config["WHATSAPP_BUSINESS_NUMBER"]
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": numero_empresa,
            "type": "document",
            "document": {
                "id": media_id,
                "filename": filename
            }
        }
        # Enviar la solicitud POST
        response = requests.post(url, headers=headers, json=payload)
        # Guardar datos relevantes en el logger de WhatsApp
        whatsapp_logger.info({"event": "send_document", "media_id": media_id, "filename": filename, "status_code": response.status_code, "response": response.json()})
    except Exception as e:
        whatsapp_logger.error(f"Error enviando documento a WhatsApp: {str(e)}", exc_info=True)
        raise e
    
    
def send_image(media_id):
    try:
        token = current_app.config["WHATSAPP_TOKEN"]
        phone_number_id = current_app.config["WHATSAPP_PHONE_NUMBER_ID"]
        numero_empresa = current_app.config["WHATSAPP_BUSINESS_NUMBER"]
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": numero_empresa,
            "type": "image",
            "image": {
                "id": media_id
            }
        }
        # Enviar la solicitud POST
        response = requests.post(url, headers=headers, json=payload)
        # Guardar datos relevantes en el logger de WhatsApp
        whatsapp_logger.info({"event": "send_image", "media_id": media_id, "status_code": response.status_code, "response": response.json()})
    except Exception as e:
        whatsapp_logger.error(f"Error enviando imagen a WhatsApp: {str(e)}", exc_info=True)
        raise e
    

def delete_media(id):
    try:
        token = current_app.config["WHATSAPP_TOKEN"]
        
        url = f"https://graph.facebook.com/v18.0/{id}"

        headers = {
            "Authorization": f"Bearer {token}"
        }
        # Enviar la solicitud DELETE
        response = requests.delete(url, headers=headers)
        # Guardar datos relevantes en el logger de WhatsApp
        whatsapp_logger.info({"event": "delete_media", "id": id, "status_code": response.status_code})
    except Exception as e:
        whatsapp_logger.error(f"Error eliminando archivo de WhatsApp: {str(e)}", exc_info=True)
        raise e