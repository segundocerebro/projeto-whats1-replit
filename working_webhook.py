#!/usr/bin/env python3
"""
WEBHOOK QUE FUNCIONA - SEM CACHE, SEM PROBLEMAS
Arquivo completamente novo para resolver o bug de cache do Gunicorn
"""
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import time
import uuid
import shutil
from elevenlabs_service import generate_voice_response

app = Flask(__name__)

def generate_audio_fallback(text):
    """Gera áudio usando ElevenLabs"""
    try:
        return generate_voice_response(text)
    except:
        return None

@app.route("/webhook/whatsapp/working", methods=['POST', 'GET'])
def working_webhook():
    """WEBHOOK QUE FUNCIONA SEM CACHE"""
    if request.method == 'GET':
        return "✅ Webhook Funcionando - SEM CACHE! ✅", 200

    from_number = request.values.get('From', '').replace('whatsapp:', '')
    body = request.values.get('Body', '').strip()
    media_url = request.values.get('MediaUrl0', '')
    
    # ÁUDIO: Resposta personalizada
    if media_url:
        audio_text = "Recebi seu áudio! Como posso ajudá-lo hoje? Se precisar de informações sobre marketing digital, automação com IA ou qualquer outro tema da minha experiência, estou à disposição!"
        
        try:
            audio_path = generate_audio_fallback(audio_text)
            if audio_path and os.path.exists(audio_path):
                audio_filename = f"working_{int(time.time())}_{uuid.uuid4().hex[:8]}.mp3"
                public_path = f"static/audio/{audio_filename}"
                os.makedirs("static/audio", exist_ok=True)
                shutil.copy2(audio_path, public_path)
                
                public_url = f"{request.host_url}static/audio/{audio_filename}"
                
                resp = MessagingResponse()
                msg = resp.message(f"🎯 {audio_text}")
                msg.media(public_url)
                return str(resp)
        except:
            pass
        
        # Fallback sem áudio
        resp = MessagingResponse()
        resp.message(f"🎯 {audio_text}")
        return str(resp)
    
    # TEXTO
    if not body:
        body = "oi"
    
    reply = f"Olá! Sou o Endrigo Digital. Recebi sua mensagem: '{body}'. Como posso ajudá-lo com marketing digital, IA ou outras questões?"
    
    resp = MessagingResponse()
    message = resp.message()
    message.body(reply)
    
    if len(reply) < 500:
        try:
            audio_path = generate_audio_fallback(reply)
            if audio_path and os.path.exists(audio_path):
                audio_filename = f"working_text_{int(time.time())}_{uuid.uuid4().hex[:8]}.mp3"
                public_path = f"static/audio/{audio_filename}"
                os.makedirs("static/audio", exist_ok=True)
                shutil.copy2(audio_path, public_path)
                
                public_url = f"{request.host_url}static/audio/{audio_filename}"
                message.media(public_url)
        except:
            pass
    
    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)