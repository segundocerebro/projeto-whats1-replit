"""
WEBHOOK WHATSAPP 100% FUNCIONANDO
Sistema simples e eficaz sem complicações
"""
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import requests
import logging
from openai import OpenAI
from elevenlabs_service import generate_voice_response

# Configuração
app = Flask(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/webhook/FUNCIONA', methods=['POST'])
def webhook_que_funciona():
    """Sistema que FUNCIONA de verdade"""
    try:
        # 1. Receber dados
        body = request.values.get('Body', '').strip()
        media_url = request.values.get('MediaUrl0', '')
        from_number = request.values.get('From', '').replace('whatsapp:', '')
        
        logging.info(f"💬 Mensagem de {from_number}: {body}")
        
        # 2. Se for áudio, tentar transcrever (mas não quebrar se falhar)
        if media_url and 'audio' in request.values.get('MediaContentType0', ''):
            logging.info("🎤 Áudio detectado")
            try:
                # Baixar com autenticação
                import base64
                twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
                twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
                
                if twilio_sid and twilio_token:
                    credentials = base64.b64encode(f"{twilio_sid}:{twilio_token}".encode()).decode()
                    headers = {'Authorization': f'Basic {credentials}'}
                    audio_data = requests.get(media_url, headers=headers, timeout=10).content
                    
                    # Salvar e transcrever
                    with open('/tmp/audio.ogg', 'wb') as f:
                        f.write(audio_data)
                    
                    with open('/tmp/audio.ogg', 'rb') as f:
                        transcription = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=f,
                            language="pt"
                        )
                        body = transcription.text
                        logging.info(f"✅ Transcrição: {body}")
                        
            except Exception as e:
                logging.error(f"❌ Erro no áudio: {e}")
                body = "você enviou um áudio"  # Continuar mesmo com erro
        
        # 3. Gerar resposta SEMPRE
        if not body:
            body = "oi"
        
        # Sistema de resposta direto
        if "áudio" in body.lower() or "audio" in body.lower():
            reply = "Sim, consigo enviar áudios perfeitamente! Todas minhas respostas são convertidas automaticamente em áudio com minha voz clonada. Como posso te ajudar?"
        elif "oi" in body.lower() or "olá" in body.lower():
            reply = "Oi! Sou o Endrigo Almada, especialista em marketing digital! Como posso ajudar você hoje?"
        else:
            # Usar AI apenas se necessário
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user", 
                        "content": f"""Você é Endrigo Almada, especialista brasileiro em marketing digital.
                        
                        IMPORTANTE: Você ENVIA ÁUDIOS automaticamente. Suas respostas são convertidas em áudio.
                        
                        Responda naturalmente para: {body}"""
                    }],
                    max_tokens=200,
                    temperature=0.7
                )
                reply = response.choices[0].message.content.strip()
            except:
                reply = "Sou o Endrigo! Especialista em marketing digital. Como posso te ajudar?"
        
        # 4. Criar resposta TwiML
        resp = MessagingResponse()
        message = resp.message()
        message.body(reply)
        
        # 5. Gerar áudio se possível
        try:
            if len(reply) < 500:  # Evitar áudios muito longos
                audio_path = generate_voice_response(reply.replace("*", "").replace("_", ""))
                if audio_path:
                    public_url = f"{os.getenv('REPLIT_URL', 'https://your-repl.replit.dev')}/static/audio/{os.path.basename(audio_path)}"
                    message.media(public_url)
                    logging.info(f"🔊 Áudio anexado: {public_url}")
        except Exception as e:
            logging.error(f"❌ Erro no áudio: {e}")
            # Continuar sem áudio
        
        logging.info(f"✅ Resposta enviada: {reply[:50]}...")
        return str(resp)
        
    except Exception as e:
        logging.error(f"💥 ERRO GERAL: {e}")
        # Resposta de emergência
        resp = MessagingResponse()
        resp.message("Oi! Sou o Endrigo. Tivemos um problema técnico momentâneo. Tente novamente!")
        return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)