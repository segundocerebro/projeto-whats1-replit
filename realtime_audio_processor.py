#!/usr/bin/env python3
"""
Processador Real de Áudio via OpenAI Realtime API
Implementa o fluxo completo: WhatsApp áudio → Realtime API → resposta em áudio
"""
import asyncio
import websockets
import json
import logging
import base64
import tempfile
import subprocess
import os
import requests
from typing import Optional, Dict, Any

class RealtimeAudioProcessor:
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.websocket = None
        self.is_connected = False
        self.session_id = None
        
    async def connect(self):
        """Conecta ao OpenAI Realtime API via WebSocket"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
            
            # Fix para websockets - usar headers corretos
            self.websocket = await websockets.connect(
                uri, 
                additional_headers=headers
            )
            self.is_connected = True
            
            # Configura sessão
            await self._configure_session()
            
            logging.info("🎤 Conectado ao OpenAI Realtime API")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao conectar Realtime API: {e}")
            self.is_connected = False
            return False
    
    async def _configure_session(self):
        """Configura a sessão do Realtime API"""
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": """Você é Endrigo Almada, especialista em marketing digital com 22 anos de experiência.
                Responda de forma natural, amigável e profissional em português brasileiro.
                Mantenha conversas fluidas e focadas em ajudar com marketing digital e IA.""",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                },
                "tools": [],
                "tool_choice": "auto",
                "temperature": 0.8,
                "max_response_output_tokens": 4096
            }
        }
        
        await self.websocket.send(json.dumps(config))
        logging.info("Sessão Realtime configurada")
    
    def download_and_convert_audio(self, media_url: str) -> Optional[bytes]:
        """Baixa áudio do WhatsApp e converte para PCM 16kHz"""
        try:
            # Download do áudio
            response = requests.get(media_url, timeout=10)
            if response.status_code != 200:
                return None
            
            # Salva temporariamente
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_input:
                temp_input.write(response.content)
                input_path = temp_input.name
            
            # Converte para PCM 16kHz mono
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_output:
                output_path = temp_output.name
            
            # FFmpeg: WhatsApp OGG → PCM 16kHz
            cmd = [
                'ffmpeg', '-i', input_path,
                '-ar', '24000',  # 24kHz como esperado pelo Realtime API
                '-ac', '1',      # Mono
                '-f', 'wav',     # Formato WAV
                '-y',            # Sobrescrever
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Lê o áudio convertido
                with open(output_path, 'rb') as f:
                    # Pula o header WAV (44 bytes) para obter PCM puro
                    f.seek(44)
                    pcm_data = f.read()
                
                # Limpa arquivos temporários
                os.unlink(input_path)
                os.unlink(output_path)
                
                logging.info(f"Áudio convertido: {len(pcm_data)} bytes PCM")
                return pcm_data
            else:
                logging.error(f"Erro FFmpeg: {result.stderr}")
                return None
                
        except Exception as e:
            logging.error(f"Erro ao processar áudio: {e}")
            return None
    
    async def process_audio_message(self, media_url: str, from_number: str) -> Dict[str, Any]:
        """Processa mensagem de áudio via Realtime API"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # 1. Baixa e converte o áudio
            pcm_audio = self.download_and_convert_audio(media_url)
            if not pcm_audio:
                return {"success": False, "error": "Falha ao processar áudio"}
            
            # 2. Envia áudio para Realtime API
            audio_b64 = base64.b64encode(pcm_audio).decode('utf-8')
            
            append_message = {
                "type": "input_audio_buffer.append",
                "audio": audio_b64
            }
            
            await self.websocket.send(json.dumps(append_message))
            
            # 3. Committa o áudio
            commit_message = {
                "type": "input_audio_buffer.commit"
            }
            
            await self.websocket.send(json.dumps(commit_message))
            
            # 4. Solicita resposta
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": "Responda de forma natural em português brasileiro."
                }
            }
            
            await self.websocket.send(json.dumps(response_create))
            
            # 5. Aguarda resposta
            response_text = ""
            response_audio = b""
            
            timeout = 15
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    
                    if data.get("type") == "response.text.delta":
                        response_text += data.get("delta", "")
                    
                    elif data.get("type") == "response.audio.delta":
                        audio_delta = data.get("delta", "")
                        if audio_delta:
                            response_audio += base64.b64decode(audio_delta)
                    
                    elif data.get("type") == "response.done":
                        break
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logging.error(f"Erro ao receber mensagem: {e}")
                    break
            
            # 6. Converte áudio de resposta para formato WhatsApp
            audio_file = None
            if response_audio:
                audio_file = self._convert_response_audio(response_audio)
            
            return {
                "success": True,
                "text": response_text or "Resposta processada via Realtime API",
                "audio_file": audio_file,
                "source": "realtime_api"
            }
            
        except Exception as e:
            logging.error(f"Erro no processamento Realtime: {e}")
            return {"success": False, "error": str(e)}
    
    def _convert_response_audio(self, pcm_audio: bytes) -> Optional[str]:
        """Converte PCM de resposta para MP3 para WhatsApp"""
        try:
            # Salva PCM temporariamente
            with tempfile.NamedTemporaryFile(suffix='.pcm', delete=False) as temp_pcm:
                temp_pcm.write(pcm_audio)
                pcm_path = temp_pcm.name
            
            # Converte para MP3
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
                mp3_path = temp_mp3.name
            
            # FFmpeg: PCM 24kHz → MP3
            cmd = [
                'ffmpeg', '-f', 's16le',  # PCM 16-bit little endian
                '-ar', '24000',           # 24kHz
                '-ac', '1',               # Mono
                '-i', pcm_path,
                '-codec:a', 'mp3',
                '-b:a', '128k',
                '-y',
                mp3_path
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                # Limpa PCM temporário
                os.unlink(pcm_path)
                logging.info(f"Áudio de resposta convertido: {mp3_path}")
                return mp3_path
            else:
                logging.error(f"Erro na conversão de resposta: {result.stderr}")
                return None
                
        except Exception as e:
            logging.error(f"Erro ao converter resposta de áudio: {e}")
            return None
    
    async def disconnect(self):
        """Desconecta do Realtime API"""
        if self.websocket and self.is_connected:
            await self.websocket.close()
            self.is_connected = False
            logging.info("Desconectado do Realtime API")

# Instância global
realtime_processor = RealtimeAudioProcessor()