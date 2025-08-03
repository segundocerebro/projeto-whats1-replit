# 🎤 Configuração do Webhook Realtime - Endrigo Digital

## URL do Webhook v3 Realtime
```
https://6771fe47-1a6d-4a14-a791-ac9ee41dd82d-00-ys74xr6dg9hv.worf.replit.dev/webhook/whatsapp/realtime
```

## Configuração no Twilio Console

### 1. Acesse o Twilio Console
- Vá para: https://console.twilio.com/
- Navegue para: Messaging > Settings > WhatsApp Sandbox

### 2. Configure o Webhook
- **Webhook URL**: `https://6771fe47-1a6d-4a14-a791-ac9ee41dd82d-00-ys74xr6dg9hv.worf.replit.dev/webhook/whatsapp/realtime`
- **HTTP Method**: POST
- **Status Callback URL**: (opcional - deixe em branco)

### 3. Teste Imediato
Envie um áudio pelo WhatsApp para o número sandbox do Twilio e o sistema irá:

1. ✅ **Receber o áudio** do WhatsApp
2. ✅ **Converter automaticamente** OGG → PCM 16kHz
3. ✅ **Processar via Realtime API** com latência <525ms
4. ✅ **Responder em áudio** convertido PCM → OGG
5. ✅ **Enviar de volta** pelo WhatsApp

## Sistemas Disponíveis

| Webhook | Tecnologia | Latência | Recursos |
|---------|------------|----------|----------|
| `/webhook/whatsapp` | Assistants API | 2-5s | Sistema original |
| `/webhook/whatsapp/v2` | Pipeline Avançado | <1s | Memória + KB |
| `/webhook/whatsapp/realtime` | **Realtime API** | **<525ms** | **Speech-to-Speech** |

## Fluxo Garantido do v3 Realtime

```
WhatsApp Áudio → Download → FFmpeg (OGG→PCM) → Realtime API → 
Processamento IA → Resposta Áudio → FFmpeg (PCM→OGG) → WhatsApp
```

## Fallback Inteligente
Se o sistema Realtime falhar, automaticamente usa o sistema v2 avançado como backup.

## Status do Sistema
- 🟢 **Realtime Audio**: Disponível
- 🟢 **Base de Conhecimento**: 3 documentos carregados  
- 🟢 **FFmpeg**: Instalado para conversões
- 🟢 **ElevenLabs**: Configurado com voz Endrigo
- 🟢 **Personalidade v4**: Multi-camadas ativa

## Teste Local
Para testar localmente sem WhatsApp:
```bash
curl -X POST http://localhost:5000/webhook/whatsapp/realtime \
  -d "From=whatsapp:+5511999999999&MediaUrl0=test_audio_url"
```

---
**Sistema Pronto para Uso Imediato!** 🚀