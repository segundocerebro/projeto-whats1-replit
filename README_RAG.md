# Clone Digital Fluido do Endrigo com Integração RAG

Sistema avançado de clone digital conversacional do Endrigo Almada, fundador do maior ecossistema publicitário do interior de SP, com 22 anos de expertise em marketing, inovação e IA.

## 🚀 Funcionalidades Principais

### Speech-to-Speech Realtime API
- **OpenAI Realtime API**: WebSocket direto para latência <800ms
- **Voice Activity Detection**: Detecção automática de início/fim de fala
- **Processamento streaming**: Pipeline otimizado para máxima naturalidade
- **Fallback inteligente**: Sistema degrada graciosamente

### Sistema RAG Integrado
- **Knowledge Base**: Acesso inteligente a arquivos PDF (biografia, cases)
- **Contextualização**: Respostas personalizadas baseadas na experiência real
- **Busca semântica**: Extração de trechos relevantes para cada conversa
- **Exemplos práticos**: "Como diretor do Bandeirante, aumentei engajamento em 25%"

### Personalidade Multi-Camadas v4
- **Identidade central**: Fundador em Birigui, SP
- **Estilo conversacional**: Brasileiro caloroso e profissional
- **Memória contextual**: Histórico completo de conversas
- **Expertise real**: Marketing esportivo, IA, imobiliário, agronegócio

## 🎯 Diferenciais Tecnológicos

### Migração da Assistants API para Realtime API
- WebSocket persistente com OpenAI
- Processamento direto de áudio sem transcrição intermediária
- Resposta em tempo real com voz clonada do Endrigo
- Sistema híbrido para máxima confiabilidade

### Pipeline Otimizado
1. **Recepção**: WhatsApp → Twilio → Flask webhook
2. **Processamento**: Download seguro → Realtime API → Resposta áudio
3. **RAG**: Busca contexto relevante em documentos
4. **Personalização**: Injeta experiência real nas respostas
5. **Entrega**: Áudio + texto com voz clonada ElevenLabs

## 🔧 Configuração Técnica

### Dependências Instaladas
```bash
flask twilio openai flask_sqlalchemy requests werkzeug 
websocket-client pdfplumber numpy
```

### Estrutura de Pastas
```
/documents/          # PDFs como bio_endrigo.pdf
/static/audio/       # Áudios gerados
/templates/          # Interface web
```

### Variáveis de Ambiente
```bash
OPENAI_API_KEY=sk-...          # OpenAI API key
TWILIO_ACCOUNT_SID=AC...       # Twilio credentials  
TWILIO_AUTH_TOKEN=...          # Twilio auth
ELEVENLABS_API_KEY=...         # ElevenLabs key
ELEVENLABS_VOICE_ID=SuM1a4...  # Voz clonada Endrigo
DATABASE_URL=postgresql://...   # PostgreSQL Neon
SESSION_SECRET=...             # Flask secret
```

## 📱 Webhooks Disponíveis

### Sistema Realtime (Recomendado)
```
URL: https://endrigo-digital.replit.app/webhook/whatsapp
Method: POST
```

### Sistemas Alternativos
- `/webhook/whatsapp/v2` - Sistema avançado híbrido
- `/webhook/FUNCIONA` - Sistema garantido rápido

## 🎨 Funcionamento RAG

### Busca Contextual
```python
# Para pergunta: "Experiência com marketing esportivo?"
# RAG busca: "Bandeirante Esporte Clube", "diretor de marketing"
# Resposta: Contextualizada com case real de aumento de 25% engajamento
```

### Personalização Automática
- Detecta intenções comerciais
- Puxa cases relevantes da biografia
- Sugere soluções baseadas na experiência real
- Mantém tom caloroso e profissional

## 🚀 Deploy e Teste

### 1. Configure Arquivo Bio
Coloque `bio_endrigo.pdf` na pasta `/documents/` com:
- Experiência no Bandeirante Esporte Clube
- Cases de marketing digital
- Expertise em IA e automação
- Histórico profissional completo

### 2. Configure Webhook Twilio
```
Webhook URL: https://endrigo-digital.replit.app/webhook/whatsapp
HTTP Method: POST
```

### 3. Teste o Sistema
- Envie áudio: Processamento via Realtime API
- Envie texto sobre marketing: Resposta com contexto da bio
- Pergunte sobre futebol: Case do Bandeirante automaticamente

## 📊 Monitoramento

### Endpoints de Status
- `/health` - Health check completo
- `/stats` - Estatísticas de uso
- `/system/realtime-status` - Status Realtime API
- `/` - Dashboard principal

### Logs Detalhados
- Processamento Realtime API
- Download e conversão de áudio
- Busca RAG em documentos
- Fallbacks automáticos

---

**Clone Digital Fluido** - Endrigo Almada | Birigui, SP  
*Sistema baseado em experiência real de 22 anos em marketing e inovação*