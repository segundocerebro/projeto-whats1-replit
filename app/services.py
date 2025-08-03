# app/services.py
import logging
from app.clients import openai_client

logger = logging.getLogger(__name__)

def handle_new_message(payload: dict):
    waid = payload.get("WaId")
    from_user = payload.get("From")
    to_bot = payload.get("To")
    user_input = payload.get("MediaUrl0") or payload.get("Body") or ""
    session_id = f"wa:{waid}" if waid else None

    if not all([session_id, from_user, to_bot, user_input]):
        logger.error(f"[HANDLE] Payload inválido, abortando: {payload}")
        return

    logger.info(f"[HANDLE] Iniciando para sessão={session_id}")
    openai_client.orchestrate_assistant_response(session_id, user_input, from_user, to_bot)
    logger.info(f"[HANDLE] Finalizado para sessão={session_id}")