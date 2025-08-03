# app/utils/wa.py
import logging
logger = logging.getLogger(__name__)

WHATSAPP_PREFIX = "whatsapp:"

def normalize_wa(number: str) -> str:
    """Garante que um número de telefone tenha o prefixo 'whatsapp:'."""
    if not number:
        raise ValueError("O número de telefone não pode ser vazio.")
    
    n = number.strip()
    if not n.startswith(WHATSAPP_PREFIX):
        logger.warning(f"[WA-NORMALIZER] Adicionando prefixo 'whatsapp:' ao número: {n}")
        n = WHATSAPP_PREFIX + n
    return n

def assert_same_channel(from_n: str, to_n: str):
    """Verifica se ambos os números são do canal WhatsApp, para segurança."""
    if not (from_n.startswith(WHATSAPP_PREFIX) and to_n.startswith(WHATSAPP_PREFIX)):
        raise ValueError(f"Erro de canal: Remetente ({from_n}) e Destinatário ({to_n}) devem ser ambos do WhatsApp.")