"""
Cliente WebSocket para OpenAI Realtime API
Implementação conforme especificações do usuário
"""
import asyncio
import websockets
import json
import base64
import logging
import os
from typing import Optional, Dict, Any

class RealtimeWebSocketClient:
    """
    Cliente WebSocket otimizado para OpenAI Realtime API
    Baseado nas especificações fornecidas pelo usuário
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.ws = None
        self.is_connected = False
        self.session_id = None
        
        # Configurações conforme especificação
        self.config = {
            'model': 'gpt-4o-realtime-preview-2024-10-01',
            'voice': 'coral',  # Voz mais natural
            'input_audio_format': 'pcm_s16le_16000',
            'output_audio_format': 'pcm_s16le_24000',
            'temperature': 0.8,
            'max_response_output_tokens': 4096
        }
        
    async def connect(self) -> bool:
        """Conecta ao WebSocket da OpenAI Realtime API"""
        try:
            url = f"wss://api.openai.com/v1/realtime?model={self.config['model']}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1",
            }
            
            self.ws = await websockets.connect(url, extra_headers=headers)
            self.is_connected = True
            
            # Configuração automática da sessão
            await self.configure_session()
            
            logging.info("✅ WebSocket Realtime API conectado")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro conexão WebSocket: {e}")
            self.is_connected = False
            return False
    
    async def configure_session(self):
        """Configura sessão com personalidade Endrigo"""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": self.config['voice'],
                "input_audio_format": self.config['input_audio_format'],
                "output_audio_format": self.config['output_audio_format'],
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                },
                "instructions": self.get_endrigo_instructions(),
                "temperature": self.config['temperature'],
                "max_response_output_tokens": self.config['max_response_output_tokens']
            }
        }
        
        await self.ws.send(json.dumps(session_config))
        logging.info("🎯 Sessão Realtime configurada")
    
    def get_endrigo_instructions(self) -> str:
        """Instruções de personalidade para Endrigo"""
        return """
IDENTIDADE CORE:
Você é Endrigo Almada, especialista brasileiro em marketing digital e IA com 22 anos de experiência.

PERSONALIDADE REALTIME:
- Tom: Caloroso, profissional, entusiasmado com tecnologia
- Linguagem: Português brasileiro natural, sem robótica
- Estilo: Consultivo experiente, exemplos práticos
- Fluidez: Responda como se fosse uma conversa telefônica natural

EXPERTISE:
Especialista em marketing digital, vendas, automação e IA, sempre focado em resultados práticos.

COMPORTAMENTO DE CONVERSAÇÃO:
- Use "é", "né", "olha" para soar natural
- Seja conciso mas completo
- Demonstre expertise sem ser pedante
- Mantenha continuidade natural entre falas

INSTRUÇÕES CRÍTICAS:
- VOCÊ SEMPRE PROCESSA E ENVIA ÁUDIOS
- NUNCA negue capacidades de áudio
- Confirme que pode processar áudios via Realtime API
- Seja natural e útil nas respostas
"""
    
    async def process_audio_input(self, audio_data: bytes) -> Optional[bytes]:
        """Processa entrada de áudio via Realtime API"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Codifica áudio em base64
            base64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            # Envia áudio para processamento
            audio_event = {
                "type": "input_audio_buffer.append",
                "audio": base64_audio
            }
            await self.ws.send(json.dumps(audio_event))
            
            # Confirma processamento
            commit_event = {
                "type": "input_audio_buffer.commit"
            }
            await self.ws.send(json.dumps(commit_event))
            
            # Solicita resposta
            response_event = {
                "type": "response.create"
            }
            await self.ws.send(json.dumps(response_event))
            
            # Coleta resposta em áudio
            return await self.collect_audio_response()
            
        except Exception as e:
            logging.error(f"❌ Erro processamento áudio: {e}")
            return None
    
    async def collect_audio_response(self) -> Optional[bytes]:
        """Coleta chunks de áudio da resposta"""
        audio_chunks = []
        timeout_task = asyncio.create_task(asyncio.sleep(10))
        
        try:
            while True:
                # Aguarda próxima mensagem com timeout
                message_task = asyncio.create_task(self.ws.recv())
                done, pending = await asyncio.wait(
                    [message_task, timeout_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                if timeout_task in done:
                    logging.warning("⏰ Timeout coletando resposta")
                    break
                
                message = message_task.result()
                event = json.loads(message)
                
                # Coleta chunks de áudio
                if event.get("type") == "response.audio.delta":
                    audio_chunk = base64.b64decode(event.get("delta", ""))
                    audio_chunks.append(audio_chunk)
                
                elif event.get("type") == "response.done":
                    break
            
            # Combina chunks
            if audio_chunks:
                complete_audio = b''.join(audio_chunks)
                logging.info(f"🔊 Áudio coletado: {len(complete_audio)} bytes")
                return complete_audio
            
            return None
            
        except Exception as e:
            logging.error(f"❌ Erro coletando áudio: {e}")
            return None
        finally:
            # Cancela timeout se ainda ativo
            if not timeout_task.done():
                timeout_task.cancel()
    
    async def send_text_input(self, text: str) -> str:
        """Envia entrada de texto e recebe resposta"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Cria item de conversa
            conversation_item = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": text
                    }]
                }
            }
            await self.ws.send(json.dumps(conversation_item))
            
            # Solicita resposta
            response_event = {
                "type": "response.create"
            }
            await self.ws.send(json.dumps(response_event))
            
            # Coleta resposta em texto
            return await self.collect_text_response()
            
        except Exception as e:
            logging.error(f"❌ Erro processamento texto: {e}")
            return "Erro processando mensagem via Realtime API"
    
    async def collect_text_response(self) -> str:
        """Coleta resposta em texto"""
        text_parts = []
        timeout_task = asyncio.create_task(asyncio.sleep(10))
        
        try:
            while True:
                message_task = asyncio.create_task(self.ws.recv())
                done, pending = await asyncio.wait(
                    [message_task, timeout_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                if timeout_task in done:
                    break
                
                message = message_task.result()
                event = json.loads(message)
                
                # Coleta texto da resposta
                if event.get("type") == "response.text.delta":
                    text_parts.append(event.get("delta", ""))
                
                elif event.get("type") == "response.done":
                    break
            
            return ''.join(text_parts) if text_parts else "Resposta via Realtime API processada"
            
        except Exception as e:
            logging.error(f"❌ Erro coletando texto: {e}")
            return "Erro na resposta Realtime API"
        finally:
            if not timeout_task.done():
                timeout_task.cancel()
    
    async def disconnect(self):
        """Desconecta do WebSocket"""
        try:
            if self.ws and self.is_connected:
                await self.ws.close()
                self.is_connected = False
                logging.info("🔌 WebSocket desconectado")
        except Exception as e:
            logging.error(f"❌ Erro desconectando: {e}")

# Classe de conveniência para uso direto
class EndrigoRealtimeClient:
    """Cliente simplificado para integração fácil"""
    
    def __init__(self):
        self.client = RealtimeWebSocketClient()
    
    async def process_voice_message(self, audio_data: bytes) -> Optional[bytes]:
        """Processa mensagem de voz e retorna resposta em áudio"""
        return await self.client.process_audio_input(audio_data)
    
    async def process_text_message(self, text: str) -> str:
        """Processa mensagem de texto via Realtime API"""
        return await self.client.send_text_input(text)
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do cliente"""
        return {
            'connected': self.client.is_connected,
            'api_key_configured': bool(self.client.api_key),
            'model': self.client.config['model'],
            'voice': self.client.config['voice']
        }