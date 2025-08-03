# app/clients/twilio_client.py
import os
import logging
import requests
import uuid
import subprocess
import tempfile
from twilio.rest import Client
# Removed circular import - OpenAI client is handled elsewhere

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def _transcode_to_wav(src_path: str):
    dst_path = src_path.rsplit(".", 1)[0] + ".wav"
    command = ["ffmpeg", "-y", "-i", src_path, "-ac", "1", "-ar", "16000", "-acodec", "pcm_s16le", dst_path]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        return dst_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro no FFMPEG: {e.stderr}")
        raise

def download_and_prepare_audio(media_url: str):
    try:
        tmpdir = tempfile.mkdtemp(prefix="wa_audio_")
        with requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=20, stream=True) as r:
            r.raise_for_status()
            ext = ".ogg"
            raw_path = os.path.join(tmpdir, f"{uuid.uuid4()}{ext}")
            with open(raw_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        wav_path = _transcode_to_wav(raw_path)
        os.remove(raw_path)
        return wav_path
    except Exception as e:
        logger.error(f"❌ Falha ao baixar/transcodificar áudio: {e}", exc_info=True)
        return None

def transcrever_audio_com_whisper(caminho_do_audio: str):
    """Transcreve áudio usando OpenAI Whisper - versão sem circular import"""
    from openai import OpenAI
    
    if not caminho_do_audio or not os.path.exists(caminho_do_audio):
        return "Erro: Arquivo de áudio não encontrado."
    try:
        # Initialize OpenAI client locally to avoid circular import
        openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        with open(caminho_do_audio, "rb") as audio_file:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, response_format="text"
            )
        return str(transcription).strip()
    except Exception as e:
        logger.error(f"❌ Erro na transcrição com Whisper: {e}", exc_info=True)
        return "Desculpe, tive um problema para entender seu áudio."
    finally:
        if caminho_do_audio and os.path.exists(caminho_do_audio):
            try:
                os.remove(caminho_do_audio)
            except OSError as e:
                logger.error(f"Erro ao remover arquivo temporário {caminho_do_audio}: {e}")