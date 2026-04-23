import os
import shutil
import time
from flask import Blueprint, request, jsonify, current_app
from app.services.auth import token_required
from werkzeug.utils import secure_filename
from app.utils.validators import validar_cedula_ecuatoriana
from app.services.mail_service import send_email_client, send_email_company
from app.services.whatsapp_service import notify_company
from app.loggers import app_logger

# Blueprint para rutas de contacto
contacto_bp = Blueprint("contacto", __name__)


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@contacto_bp.route("/contratar", methods=["POST"])
@token_required
def contratar(token):

    # ======= VALIDACIÓN CAMPOS BASE =======
    required_fields = [
        "servicio", "tipoPersona", "vigencia", "precio",
        "tipoIdentificacion", "identificacion", "nombres",
        "correo", "celular"
    ]
    for field in required_fields:
        if not request.form.get(field):
            app_logger.warning({"event": "missing_field", "campo": field, "ip": request.remote_addr})
            return jsonify({"error": f"Campo requerido: {field}"}), 400
        
    # Validar cédula ecuatoriana
    identificacion = request.form.get("identificacion")
    # Validar cedula solo numérica
    if not identificacion.isdigit():
        app_logger.warning({"event": "invalid_identificacion", "identificacion": identificacion, "ip": request.remote_addr})
        return jsonify({"error": "Identificación inválida"}), 400
    if request.form.get("tipoIdentificacion") == "Cédula":
        if not validar_cedula_ecuatoriana(identificacion):
            app_logger.warning({"event": "invalid_identificacion", "identificacion": identificacion, "ip": request.remote_addr})
            return jsonify({"error": "Identificación inválida"}), 400

    # ======= VALIDAR IMÁGENES OBLIGATORIAS =======
    image_fields = [
        "imgCedulaFront",
        "imgCedulaBack",
        "imgSelfie"
    ]
    
    formatos_imagenes = current_app.config["ALLOWED_IMAGES"]
    formatos_pdf = current_app.config["ALLOWED_PDF"]
    
    for field in image_fields:
        file = request.files.get(field)
        # Validar que el archivo exista
        if not file:
            app_logger.warning({"event": "missing_file", "campo": field, "ip": request.remote_addr})
            return jsonify({"error": f"Archivo requerido: {field}"}), 400
        # Validar extensión del archivo (permitir solo imagenes)
        if not allowed_file(file.filename, formatos_imagenes):
            app_logger.warning({"event": "invalid_extension", "campo": field, "ip": request.remote_addr})
            return jsonify({"error": f"Extensión inválida en {field}"}), 400
        # Validar tamaño del archivo (máximo 10MB)
        if file.content_length > current_app.config["MAX_CONTENT_LENGTH_IMAGE"]:
            app_logger.warning({"event": "file_too_large", "campo": field, "ip": request.remote_addr})
            return jsonify({"error": f"Archivo demasiado grande en {field} (máximo 5MB)"}), 400

        
    # ======= VALIDACIONES SEGÚN TIPO =======
    tipo_servicio = request.form.get("tipoPersona")
    extra_files = ["fileRuc", "fileConstitucion", "fileNombramiento"]
    # Validar campos adicionales según tipo de servicio
    if tipo_servicio == "Persona RUC":
        file_ruc = request.files.get("fileRuc")
        # Validar que el archivo exista y sea PDF
        if not file_ruc or not allowed_file(file_ruc.filename, formatos_pdf):
            app_logger.warning({"event": "missing_file", "campo": "fileRuc", "ip": request.remote_addr})
            return jsonify({"error": "RUC (PDF) obligatorio"}), 400
        # Validar tamaño del archivo (máximo 10MB)
        if file_ruc.content_length > current_app.config["MAX_CONTENT_LENGTH_FILE"]:
            app_logger.warning({"event": "file_too_large", "campo": "fileRuc", "ip": request.remote_addr})
            return jsonify({"error": "Archivo demasiado grande en RUC (máximo 10MB)"}), 400
        
    elif tipo_servicio == "Persona Juridica":

        for field in extra_files:
            file = request.files.get(field)
            # Validar que el archivo exista y sea PDF
            if not file or not allowed_file(file.filename, formatos_pdf):
                app_logger.warning({"event": "missing_file", "campo": field, "ip": request.remote_addr})
                return jsonify({"error": f"{field} (PDF) obligatorio"}), 400
            # Validar tamaño del archivo (máximo 10MB)
            if file.content_length > current_app.config["MAX_CONTENT_LENGTH_FILE"]:
                app_logger.warning({"event": "file_too_large", "campo": field, "ip": request.remote_addr})
                return jsonify({"error": f"Archivo demasiado grande en {field} (máximo 10MB)"}), 400
    
    # ====== VALIDACIÓN ARCHIVO COMPROBANTE =======
    comprobante = request.files.get("comprobantePago")
    if not comprobante:
        app_logger.warning({"event": "missing_file", "campo": "comprobantePago", "ip": request.remote_addr})
        return jsonify({"error": "Archivo requerido: comprobantePago"}), 400
    if allowed_file(comprobante.filename, formatos_pdf.union(formatos_imagenes)):
        formatofile = comprobante.filename.split(".")[-1]
        if formatofile in formatos_pdf:
            if comprobante.content_length > current_app.config["MAX_CONTENT_LENGTH_FILE"]:
                app_logger.warning({"event": "file_too_large", "campo": "comprobantePago", "ip": request.remote_addr})
                return jsonify({"error": "Archivo demasiado grande en comprobantePago (máximo 10MB)"}), 400
        else:            
            if comprobante.content_length > current_app.config["MAX_CONTENT_LENGTH_IMAGE"]:
                app_logger.warning({"event": "file_too_large", "campo": "comprobantePago", "ip": request.remote_addr})
                return jsonify({"error": "Archivo demasiado grande en comprobantePago (máximo 5MB)"}), 400
    else:
        app_logger.warning({"event": "invalid_extension", "campo": "comprobantePago", "ip": request.remote_addr})
        return jsonify({"error": "Extensión inválida en comprobantePago"}), 400
                
    # ======= GUARDAR ARCHIVOS TEMPORALMENTE =======
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    # Crear carpeta temporal única por solicitud usando un identificador único como la cédula y hora y fecha de la solicitud
    request_folder = os.path.join(upload_folder, f"temp_{identificacion}_{str(int(round(time.time())))}")
    os.makedirs(request_folder, exist_ok=True)

    # Lista para almacenar rutas de archivos guardados
    archivos_guardados = {}
    
    try:
        # ===== ARCHIVOS =====
        for file_key in request.files:
            file = request.files[file_key]
            # Obtener nombre seguro del archivo mas un identificador único para evitar colisiones
            filename = secure_filename(file.filename)
            filename = f"{file_key}_{filename}" 
            file_path = os.path.join(request_folder, filename)
            file.save(file_path)

            archivos_guardados.update({file_key: [file_path, file.mimetype]})
        app_logger.info({"event": "files_saved", "archivos": list(archivos_guardados.keys()), "ip": request.remote_addr})
        # ===== PROCESAMIENTO DE ENVIO DE CORREO =====
        datos = {
            "servicio": request.form.get("servicio"),
            "tipoPersona": request.form.get("tipoPersona"),
            "vigencia": request.form.get("vigencia"),
            "precio": request.form.get("precio"),
            "tipoIdentificacion": request.form.get("tipoIdentificacion"),
            "nombres": request.form.get("nombres"),
            "identificacion": request.form.get("identificacion"),
            "celular": request.form.get("celular"),
            "correo": request.form.get("correo"),
        }
        
        # Enviar correo al cliente
        send_email_client(
            subject=f"Solicitud de {datos['servicio']} - {datos['nombres']}",
            data=datos,
            recipient=datos["correo"]
        )
        
        # Enviar correo a la empresa con los datos de la solicitud y archivos adjuntos
        send_email_company(datos, archivos_guardados)
        
        app_logger.info({"event": "solicitud_processed", "datos": datos, "archivos_guardados": len(archivos_guardados), "ip": request.remote_addr})
        return jsonify({"mensaje": "Solicitud procesada correctamente", "archivos_guardados": len(archivos_guardados), "archivos": archivos_guardados}), 200

    except Exception as e:
        app_logger.error({"event": "error_processing_solicitud", "error": str(e), "ip": request.remote_addr})
        return jsonify({"error": str(e)}), 500

    finally:
        # ======= ELIMINACIÓN AUTOMÁTICA DE ARCHIVOS TEMPORALES =======
        if os.path.exists(request_folder):
            shutil.rmtree(request_folder)
            app_logger.info({"event": "temp_folder_deleted", "folder": request_folder})
            
            
@contacto_bp.route("/test", methods=["GET"])
def test():
    app_logger.info({"event": "test_endpoint_called", "ip": request.remote_addr})
    return jsonify({"message": "Test endpoint working!"}), 200