# app/routes.py
import logging
from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from app import EXECUTOR
from app.services import handle_new_message

logger = logging.getLogger(__name__)
whatsapp_bp = Blueprint("whatsapp_bp", __name__)

@whatsapp_bp.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming = request.values.to_dict()
    logger.info(f"[WEBHOOK] SID={incoming.get('MessageSid')}, De={incoming.get('From')}, WaId={incoming.get('WaId')}")
    
    EXECUTOR.submit(handle_new_message, incoming)

    # ACK TEMPORÁRIO DE DEBUG (removeremos na v1.1)
    resp = MessagingResponse()
    resp.message("Recebi. Processando...")
    return str(resp)

@whatsapp_bp.route("/webhook/status", methods=["POST"])
def twilio_status():
    """Recebe e loga o status final de entrega da mensagem (telemetria)."""
    data = request.form.to_dict()
    logger.info(
        f"[STATUS DE ENTREGA] SID={data.get('MessageSid')}, "
        f"Status={data.get('MessageStatus')}, "
        f"Erro={data.get('ErrorCode')}"
    )
    return ("", 204)