# app/__init__.py
import os
import logging
import threading
import concurrent.futures
from .utils.logger_config import setup_logging
from flask import Flask

# Primeiro, configura o logging
setup_logging()
logger = logging.getLogger(__name__)

# Fail-safe de boot: Corrige o sender do Twilio sem prefixo
bn = os.environ.get("TWILIO_PHONE_NUMBER", "")
if bn and not bn.startswith("whatsapp:"):
    logger.warning("[BOOT] TWILIO_PHONE_NUMBER sem 'whatsapp:'. Corrigindo em runtime.")
    os.environ["TWILIO_PHONE_NUMBER"] = "whatsapp:" + bn

# Executor global para tarefas em segundo plano (robusto)
EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=8)

def _thread_excepthook(args):
    """Captura e loga qualquer erro não tratado que aconteça em uma thread."""
    logger.error("[THREAD CRASH DETECTADO]", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))

threading.excepthook = _thread_excepthook

def create_app():
    """Cria e retorna a instância da aplicação Flask."""
    app = Flask(__name__)
    
    # Import blueprint after app creation to avoid circular imports
    from .routes import whatsapp_bp
    app.register_blueprint(whatsapp_bp)
    
    @app.get("/health")
    def health():
        """Endpoint de verificação de saúde para monitoramento."""
        return "ok", 200
        
    return app