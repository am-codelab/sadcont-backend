from flask import Blueprint, request, jsonify, current_app
import os

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Verificación inicial (Meta prueba tu endpoint)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == current_app.config["SECRET_KEY"]:
            return challenge, 200
        else:
            return "Verification failed", 403

    # Recepción de eventos
    if request.method == "POST":
        data = request.json
        print("Webhook recibido:", data)
        return jsonify({"status": "ok"}), 200