# app/utils/executor.py
import concurrent.futures
import logging
import threading

logger = logging.getLogger(__name__)

# Executor global para tasks do webhook (mais robusto que Threading manual)
EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=8)

def _thread_excepthook(args):
    """Função que captura e loga qualquer erro não tratado em uma thread."""
    logger.error("[THREAD CRASH DETECTADO]", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))

threading.excepthook = _thread_excepthook