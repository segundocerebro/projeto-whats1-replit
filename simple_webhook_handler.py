#!/usr/bin/env python3
"""
Handler simples e rápido para WhatsApp - sem travamentos
"""
import logging
import os
from openai import OpenAI
from twilio.twiml.messaging_response import MessagingResponse

class SimpleWhatsAppHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
    def process_message(self, message_text: str, from_number: str) -> str:
        """Processa mensagem de forma rápida e simples"""
        try:
            logging.info(f"[SIMPLE] Processando: {message_text[:50]}...")
            
            # Prompt direto e eficiente
            prompt = f"""Você é Endrigo Almada, especialista em marketing digital com 22 anos de experiência.
            Responda de forma natural, amigável e profissional em português brasileiro.
            Mantenha respostas concisas (máximo 150 palavras).
            
            Mensagem: {message_text}"""
            
            # Chat completion direto - muito mais rápido
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é Endrigo Almada, especialista em marketing digital com 22 anos de experiência. Responda de forma natural, amigável e profissional em português brasileiro."},
                    {"role": "user", "content": message_text}
                ],
                max_tokens=200,
                temperature=0.7,
                timeout=8  # Timeout agressivo
            )
            
            response_text = response.choices[0].message.content.strip()
            logging.info(f"[SIMPLE] Resposta: {response_text[:50]}...")
            
            return response_text
            
        except Exception as e:
            logging.error(f"[SIMPLE] Erro: {e}")
            return "Olá! Estou aqui para ajudar com marketing digital. Como posso te apoiar hoje?"
    
    def create_twiml_response(self, text: str) -> str:
        """Cria resposta TwiML simples"""
        resp = MessagingResponse()
        resp.message(text)
        return str(resp)