# Como Configurar Webhook no Twilio - Guia Passo a Passo

## 🎯 URLs dos Webhooks Disponíveis

Após o deploy no Replit, você tem estas opções:

### Para Sistema Completo (RAG + Áudio):
```
https://endrigo-digital.replit.app/webhook/whatsapp/realtime
```

### Para Sistema Híbrido (RAG apenas):
```
https://endrigo-digital.replit.app/webhook/whatsapp
```

## 📱 Passos para Configurar no Twilio Console

### 1. Acesse o Twilio Console
- Entre em: https://console.twilio.com
- Faça login com sua conta

### 2. Navegue para WhatsApp Sandbox
- No menu lateral esquerdo, clique em "Messaging"
- Depois clique em "Try it out" 
- Selecione "Send a WhatsApp message"

### 3. Configure o Webhook
- Na seção "Sandbox Configuration"
- Encontre o campo "When a message comes in"
- **COLE A URL:** `https://endrigo-digital.replit.app/webhook/whatsapp/realtime`
- Método HTTP: **POST**
- Clique em "Save Configuration"

### 4. Para Produção (WhatsApp Business)
Se você tem WhatsApp Business aprovado:
- Vá em "Messaging" → "Senders" → "WhatsApp senders"
- Clique no seu número aprovado
- Na seção "Webhook", configure:
  - **URL:** `https://endrigo-digital.replit.app/webhook/whatsapp/realtime`
  - **Método:** POST
  - Salve as alterações

## ✅ Teste da Configuração

Após configurar, teste enviando:

1. **Mensagem de texto:** "me conte sobre o Bandeirante"
   - Deve retornar informações sobre o clube com RAG

2. **Mensagem de áudio:** Grave um áudio curto
   - Deve processar via OpenAI Realtime API

## 🔧 Solução de Problemas

### Se não funcionar:
1. Verifique se a URL está correta (sem barras extras)
2. Confirme que o método é POST
3. Teste a URL diretamente no navegador - deve retornar:
   ```
   🎯 Clone Digital Realtime API - Speech-to-Speech Ativo! ✅
   ```

### URLs para Verificação:
- Status: `https://endrigo-digital.replit.app/upgrade-webhook`
- Saúde: `https://endrigo-digital.replit.app/health`

## 📋 Resumo das URLs

| Funcionalidade | URL | Recomendado |
|---|---|---|
| **Sistema Completo** | `/webhook/whatsapp/realtime` | ✅ SIM |
| Sistema Híbrido | `/webhook/whatsapp` | - |
| Status dos Webhooks | `/upgrade-webhook` | Para verificação |

**Use a URL completa:** `https://endrigo-digital.replit.app/webhook/whatsapp/realtime`