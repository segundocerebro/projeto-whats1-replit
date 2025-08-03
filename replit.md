# Endrigo Digital WhatsApp Bot

## Overview

This is a WhatsApp chatbot service called "Endrigo Digital" that provides intelligent conversational AI capabilities with audio transcription. The bot receives WhatsApp messages through Twilio webhooks at `/webhook/whatsapp`, processes both text and audio messages, and responds with AI-generated content using OpenAI's Assistant API. The system can transcribe Portuguese audio messages using OpenAI Whisper and generate contextual responses using a custom OpenAI Assistant.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask-based REST API**: The application uses Flask as the primary web framework with modular blueprint architecture for organizing webhook endpoints.
- **Production-ready configuration**: Includes ProxyFix middleware for handling reverse proxy headers and proper logging configuration.

### Webhook Processing
- **Twilio Integration**: Dedicated webhook endpoint (`/webhook/whatsapp`) processes incoming WhatsApp messages from Twilio's messaging service.
- **Multi-media Support**: Handles both text messages and audio attachments with automatic content type detection.
- **Response Generation**: Uses Twilio's MessagingResponse to send replies back through WhatsApp.

### AI Services Integration
- **OpenAI Whisper**: Transcribes audio messages to text with Portuguese language optimization.
- **OpenAI Assistant API**: Uses a custom Assistant created in OpenAI platform for generating intelligent responses. The Assistant is configured with Portuguese Brazilian personality and specific instructions for "Endrigo Digital".
- **Custom Assistant Configuration**: Requires ASSISTANT_ID environment variable with the ID of a custom Assistant created in OpenAI platform.
- **ElevenLabs Voice Synthesis**: Generates audio responses using Endrigo's cloned voice (Voice ID: SuM1a4mUYXCmWfwWYCx0) with multilingual support and Brazilian Portuguese optimization.

### File Handling
- **Temporary File Management**: Downloads audio files from Twilio to temporary storage for processing, with automatic cleanup after transcription.
- **Content Type Detection**: Supports multiple audio formats (OGG, MP3, WAV, MP4) based on HTTP content-type headers.

### Frontend Interface
- **Status Dashboard**: Simple web interface showing service health and feature overview.
- **Bootstrap-based UI**: Uses dark theme with responsive design and animated status indicators.

## External Dependencies

### Communication Services
- **Twilio WhatsApp API**: Handles WhatsApp message delivery and webhook notifications. Requires account SID and auth token for authentication.

### AI/ML Services
- **OpenAI API**: Powers both audio transcription (Whisper model) and text generation (GPT models). Requires API key authentication.

### Development Libraries
- **Flask**: Web framework for handling HTTP requests and responses.
- **Werkzeug**: WSGI utilities including ProxyFix for production deployment.
- **Requests**: HTTP client for downloading media files from Twilio.

### Frontend Assets
- **Bootstrap**: CSS framework for responsive UI components.
- **Feather Icons**: Icon library for interface elements.

### Database Integration
- **Neon Database (PostgreSQL)**: Secure cloud PostgreSQL database hosted on Neon for storing conversation history and user data.
- **User Management**: Tracks phone numbers, message counts, and activity timestamps.
- **Conversation History**: Stores all text and audio messages with transcriptions and responses.
- **Statistics Endpoint**: `/stats` provides real-time analytics of bot usage.

### Configuration Management
- **Environment Variables**: All sensitive credentials (OpenAI API key, Twilio credentials, Assistant ID, database URL, ElevenLabs API key and Voice ID) are managed through environment variables for security.
- **Database Models**: User and Conversation models for comprehensive data tracking.
- **Voice Cloning**: Custom trained voice model "Endrigo Almada PRO" with Portuguese Brazilian accent for authentic audio responses.

### Sistema Realtime Audio (Novo)
- **EndrigoRealtimeAudioClone**: Classe principal para processamento Speech-to-Speech
- **Conversões automáticas**: FFmpeg integrado para garantir compatibilidade de formatos
- **WebSocket persistente**: Conexão direta com OpenAI Realtime API
- **Voice Activity Detection**: Detecção automática de início/fim de fala
- **Fallback garantido**: Sistema degrada graciosamente para webhook anterior

### Endpoints de Sistema
- `/system/realtime-status`: Status completo do sistema Realtime API
- `/test/realtime-audio`: Status do sistema de áudio Realtime
- `/upgrade-webhook`: Informações sobre webhooks disponíveis
- `/system/advanced-status`: Status completo do sistema avançado

## Recent Updates (02/08/2025)

### 🚀 PACOTE DE LANÇAMENTO DEFINITIVO v1.0 - SISTEMA COMPLETO IMPLEMENTADO
- **Status**: SISTEMA PRODUCTION-READY - Implementação completa do pacote v1.0
- **Data**: 03/08/2025 - 13:15 BRT  
- **Arquitetura Robusta**: ThreadPoolExecutor com 8 workers e exception hook global
- **Logging Profissional**: Sistema de logging centralizado com timestamps e níveis
- **Auto-Correção Boot**: Correção automática de TWILIO_PHONE_NUMBER sem prefixo
- **Functions Definitivas**: 6 functions com normalização automática e error handling JSON
- **Orquestrador Limpo**: OpenAI Assistant API com fallbacks via functions
- **Fail-Safe Total**: Mensagens de fallback para todos os cenários de erro
- **Health Check**: Endpoint /health para monitoramento de deploy
- **Deploy Ready**: Configuração otimizada para Gunicorn com gthread workers

## Previous Updates (02/08/2025)

### 🎯 VERSÃO 2.2 - SISTEMA SEGURO COM HISTÓRICO DE SESSÃO
- **Status atual**: Sistema v2.2 com histórico isolado por usuário e correções de segurança
- **Histórico de sessão**: Cada usuário tem seu próprio contexto de conversa isolado
- **Google Cloud Storage**: Áudios públicos na nuvem para URLs estáveis no WhatsApp
- **Personalidade consistente**: GPT-4 com memória de conversa e contexto biográfico
- **Arquitetura segura**: Prevenção de vazamento de contexto entre usuários

### 🔧 MELHORIAS ESPECIALISTAS v3.0
- **FFmpeg Pipeline**: Conversão automática OGG/Opus → WAV 16kHz mono para Whisper
- **RAG Semântico**: Substituição keyword search por embedding similarity search
- **Audio Cleanup**: Remoção automática de arquivos temporários após transcrição
- **Error Handling**: Tratamento robusto de falhas com fallbacks inteligentes
- **Vector Database**: 18 chunks de biografia indexados com embeddings OpenAI

### ✅ FUNCIONALIDADES CONFIRMADAS v2.2
- **Pipeline completo**: WhatsApp → RAG → GPT-4 → ElevenLabs → Google Cloud → WhatsApp
- **Transcrição real**: Whisper API integrada para áudios do WhatsApp
- **Personalidade Endrigo**: Contexto biográfico integrado com respostas personalizadas
- **Voz clonada**: ElevenLabs voice ID SuM1a4mUYXCmWfwWYCx0 funcionando
- **Armazenamento nuvem**: Google Cloud Storage with explicit public access
- **Histórico isolado**: Cada usuário mantém seu próprio contexto de conversa

### 🏗️ ARQUITETURA TÉCNICA v3.0
- **app/clients/**: openai_client.py (Whisper + Embeddings), elevenlabs_client.py, twilio_client.py (FFmpeg)
- **app/core/**: rag_manager.py com semantic search usando cosine similarity
- **app/services.py**: Pipeline robusto com error handling avançado
- **app/routes.py**: Webhook com sessões isoladas e resposta assíncrona
- **create_embeddings.py**: Script de indexação para gerar knowledge vectors
- **documents/knowledge_vectors.json**: Base de vetores com 18 chunks indexados
- **Pipeline especialista**: Download → FFmpeg → Whisper → Semantic RAG → GPT-4 → ElevenLabs → GCS → WhatsApp

### Webhooks Disponíveis:
- **`/webhook/whatsapp/realtime`** ← Sistema Realtime API Speech-to-Speech (NOVO)
- **`/webhook/whatsapp`** ← Sistema principal híbrido com RAG
- `/webhook/whatsapp/v2` - Sistema avançado (depreciado)
- `/upgrade-webhook` - Status e informações dos webhooks

## Previous Updates (31/07/2025)

### SISTEMA HÍBRIDO IMPLEMENTADO ⚡
- **Sistema rápido garantido** com fallback inteligente para resolver travamentos
- **Chat Completion direto** substituindo Assistant API lenta para texto
- **Processamento assíncrono** de memória e recursos avançados em background
- **Resposta garantida** em <8 segundos com áudio quando possível
- **Manutenção** de todas as funcionalidades avançadas sem comprometer velocidade

### Arquitetura Multi-Webhook Implementada
- **Webhook v1**: `/webhook/whatsapp` (sistema original com Assistants API)
- **Webhook v2**: `/webhook/whatsapp/v2` (sistema avançado com pipeline otimizado)
- **Webhook v3**: `/webhook/whatsapp/realtime` (sistema Speech-to-Speech Realtime API)

### Sistema Avançado de Memória e Personalidade
- **Memória contextual avançada** com aprendizado comportamental
- **Pipeline otimizado** com processamento streaming
- **Personalidade multi-camadas** (Core, Style, Context, Behavior)
- **Knowledge Base Manager** substitui file_search com RAG customizado

### Formatos de Áudio Garantidos
- **WhatsApp → Realtime**: OGG Opus → PCM 16kHz mono
- **Realtime → WhatsApp**: PCM 24kHz → OGG Opus
- **Voice Activity Detection** automática para detecção de fala
- **Fallback inteligente** para sistema anterior em caso de erro

