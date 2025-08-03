# main.py - Clone Digital do Endrigo CORRIGIDO (Sem Cache)
from flask import Flask, request, render_template, jsonify, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
import time
import logging
import base64
import uuid
import shutil

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Imports condicionais
try:
    from elevenlabs_service import generate_voice_response
    def generate_audio_fallback(text):
        return generate_voice_response(text)
except ImportError:
    logging.warning("ElevenLabs service not available")
    def generate_audio_fallback(text):
        return None

try:
    from knowledge_base_manager import initialize_knowledge_base as init_kb
    def initialize_knowledge_base():
        return init_kb()
except ImportError:
    logging.warning("Knowledge base not available")
    def initialize_knowledge_base():
        class DummyKB:
            def get_context_for_query(self, query): return ""
        return DummyKB()

# Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure Flask
app = Flask(__name__)
database_url = os.getenv("DATABASE_URL")
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10
        }
    }
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = os.getenv("SESSION_SECRET", "dev-secret-key")

# Middleware
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    total_messages = db.Column(db.Integer, default=0)
    first_message_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_date = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    user_message = db.Column(db.Text)
    bot_response = db.Column(db.Text)
    message_type = db.Column(db.String(10))
    transcribed_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    """Serve audio files publicly"""
    return send_from_directory('static/audio', filename)

# NOVA ROTA BYPASS - CONTORNA CACHE TWILIO DO MANUS
@app.route("/webhook/whatsapp/fresh", methods=['POST', 'GET'])
def whatsapp_webhook_fresh():
    """Nova rota limpa - bypassa cache Twilio do Manus"""
    return whatsapp_webhook()

# WEBHOOK CORRIGIDO - SEM CACHE
@app.route("/webhook/whatsapp", methods=['POST', 'GET'])
def whatsapp_webhook():
    """Webhook corrigido - Sem cache, processamento completo de áudio"""
    if request.method == 'GET':
        return "Webhook funcionando! ✅", 200

    from_number = request.values.get('From', '').replace('whatsapp:', '')
    body = request.values.get('Body', '').strip()
    media_url = request.values.get('MediaUrl0', '')
    media_content_type = request.values.get('MediaContentType0', '')
    
    logging.info(f"📱 Nova mensagem de {from_number}: {'ÁUDIO' if media_url else body[:50]}")
    
    # Manage user in database
    user = User.query.filter_by(phone_number=from_number).first()
    if not user:
        user = User()
        user.phone_number = from_number
        user.total_messages = 0
        user.first_message_date = datetime.utcnow()
        user.last_message_date = datetime.utcnow()
        db.session.add(user)
    
    user.total_messages = (user.total_messages or 0) + 1
    user.last_message_date = datetime.utcnow()
    db.session.commit()

    # COMPLETE AUDIO PROCESSING (Grok's Fix)
    if media_url and 'audio' in media_content_type:
        logging.info(f"🎵 Processando áudio com sistema completo: {media_url}")
        try:
            # Download audio with robust authentication
            twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
            twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
            
            if twilio_sid and twilio_token:
                auth_string = base64.b64encode(f"{twilio_sid}:{twilio_token}".encode()).decode()
                headers = {'Authorization': f'Basic {auth_string}'}
                audio_response = requests.get(media_url, headers=headers, timeout=10)
                audio_data = audio_response.content
                
                logging.info(f"✅ Áudio baixado: {len(audio_data)} bytes")
                
                # Transcribe with Whisper
                temp_audio_path = f"/tmp/audio_{int(time.time())}.ogg"
                with open(temp_audio_path, 'wb') as f:
                    f.write(audio_data)
                
                with open(temp_audio_path, 'rb') as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="pt"
                    )
                
                transcribed_text = transcription.text.strip()
                logging.info(f"🎙️ Transcrição: {transcribed_text[:100]}...")
                
                # Clean up temp file
                try:
                    os.remove(temp_audio_path)
                except:
                    pass
                
                if transcribed_text:
                    # Get RAG context
                    try:
                        kb = initialize_knowledge_base()
                        context_from_docs = kb.get_context_for_query(transcribed_text)
                    except Exception as e:
                        logging.error(f"Erro RAG: {e}")
                        context_from_docs = ""
                    
                    # Generate personalized response with RAG
                    system_prompt = f"""
Você é Endrigo Almada, fundador do maior ecossistema publicitário do interior de São Paulo.

IDENTIDADE:
- 22 anos de experiência em marketing digital, IA, imobiliário e agronegócio
- Sede em Birigui, SP - referência em inovação no interior paulista
- Especialista em automação com IA e soluções digitais

PERSONALIDADE:
- Comunicação calorosa, profissional e entusiasmada
- Linguagem natural brasileira, próxima e acessível
- Positivo, prestativo e orientado a soluções

{context_from_docs}

Responda como Endrigo, integrando o contexto relevante de forma natural.
                    """
                    
                    chat_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": transcribed_text}
                        ],
                        max_tokens=300,
                        temperature=0.8
                    )
                    
                    reply = chat_response.choices[0].message.content
                    if reply:
                        reply = reply.strip()
                    else:
                        reply = "Desculpe, não consegui processar sua mensagem."
                    
                    # Generate audio response with ElevenLabs
                    try:
                        audio_path = generate_audio_fallback(reply)
                        if audio_path and os.path.exists(audio_path):
                            audio_filename = f"audio_complete_{int(time.time())}_{uuid.uuid4().hex[:8]}.mp3"
                            public_path = f"static/audio/{audio_filename}"
                            os.makedirs("static/audio", exist_ok=True)
                            shutil.copy2(audio_path, public_path)
                            
                            public_url = f"{request.host_url}static/audio/{audio_filename}"
                            
                            # Save conversation
                            conversation = Conversation()
                            conversation.phone_number = from_number
                            conversation.user_message = transcribed_text
                            conversation.bot_response = reply
                            conversation.message_type = 'audio'
                            conversation.transcribed_text = transcribed_text
                            conversation.timestamp = datetime.utcnow()
                            db.session.add(conversation)
                            db.session.commit()
                            
                            # Response with text + audio
                            resp = MessagingResponse()
                            msg = resp.message(f"🎯 {reply}")
                            msg.media(public_url)
                            
                            logging.info(f"✅ Áudio processado completamente: {audio_filename}")
                            return str(resp)
                    
                    except Exception as e:
                        logging.error(f"Erro geração áudio: {e}")
                    
                    # Fallback without audio but with complete response
                    resp = MessagingResponse()
                    resp.message(f"🎯 {reply}")
                    return str(resp)
        
        except Exception as e:
            logging.error(f"Erro processamento áudio: {e}")
        
        # Personalized fallback for audio
        fallback_text = "Recebi seu áudio! Como posso ajudá-lo hoje? Se precisar de informações sobre marketing digital, automação com IA ou qualquer outro tema da minha experiência, estou à disposição!"
        
        try:
            audio_path = generate_audio_fallback(fallback_text)
            if audio_path and os.path.exists(audio_path):
                audio_filename = f"fallback_{int(time.time())}_{uuid.uuid4().hex[:8]}.mp3"
                public_path = f"static/audio/{audio_filename}"
                os.makedirs("static/audio", exist_ok=True)
                shutil.copy2(audio_path, public_path)
                
                public_url = f"{request.host_url}static/audio/{audio_filename}"
                
                resp = MessagingResponse()
                msg = resp.message(f"🎯 {fallback_text}")
                msg.media(public_url)
                return str(resp)
        except:
            pass
        
        resp = MessagingResponse()
        resp.message(f"🎯 {fallback_text}")
        return str(resp)

    # TEXT PROCESSING with RAG
    if not body:
        body = "oi"
    
    try:
        kb = initialize_knowledge_base()
        context_from_docs = kb.get_context_for_query(body)
    except Exception as e:
        logging.error(f"Erro RAG: {e}")
        context_from_docs = ""
    
    # Generate personalized response
    system_prompt = f"""
Você é Endrigo Almada, fundador do maior ecossistema publicitário do interior de São Paulo.

IDENTIDADE:
- 22 anos de experiência em marketing digital, IA, imobiliário e agronegócio
- Sede em Birigui, SP - referência em inovação no interior paulista
- Especialista em automação com IA e soluções digitais

PERSONALIDADE:
- Comunicação calorosa, profissional e entusiasmada
- Linguagem natural brasileira, próxima e acessível
- Positivo, prestativo e orientado a soluções

{context_from_docs}

Responda como Endrigo, integrando o contexto relevante de forma natural.
    """
    
    chat_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": body}
        ],
        max_tokens=300,
        temperature=0.8
    )
    
    reply = chat_response.choices[0].message.content
    if reply:
        reply = reply.strip()
    else:
        reply = "Desculpe, não consegui processar sua mensagem."
    
    # Save conversation
    conversation = Conversation()
    conversation.phone_number = from_number
    conversation.user_message = body
    conversation.bot_response = reply
    conversation.message_type = 'text'
    conversation.timestamp = datetime.utcnow()
    db.session.add(conversation)
    db.session.commit()
    
    # Response with audio if possible
    resp = MessagingResponse()
    message = resp.message()
    message.body(reply)
    
    if len(reply) < 500:
        try:
            audio_path = generate_audio_fallback(reply)
            if audio_path and os.path.exists(audio_path):
                audio_filename = f"text_{int(time.time())}_{uuid.uuid4().hex[:8]}.mp3"
                public_path = f"static/audio/{audio_filename}"
                os.makedirs("static/audio", exist_ok=True)
                shutil.copy2(audio_path, public_path)
                
                public_url = f"{request.host_url}static/audio/{audio_filename}"
                message.media(public_url)
        except Exception as e:
            logging.error(f"Erro áudio texto: {e}")
    
    return str(resp)

@app.route("/")
def home():
    """Dashboard principal"""
    try:
        total_users = db.session.query(User).count()
        total_conversations = db.session.query(Conversation).count()
        return f"""
        <h1>🎯 Clone Digital do Endrigo – CORRIGIDO! 🎤</h1>
        <p><strong>Usuários:</strong> {total_users}</p>
        <p><strong>Conversas:</strong> {total_conversations}</p>
        <p><strong>Webhook:</strong> <code>/webhook/whatsapp</code></p>
        <p><strong>Status:</strong> ✅ Sistema corrigido sem cache</p>
        """
    except Exception as e:
        return f"""
        <h1>🎯 Clone Digital do Endrigo – CORRIGIDO! 🎤</h1>
        <p><strong>Webhook:</strong> <code>/webhook/whatsapp</code></p>
        <p><strong>Status:</strong> ✅ Sistema corrigido sem cache</p>
        """

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Endrigo Digital Clone Corrigido"}, 200

@app.route('/stats')
def stats():
    """Statistics endpoint"""
    try:
        total_users = db.session.query(User).count()
        total_conversations = db.session.query(Conversation).count()
        audio_conversations = db.session.query(Conversation).filter_by(message_type='audio').count()
        
        return jsonify({
            'total_users': total_users,
            'total_conversations': total_conversations,
            'audio_conversations': audio_conversations,
            'text_conversations': total_conversations - audio_conversations,
            'system_status': 'corrigido'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NOVO ENDPOINT PARA BYPASS DE CACHE (SOLUÇÃO GEMINI)
@app.route("/test-endpoint", methods=["GET"])
def test_simple():
    return "Endpoint teste funcionando!"

@app.route("/webhook/info", methods=["GET"])
def webhook_info():
    """Informações sobre webhooks disponíveis para contornar cache"""
    return {
        "fresh_webhook": f"{request.host_url}webhook/whatsapp/fresh",
        "original_webhook": f"{request.host_url}webhook/whatsapp", 
        "cache_issue": "Use 'fresh' para contornar cache do Manus",
        "status": "Implementado Bypass Twilio Cache"
    }

# Export app for Gunicorn
app = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)