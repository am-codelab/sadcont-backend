from flask import request, jsonify, current_app
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener el token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Extrae el token después de "Bearer"
            except IndexError:
                return jsonify({'mensaje': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'mensaje': 'Token faltante'}), 401
        
        # Validar el token
        if token not in current_app.config["SECRET_KEY"]:
            return jsonify({'mensaje': 'Token no autorizado'}), 401
        
        return f(token, *args, **kwargs)
    
    return decorated