#!/usr/bin/env python3
"""
Handler simples para áudio WhatsApp - transcreve e responde
"""
import logging
import os
import requests
import tempfile
from openai import OpenAI
from typing import Optional, Dict

class SimpleAudioHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
    def download_audio(self, media_url: str) -> Optional[str]:
        """Baixa áudio do WhatsApp"""
        try:
            response = requests.get(media_url, timeout=10)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                    temp_file.write(response.content)
                    return temp_file.name
            return None
        except Exception as e:
            logging.error(f"Erro ao baixar áudio: {e}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcreve áudio usando Whisper"""
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="pt"
                )
            return transcript.text.strip()
        except Exception as e:
            logging.error(f"Erro na transcrição: {e}")
            return None
    
    def generate_response(self, transcript: str) -> str:
        """Gera resposta baseada na transcrição"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é Endrigo Almada, especialista em marketing digital com 22 anos de experiência. Responda de forma natural e amigável em português brasileiro."},
                    {"role": "user", "content": f"O usuário disse em áudio: {transcript}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Erro ao gerar resposta: {e}")
            return "Entendi sua mensagem de áudio! Como posso te ajudar com marketing digital?"
    
    def process_audio_message(self, media_url: str, from_number: str) -> Dict[str, str]:
        """Processa mensagem de áudio completa"""
        try:
            logging.info(f"[AUDIO] Processando áudio de {from_number}")
            
            # 1. Baixa áudio
            audio_path = self.download_audio(media_url)
            if not audio_path:
                return {
                    "text": "Não consegui processar o áudio. Pode repetir ou enviar por texto?",
                    "success": False
                }
            
            # 2. Transcreve
            transcript = self.transcribe_audio(audio_path)
            if not transcript:
                os.unlink(audio_path)
                return {
                    "text": "Não consegui entender o áudio. Pode falar mais alto ou enviar por texto?",
                    "success": False
                }
            
            logging.info(f"[AUDIO] Transcrito: {transcript[:50]}...")
            
            # 3. Gera resposta
            response_text = self.generate_response(transcript)
            
            # 4. Limpa arquivo temporário
            os.unlink(audio_path)
            
            logging.info(f"[AUDIO] Resposta gerada: {response_text[:50]}...")
            
            return {
                "text": response_text,
                "transcript": transcript,
                "success": True
            }
            
        except Exception as e:
            logging.error(f"[AUDIO] Erro geral: {e}")
            return {
                "text": "Houve um problema ao processar o áudio. Pode tentar novamente?",
                "success": False
            }

# Instância global
simple_audio_handler = SimpleAudioHandler()