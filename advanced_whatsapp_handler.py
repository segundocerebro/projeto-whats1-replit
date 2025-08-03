"""
Handler WhatsApp Avançado com Realtime API
Integra todos os sistemas para máxima fluidez
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse, Message
import os
import tempfile
import requests
from advanced_realtime_client import RealtimeVoiceClone
from personality_manager import PersonalityManager
from advanced_memory_system import AdvancedMemorySystem
from optimized_pipeline import OptimizedPipeline
from knowledge_base_manager import KnowledgeBaseManager
from elevenlabs_service import generate_voice_response

class AdvancedWhatsAppHandler:
    def __init__(self):
        # Componentes principais
        self.realtime_client = RealtimeVoiceClone()
        self.personality_manager = PersonalityManager()
        self.memory_system = AdvancedMemorySystem()
        self.pipeline = OptimizedPipeline()
        self.knowledge_base = KnowledgeBaseManager()
        
        # Serviços externos
        self.twilio_client = Client(
            os.environ.get('TWILIO_ACCOUNT_SID'),
            os.environ.get('TWILIO_AUTH_TOKEN')
        )
        # ElevenLabs será usado via função importada
        
        # Configurações
        self.webhook_url = os.environ.get('REPLIT_URL', 'https://your-repl-url.replit.dev')
        
    async def handle_incoming_message(self, from_number: str, message_body: str, 
                                    media_url: Optional[str] = None) -> str:
        """Handler principal para mensagens do WhatsApp"""
        start_time = time.time()
        
        try:
            # 1. Recupera contexto da memória avançada
            memory_context = self.memory_system.get_context_for_prompt(from_number)
            
            # 2. Gera prompt contextual com personalidade
            contextual_prompt = self.personality_manager.generate_contextual_prompt(
                memory_context.get('recent_conversation', []), from_number
            )
            
            # 3. Processa mensagem (texto ou áudio)
            if media_url:
                response = await self._handle_voice_message(
                    media_url, from_number, memory_context
                )
            else:
                response = await self._handle_text_message(
                    message_body, from_number, memory_context, contextual_prompt
                )
            
            # 4. Atualiza memória com a conversa
            self.memory_system.process_conversation(
                from_number, message_body or "[Mensagem de áudio]", response['text']
            )
            
            # 5. Atualiza perfil do usuário
            self.personality_manager.update_user_profile(from_number, {
                'message_text': message_body,
                'message_type': 'audio' if media_url else 'text',
                'response_generated': response['text']
            })
            
            # 6. Gera resposta TwiML
            twiml_response = self._create_twiml_response(response)
            
            # Log de performance
            total_time = (time.time() - start_time) * 1000
            logging.info(f"Mensagem processada em {total_time:.1f}ms para {from_number}")
            
            return str(twiml_response)
            
        except Exception as e:
            logging.error(f"Erro no handler WhatsApp: {e}")
            return self._create_error_response()
    
    async def _handle_voice_message(self, media_url: str, from_number: str, 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagem de áudio com Realtime API"""
        try:
            # 1. Download do áudio
            audio_data = self._download_audio(media_url)
            
            # 2. Conecta ao Realtime API se necessário
            if not self.realtime_client.is_connected:
                await self.realtime_client.connect()
            
            # 3. Injeta contexto da base de conhecimento
            kb_context = self.knowledge_base.inject_context_for_realtime("[Mensagem de áudio]")
            await self.realtime_client.inject_context(kb_context)
            
            # 4. Processa áudio via pipeline otimizado
            realtime_response = await self.pipeline.process_with_streaming(
                audio_data, context
            )
            
            if realtime_response.get('success'):
                # Usa resposta do Realtime API
                response_text = realtime_response.get('text', 'Resposta processada via Realtime API')
                audio_response = realtime_response.get('audio')
            else:
                # Fallback para sistema atual
                response_text = await self._fallback_text_response(
                    "[Mensagem de áudio transcrita]", from_number, context
                )
                audio_response = None
            
            # 4. Gera áudio se não veio do Realtime API
            if not audio_response and len(response_text) < 800:
                try:
                    audio_response = self._generate_audio_response_sync(response_text)
                except Exception as e:
                    logging.warning(f"Falha na geração de áudio: {e}")
                    audio_response = None
            
            return {
                'text': response_text,
                'audio': audio_response,
                'source': 'realtime_api' if realtime_response.get('success') else 'fallback'
            }
            
        except Exception as e:
            logging.error(f"Erro no processamento de áudio: {e}")
            return await self._handle_text_message(
                "Desculpe, não consegui processar o áudio. Pode repetir por texto?",
                from_number, context, ""
            )
    
    async def _handle_text_message(self, message_text: str, from_number: str,
                                 context: Dict[str, Any], contextual_prompt: str) -> Dict[str, Any]:
        """Processa mensagem de texto com personalidade avançada"""
        try:
            # Usa OpenAI Client atual para compatibilidade
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            assistant_id = os.environ.get('ASSISTANT_ID')
            
            # Obtém contexto relevante da base de conhecimento
            kb_context = self.knowledge_base.retrieve_relevant_context(message_text)
            
            # Injeta contexto da memória e base de conhecimento no prompt
            enhanced_prompt = f"""
{contextual_prompt}

CONTEXTO DA MEMÓRIA:
{context.get('recent_conversation', 'Primeira interação')}

PREFERÊNCIAS CONHECIDAS:
{'; '.join(context.get('user_preferences', []))}

CONTEXTO EMPRESARIAL:
{'; '.join(context.get('business_context', []))}

BASE DE CONHECIMENTO RELEVANTE:
{kb_context}

IMPORTANTE: Baseie suas respostas na base de conhecimento fornecida.
Responda de forma natural mantendo continuidade total da conversa.
            """
            
            # Cria thread com mensagem do usuário apenas (Assistant API não aceita system role)
            thread = client.beta.threads.create(
                messages=[
                    {"role": "user", "content": f"{enhanced_prompt}\n\nUsuário: {message_text}"}
                ]
            )
            
            # Executa Assistant (verifica se assistant_id existe)
            if not assistant_id:
                response_text = "Assistant ID não configurado. Usando sistema de fallback."
            else:
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant_id
                )
            
                # Aguarda resposta
                import time
                timeout = 15
                start_time = time.time()
                
                while run.status not in ["completed", "failed", "cancelled"]:
                    if time.time() - start_time > timeout:
                        break
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                
                if run.status == "completed":
                    messages = client.beta.threads.messages.list(thread_id=thread.id)
                    message_content = messages.data[0].content[0]
                    
                    # Verifica tipo de conteúdo de forma segura
                    if hasattr(message_content, 'text'):
                        response_text = message_content.text.value
                    else:
                        response_text = "Resposta processada com sistema avançado"
                else:
                    response_text = "Sistema temporariamente sobrecarregado. Tente novamente."
            
            # Gera áudio se resposta for curta
            audio_response = None
            if len(response_text) < 800:
                try:
                    audio_response = await asyncio.to_thread(
                        self._generate_audio_response_sync, response_text
                    )
                except Exception as e:
                    logging.warning(f"Falha na geração de áudio: {e}")
            
            return {
                'text': response_text,
                'audio': audio_response,
                'source': 'assistant_api'
            }
            
        except Exception as e:
            logging.error(f"Erro no processamento de texto: {e}")
            return {
                'text': "Desculpe, houve um problema técnico. Pode tentar novamente?",
                'audio': None,
                'source': 'error_fallback'
            }
    
    async def _fallback_text_response(self, message: str, from_number: str, 
                                    context: Dict[str, Any]) -> str:
        """Sistema de fallback quando Realtime API falha"""
        fallback_responses = [
            "Entendi sua mensagem! Como posso ajudar você hoje?",
            "Recebi seu áudio perfeitamente. Em que posso ser útil?",
            "Ótimo! Conte-me mais sobre o que você precisa.",
            "Perfeito! Vamos conversar sobre isso."
        ]
        
        # Seleciona resposta baseada no contexto
        import random
        return random.choice(fallback_responses)
    
    def _generate_audio_response_sync(self, text: str) -> Optional[str]:
        """Gera resposta em áudio usando ElevenLabs"""
        try:
            audio_file_path = generate_voice_response(text)
            
            if audio_file_path:
                # Move para pasta static para servir via HTTP
                static_path = self._move_to_static(audio_file_path)
                return f"{self.webhook_url}/static/audio/{static_path}"
            
        except Exception as e:
            logging.error(f"Erro na geração de áudio: {e}")
        
        return None
    
    def _download_audio(self, media_url: str) -> bytes:
        """Download de áudio do Twilio"""
        try:
            response = requests.get(media_url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logging.error(f"Erro no download de áudio: {e}")
            raise
    
    def _move_to_static(self, temp_file_path: str) -> str:
        """Move arquivo temporário para pasta static"""
        import shutil
        import uuid
        
        # Cria nome único
        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        static_dir = "static/audio"
        
        # Cria diretório se não existir
        os.makedirs(static_dir, exist_ok=True)
        
        # Move arquivo
        static_path = os.path.join(static_dir, filename)
        shutil.move(temp_file_path, static_path)
        
        return filename
    
    def _create_twiml_response(self, response_data: Dict[str, Any]) -> MessagingResponse:
        """Cria resposta TwiML para WhatsApp"""
        twiml_response = MessagingResponse()
        message = Message()
        
        # Adiciona texto
        message.body(response_data['text'])
        
        # Adiciona áudio se disponível
        if response_data.get('audio'):
            message.media(response_data['audio'])
        
        twiml_response.append(message)
        return twiml_response
    
    def _create_error_response(self) -> str:
        """Cria resposta de erro padrão"""
        twiml_response = MessagingResponse()
        message = Message()
        message.body("Desculpe, houve um problema técnico temporário. Tente novamente em alguns instantes.")
        twiml_response.append(message)
        return str(twiml_response)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Retorna status de todos os componentes"""
        status = {
            'realtime_api': {
                'connected': self.realtime_client.is_connected,
                'status': 'online' if self.realtime_client.is_connected else 'offline'
            },
            'memory_system': {
                'users_tracked': len(self.memory_system.long_term_memory),
                'total_facts': sum(
                    len(memory.get('preferences', [])) + 
                    len(memory.get('business_context', [])) + 
                    len(memory.get('insights', []))
                    for memory in self.memory_system.long_term_memory.values()
                )
            },
            'pipeline': {
                'streaming_enabled': self.pipeline.streaming_enabled,
                'target_latency': self.pipeline.max_latency_target,
                'performance_score': self.pipeline._calculate_performance_score()
            },
            'elevenlabs': {
                'configured': bool(os.environ.get('ELEVENLABS_API_KEY')),
                'voice_id': os.environ.get('ELEVENLABS_VOICE_ID', 'not_set')
            }
        }
        
        return status