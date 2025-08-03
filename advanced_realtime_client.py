"""
OpenAI Realtime API Client para Clone Digital Fluido
Implementa WebSocket connection com personalidade avançada
"""
import asyncio
import json
import logging
import websockets
import base64
import os
from typing import Dict, Any, Optional

class RealtimeVoiceClone:
    def __init__(self):
        self.ws = None
        self.is_connected = False
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.conversation_history = []
        
    async def connect(self):
        """Conecta ao OpenAI Realtime API"""
        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        try:
            self.ws = await websockets.connect(url, extra_headers=headers)
            self.is_connected = True
            logging.info("Conectado ao OpenAI Realtime API")
            await self.configure_session()
            return True
        except Exception as e:
            logging.error(f"Erro na conexão Realtime API: {e}")
            return False
    
    async def configure_session(self):
        """Configura sessão com personalidade avançada v4"""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": "coral",  # Voz mais natural que 'alloy'
                "instructions": self.get_personality_prompt(),
                "turn_detection": {
                    "type": "server_vad",  # Detecção automática de voz
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                },
                "temperature": 0.8,  # Mais natural que 1.02
                "max_response_output_tokens": 4096
            }
        }
        
        if self.ws:
            await self.ws.send(json.dumps(session_config))
        logging.info("Sessão configurada com personalidade v4")
    
    def get_personality_prompt(self):
        """Prompt otimizado baseado no guia de migração Realtime API"""
        return """
IDENTIDADE:
Você é o Endrigo Digital, especialista em marketing digital e IA com 22 anos de experiência.

CONTEXTO PROFISSIONAL:
- Fundador de ecossistema publicitário em Birigui, SP
- Expertise: Marketing digital, IA aplicada, setores imobiliário/agronegócio
- Atendimento via WhatsApp da agência

PERSONALIDADE REALTIME:
- Tom: Profissional caloroso, entusiasmado com tecnologia
- Linguagem: Português brasileiro natural, sem robótica
- Estilo: Consultivo experiente, exemplos práticos
- Fluidez: Responda de forma conversacional, como se fosse uma ligação

CONHECIMENTO BASE:
Baseie todas as respostas nos documentos da base de conhecimento da agência.
Sempre mencione cases e resultados concretos quando relevante.

COMPORTAMENTO DE CONVERSAÇÃO:
- Mantenha continuidade natural entre falas
- Use "é", "né", "olha" para soar natural
- Demonstre expertise sem ser pedante
- Seja conciso mas completo
- Use memória contextual para referências passadas
- Exemplos práticos da sua experiência de 22+ anos

FOCO EMPRESARIAL:
- Otimização empresarial com IA
- Público: Empresários inovadores e empreendedores  
- Método: Data-driven humanizado
- Abordagem: Proativa com entrega de valor real
        """
    
    async def process_audio_message(self, audio_data: bytes, user_context: Dict[str, Any] = None):
        """Processa mensagem de áudio com context injection"""
        if not self.is_connected:
            await self.connect()
        
        # Injeta contexto se fornecido
        if user_context:
            await self.inject_context(user_context)
        
        # Envia áudio para processamento
        audio_event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{
                    "type": "input_audio",
                    "audio": base64.b64encode(audio_data).decode()
                }]
            }
        }
        
        if self.ws:
            await self.ws.send(json.dumps(audio_event))
        
        # Solicita resposta
        response_event = {"type": "response.create"}
        if self.ws:
            await self.ws.send(json.dumps(response_event))
        
        # Aguarda resposta
        return await self.wait_for_response()
    
    async def inject_context(self, context: Dict[str, Any]):
        """Injeta contexto da memória avançada na conversa"""
        context_prompt = f"""
CONTEXTO DA MEMÓRIA AVANÇADA:
Conversas Recentes: {context.get('recent_conversation', '')}
Preferências do Usuário: {context.get('user_preferences', [])}
Contexto de Negócios: {context.get('business_context', [])}
Insights Aprendidos: {context.get('insights', [])}

Use este contexto para manter continuidade total da conversa.
        """
        
        context_event = {
            "type": "conversation.item.create", 
            "item": {
                "type": "message",
                "role": "system",
                "content": [{"type": "text", "text": context_prompt}]
            }
        }
        
        if self.ws:
            await self.ws.send(json.dumps(context_event))
    
    async def wait_for_response(self, timeout: int = 10):
        """Aguarda resposta do Realtime API"""
        try:
            if self.ws:
                async for message in self.ws:
                    event = json.loads(message)
                    
                    if event["type"] == "response.audio.done":
                        audio_data = base64.b64decode(event["audio"])
                        return {
                            "audio": audio_data,
                            "text": event.get("transcript", ""),
                            "success": True
                        }
                    elif event["type"] == "error":
                        logging.error(f"Erro Realtime API: {event}")
                        return {"success": False, "error": event}
                    
        except asyncio.TimeoutError:
            logging.error("Timeout aguardando resposta do Realtime API")
            return {"success": False, "error": "timeout"}
    
    async def close(self):
        """Fecha conexão WebSocket"""
        if self.ws:
            await self.ws.close()
            self.is_connected = False