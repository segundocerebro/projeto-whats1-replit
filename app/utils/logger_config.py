# app/utils/logger_config.py
import logging
import sys

def setup_logging(level=logging.INFO):
    """Configura o sistema de logging para ser limpo e informativo."""
    fmt = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    logging.basicConfig(level=level, format=fmt, stream=sys.stdout)