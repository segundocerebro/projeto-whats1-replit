"""
Configurações centralizadas para o Clone Digital do Endrigo v2.0
"""
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Config:
    """Configurações da aplicação"""
    
    # Flask
    SECRET_KEY = os.getenv("SESSION_SECRET", "dev-secret-key-v2")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DATABASE_URL = "sqlite:///endrigo_v2.db"
    
    # SQLAlchemy URI
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    
    # ElevenLabs
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "SuM1a4mUYXCmWfwWYCx0")
    
    # Paths
    DOCUMENTS_PATH = "documents"
    STATIC_AUDIO_PATH = "static/audio"
    
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
    }
    
    if "postgres" in DATABASE_URL.lower():
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {
            'sslmode': 'require',
            'connect_timeout': 10
        }

def get_logger(name):
    """Helper para obter logger configurado"""
    return logging.getLogger(name)