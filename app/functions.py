# app/functions.py
import logging, os, requests, json
from app.clients import twilio_client as tc
from app.clients import elevenlabs_client as ec
from app.utils.wa import normalize_wa

logger = logging.getLogger(__name__)

def transcribe_audio(media_url: str):
    logger.info(f"FUNCTION: Transcrevendo áudio de {media_url}")
    wav_path = tc.download_and_prepare_audio(media_url)
    if not wav_path: return "Falha ao baixar o áudio."
    return tc.transcrever_audio_com_whisper(wav_path)

def tts_generate_and_store(text: str):
    logger.info(f"FUNCTION: Gerando áudio: '{text[:30]}...'")
    return ec.gerar_audio_e_salvar(text)

def rag_query(session_id: str, query: str):
    logger.info(f"FUNCTION: Consultando RAG para sessão {session_id}")
    # Retorna contexto biográfico básico do Endrigo
    return "Endrigo Almada é um empresário brasileiro, especialista em marketing digital e vendas online. Trabalha com negócios digitais há mais de 10 anos e é conhecido por suas estratégias inovadoras."

def send_whatsapp_message(to: str, body: str):
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")
    logger.info(f"FUNCTION: Enviando texto para {to}")
    try:
        bot_num = normalize_wa(from_number)
        user_num = normalize_wa(to)
        msg = tc.twilio_client.messages.create(to=user_num, from_=bot_num, body=body)
        return json.dumps({"status": "sucesso", "sid": msg.sid})
    except Exception as e:
        logger.error(f"Falha ao enviar texto via função: {e}")
        return json.dumps({"status": "erro", "detalhe": str(e)})

def send_whatsapp_media(to: str, media_url: str):
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")
    logger.info(f"FUNCTION: Enviando mídia para {to}")
    try:
        bot_num = normalize_wa(from_number)
        user_num = normalize_wa(to)
        msg = tc.twilio_client.messages.create(to=user_num, from_=bot_num, media_url=[media_url])
        return json.dumps({"status": "sucesso", "sid": msg.sid})
    except Exception as e:
        logger.error(f"Falha ao enviar mídia via função: {e}")
        return json.dumps({"status": "erro", "detalhe": str(e)})

def probe_media_url(url: str):
    logger.info(f"FUNCTION: Verificando URL: {url}")
    try:
        r = requests.head(url, allow_redirects=True, timeout=5)
        return json.dumps({ "ok": r.status_code == 200, "status": r.status_code })
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)})

AVAILABLE_FUNCTIONS = {
    "transcribe_audio": transcribe_audio, "rag_query": rag_query,
    "tts_generate_and_store": tts_generate_and_store, "probe_media_url": probe_media_url,
    "send_whatsapp_message": send_whatsapp_message, "send_whatsapp_media": send_whatsapp_media,
}