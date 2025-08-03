import os
import logging
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-openai-api-key")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio_message(audio_file_path):
    """Transcribe audio using OpenAI Whisper"""
    try:
        logging.info(f"Transcribing audio file: {audio_file_path}")
        
        with open(audio_file_path, "rb") as audio_file:
            response = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pt"  # Portuguese language
            )
        
        transcribed_text = response.text
        logging.info(f"Transcription successful: {transcribed_text}")
        return transcribed_text
        
    except Exception as e:
        logging.error(f"Error transcribing audio: {str(e)}")
        raise e

def get_endrigo_response(message):
    """Get intelligent response from Endrigo Digital using OpenAI"""
    try:
        logging.info(f"Getting Endrigo response for: {message}")
        
        # System prompt defining Endrigo Digital's personality
        system_prompt = """Você é Endrigo Digital, um assistente virtual brasileiro inteligente e prestativo. 
        
        Características da sua personalidade:
        - Fale sempre em português brasileiro
        - Seja amigável, profissional e empático
        - Use um tom conversacional e acessível
        - Ajude com qualquer pergunta ou solicitação
        - Seja criativo e informativo nas suas respostas
        - Mantenha as respostas concisas mas completas
        - Use emojis ocasionalmente para tornar a conversa mais calorosa
        
        Você pode ajudar com:
        - Responder perguntas gerais
        - Dar conselhos e sugestões
        - Explicar conceitos
        - Ajudar com tarefas do dia a dia
        - Conversar sobre diversos assuntos
        
        Sempre responda de forma útil e positiva."""
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        endrigo_response = response.choices[0].message.content
        logging.info(f"Endrigo response: {endrigo_response}")
        return endrigo_response
        
    except Exception as e:
        logging.error(f"Error getting Endrigo response: {str(e)}")
        raise e
