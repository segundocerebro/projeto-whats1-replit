"""
Handler de Áudio Realtime - Recebe áudio, compreende e responde em áudio
Baseado no código JavaScript fornecido pelo usuário
"""
import asyncio
import websockets
import json
import logging
import base64
import tempfile
import os
import subprocess
from typing import Optional, Dict, Any
import requests
from twilio.rest import Client

class EndrigoRealtimeAudioClone:
    """
    Sistema completo de áudio: recebe áudio, compreende e responde em áudio
    Implementação Python baseada no código JavaScript fornecido
    """
    
    def __init__(self):
        self.ws = None
        self.audio_chunks = []
        self.current_user = None
        self.is_connected = False
        
        # Configurações Twilio
        self.twilio_client = Client(
            os.environ.get('TWILIO_ACCOUNT_SID'),
            os.environ.get('TWILIO_AUTH_TOKEN')
        )
        self.twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER', '+14155238886')
        
        # Configurações de áudio
        self.input_audio_format = 'pcm_s16le_16000'
        self.output_audio_format = 'pcm_s16le_24000'
        
    async def connect(self):
        """Conecta ao OpenAI Realtime API com configuração de áudio"""
        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        try:
            self.ws = await websockets.connect(url, extra_headers=headers)
            self.is_connected = True
            
            # Configura session para áudio
            await self.configure_audio_session()
            
            # Inicia listener de eventos
            asyncio.create_task(self.listen_to_server_events())
            
            logging.info("🎤 Endrigo Realtime Audio conectado!")
            return True
            
        except Exception as e:
            logging.error(f"Erro na conexão Realtime Audio: {e}")
            return False
    
    async def configure_audio_session(self):
        """Configura sessão otimizada para áudio"""
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": "coral",  # Voz mais natural
                "input_audio_format": self.input_audio_format,
                "output_audio_format": self.output_audio_format,
                "instructions": self.get_audio_optimized_prompt(),
                "turn_detection": {
                    "type": "server_vad",  # Detecção automática de voz
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                },
                "temperature": 0.8,
                "max_response_output_tokens": 4096
            }
        }
        
        if self.ws:
            await self.ws.send(json.dumps(config))
            logging.info("🔧 Sessão de áudio configurada")
    
    def get_audio_optimized_prompt(self) -> str:
        """Prompt otimizado para conversação por áudio"""
        return """
IDENTIDADE ÁUDIO:
Você é o Endrigo Digital falando diretamente por áudio via WhatsApp.

PERSONALIDADE PARA ÁUDIO:
- Tom: Caloroso e natural como uma conversa telefônica
- Ritmo: Fluido, sem pausas robóticas
- Linguagem: Português brasileiro coloquial
- Expressões: Use "olha", "é", "né", "beleza" naturalmente

EXPERTISE ÁUDIO:
- 22 anos em marketing digital e IA
- Especialista em: Marketing, Automação, IA, Setores Imobiliário/Agronegócio
- Fundador do ecossistema publicitário em Birigui, SP

COMPORTAMENTO ÁUDIO:
- Responda como se fosse uma ligação amigável
- Seja direto mas caloroso
- Use exemplos práticos e concretos
- Mantenha energia positiva e engajamento
- Demonstre expertise sem ser técnico demais

FOCO:
- Ajudar empresários com soluções de IA e marketing
- Entregar valor real em cada resposta
- Manter conversa natural e fluida
        """
    
    async def process_whatsapp_audio(self, audio_url: str, from_number: str) -> bool:
        """
        Processa áudio do WhatsApp - Pipeline completo:
        1. Download áudio → 2. Converte formato → 3. Envia Realtime → 4. Recebe resposta
        """
        try:
            logging.info(f"🎵 Processando áudio de {from_number}")
            
            # 1. Download do áudio do WhatsApp
            audio_buffer = await self.download_whatsapp_audio(audio_url)
            
            # 2. Converte para formato Realtime API
            pcm_audio = await self.convert_to_realtime_format(audio_buffer)
            base64_audio = base64.b64encode(pcm_audio).decode()
            
            # 3. Envia áudio para Realtime API
            await self.send_audio_to_realtime(base64_audio, from_number)
            
            logging.info("✅ Áudio enviado para processamento Realtime")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro processando áudio: {e}")
            return False
    
    async def download_whatsapp_audio(self, audio_url: str) -> bytes:
        """Download do áudio do WhatsApp"""
        try:
            response = requests.get(audio_url, timeout=15)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logging.error(f"Erro no download do áudio: {e}")
            raise
    
    async def convert_to_realtime_format(self, audio_buffer: bytes) -> bytes:
        """
        GARANTE conversão WhatsApp → Realtime API
        WhatsApp Voice Note (OGG Opus) → PCM 16kHz mono
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as input_file:
            input_file.write(audio_buffer)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.raw') as output_file:
            output_path = output_file.name
        
        try:
            # GARANTE conversão exata: WhatsApp OGG → PCM 16kHz mono
            cmd = [
                'ffmpeg', 
                '-i', input_path,           # Input WhatsApp audio
                '-f', 's16le',              # Output format: signed 16-bit little-endian
                '-acodec', 'pcm_s16le',     # Codec: PCM signed 16-bit 
                '-ar', '16000',             # GARANTIDO: 16kHz (Realtime API requirement)
                '-ac', '1',                 # GARANTIDO: Mono channel
                '-y',                       # Overwrite output
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logging.error(f"Erro conversão WhatsApp→Realtime: {result.stderr}")
                raise Exception(f"Falha na conversão de áudio: {result.stderr}")
            
            # Lê áudio convertido
            with open(output_path, 'rb') as f:
                pcm_data = f.read()
            
            logging.info(f"✅ Áudio convertido: {len(audio_buffer)} bytes → {len(pcm_data)} bytes PCM")
            return pcm_data
            
        except subprocess.TimeoutExpired:
            logging.error("Timeout na conversão de áudio")
            raise Exception("Timeout na conversão de áudio")
            
        finally:
            # Cleanup garantido
            for temp_file in [input_path, output_path]:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    async def send_audio_to_realtime(self, base64_audio: str, from_number: str):
        """
        GARANTE envio correto do áudio para Realtime API
        Implementa o fluxo exato do código JavaScript
        """
        if not self.ws:
            raise Exception("WebSocket não conectado")
        
        # GARANTE: Armazena usuário atual para resposta
        self.current_user = from_number
        self.audio_chunks = []  # Reset chunks para nova resposta
        
        try:
            # GARANTE: Envio do áudio em chunks otimizados
            chunk_size = 32768  # 32KB chunks para estabilidade
            total_chunks = (len(base64_audio) + chunk_size - 1) // chunk_size
            
            logging.info(f"📤 Enviando áudio em {total_chunks} chunks")
            
            for i in range(0, len(base64_audio), chunk_size):
                chunk = base64_audio[i:i + chunk_size]
                
                # GARANTE: Formato exato do evento
                audio_event = {
                    "type": "input_audio_buffer.append",
                    "audio": chunk
                }
                
                await self.ws.send(json.dumps(audio_event))
                
                # Micro delay para evitar overload
                await asyncio.sleep(0.01)
            
            # GARANTE: Confirma processamento do áudio
            commit_event = {
                "type": "input_audio_buffer.commit"
            }
            await self.ws.send(json.dumps(commit_event))
            
            # GARANTE: Solicita resposta
            response_event = {
                "type": "response.create"
            }
            await self.ws.send(json.dumps(response_event))
            
            logging.info("✅ Áudio enviado para Realtime API - aguardando resposta")
            
        except Exception as e:
            logging.error(f"❌ Erro enviando áudio para Realtime: {e}")
            raise
    
    async def listen_to_server_events(self):
        """Escuta eventos do servidor Realtime API"""
        try:
            if self.ws:
                async for message in self.ws:
                    event = json.loads(message)
                    await self.handle_server_event(event)
        except Exception as e:
            logging.error(f"Erro listening eventos: {e}")
    
    async def handle_server_event(self, event: Dict[str, Any]):
        """
        GARANTE processamento correto dos eventos do servidor
        Implementa exatamente o fluxo do código JavaScript
        """
        event_type = event.get("type")
        
        if event_type == "response.audio.delta":
            # GARANTE: Captura chunks de áudio da resposta
            delta = event.get("delta", "")
            if delta:
                self.audio_chunks.append(delta)
                logging.debug(f"🔊 Chunk áudio recebido: {len(delta)} chars")
            
        elif event_type == "response.done":
            # GARANTE: Resposta completa - envia para WhatsApp
            logging.info(f"✅ Resposta completa: {len(self.audio_chunks)} chunks")
            await self.send_response_to_whatsapp()
            
        elif event_type == "error":
            error_msg = event.get("error", {}).get("message", "Erro desconhecido")
            logging.error(f"❌ Erro Realtime API: {error_msg}")
            
            # Fallback: envia resposta de erro via texto se necessário
            if self.current_user:
                await self.send_error_fallback()
                
        elif event_type == "response.text.done":
            # Log da transcrição para debug
            text = event.get("text", "")
            logging.info(f"📝 Transcrição: {text[:150]}...")
            
        elif event_type == "session.created":
            logging.info("🔗 Sessão Realtime criada")
            
        elif event_type == "session.updated":
            logging.info("⚙️ Configuração de sessão atualizada")
            
        elif event_type == "input_audio_buffer.committed":
            logging.info("🎤 Áudio confirmado pelo servidor")
            
        elif event_type == "response.created":
            logging.info("🤖 Gerando resposta...")
            
        elif event_type == "response.output_item.added":
            logging.info("📋 Item de resposta adicionado")
            
        else:
            logging.debug(f"🔍 Evento: {event_type}")
    
    async def send_error_fallback(self):
        """Envia resposta de fallback em caso de erro"""
        try:
            error_message = "Desculpe, houve um problema técnico. Pode repetir por favor?"
            
            await asyncio.to_thread(
                self.twilio_client.messages.create,
                from_=f'whatsapp:{self.twilio_phone}',
                to=f'whatsapp:{self.current_user}',
                body=error_message
            )
            
            logging.info("📤 Mensagem de erro enviada")
            
        except Exception as e:
            logging.error(f"Erro enviando fallback: {e}")
    
    async def send_response_to_whatsapp(self):
        """Envia resposta de áudio de volta para WhatsApp"""
        try:
            if not self.audio_chunks:
                logging.warning("Nenhum chunk de áudio para enviar")
                return
            
            logging.info(f"🔊 Enviando {len(self.audio_chunks)} chunks de áudio")
            
            # 1. Combina chunks de áudio
            complete_audio = b''.join([
                base64.b64decode(chunk) for chunk in self.audio_chunks if chunk
            ])
            
            if not complete_audio:
                logging.warning("Áudio combinado está vazio")
                return
            
            # 2. Converte para formato WhatsApp (OGG)
            ogg_audio = await self.convert_to_whatsapp_format(complete_audio)
            
            # 3. Salva e serve via HTTP
            audio_url = await self.serve_audio_file(ogg_audio)
            
            # 4. Envia via Twilio
            await self.send_via_twilio(audio_url)
            
            # 5. Reset para próxima mensagem
            self.audio_chunks = []
            
            logging.info("✅ Resposta de áudio enviada!")
            
        except Exception as e:
            logging.error(f"❌ Erro enviando resposta: {e}")
            self.audio_chunks = []  # Reset mesmo com erro
    
    async def convert_to_whatsapp_format(self, pcm_audio: bytes) -> bytes:
        """
        GARANTE conversão Realtime API → WhatsApp
        PCM 24kHz → OGG Opus (formato WhatsApp compatível)
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.raw') as input_file:
            input_file.write(pcm_audio)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as output_file:
            output_path = output_file.name
        
        try:
            # GARANTE conversão exata: PCM 24kHz → OGG Opus WhatsApp
            cmd = [
                'ffmpeg',
                '-f', 's16le',              # Input format: signed 16-bit little-endian
                '-ar', '24000',             # GARANTIDO: 24kHz (Realtime API output)
                '-ac', '1',                 # GARANTIDO: Mono channel
                '-i', input_path,           # Input PCM file
                '-c:a', 'libopus',          # GARANTIDO: Opus codec (WhatsApp compatible)
                '-b:a', '64k',              # Bitrate otimizado para WhatsApp
                '-application', 'voip',     # Otimização para voz
                '-frame_duration', '20',    # Frame duration otimizado
                '-y',                       # Overwrite output
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logging.error(f"Erro conversão Realtime→WhatsApp: {result.stderr}")
                raise Exception(f"Falha na conversão para WhatsApp: {result.stderr}")
            
            # Lê áudio convertido
            with open(output_path, 'rb') as f:
                ogg_data = f.read()
            
            logging.info(f"✅ Áudio convertido: {len(pcm_audio)} bytes PCM → {len(ogg_data)} bytes OGG")
            return ogg_data
            
        except subprocess.TimeoutExpired:
            logging.error("Timeout na conversão para WhatsApp")
            raise Exception("Timeout na conversão para WhatsApp")
            
        finally:
            # Cleanup garantido
            for temp_file in [input_path, output_path]:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    async def serve_audio_file(self, audio_data: bytes) -> str:
        """Salva áudio e retorna URL público"""
        import uuid
        
        # Cria nome único
        filename = f"realtime_audio_{uuid.uuid4().hex[:8]}.ogg"
        
        # Salva na pasta static
        static_dir = "static/audio"
        os.makedirs(static_dir, exist_ok=True)
        
        file_path = os.path.join(static_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        
        # Retorna URL público
        base_url = os.environ.get('REPLIT_URL', 'https://6771fe47-1a6d-4a14-a791-ac9ee41dd82d-00-ys74xr6dg9hv.worf.replit.dev')
        return f"{base_url}/static/audio/{filename}"
    
    async def send_via_twilio(self, audio_url: str):
        """Envia áudio via Twilio WhatsApp"""
        try:
            # Envia apenas o áudio (sem texto)
            message = await asyncio.to_thread(
                self.twilio_client.messages.create,
                from_=f'whatsapp:{self.twilio_phone}',
                to=f'whatsapp:{self.current_user}',
                media_url=[audio_url]
            )
            
            logging.info(f"📤 Áudio enviado via Twilio: {message.sid}")
            
        except Exception as e:
            logging.error(f"Erro enviando via Twilio: {e}")
            raise
    
    async def close(self):
        """Fecha conexão WebSocket"""
        if self.ws:
            await self.ws.close()
            self.is_connected = False