# Clone Digital Fluido – Endrigo Almada Realtime API

## Descrição Geral

Este projeto implementa um clone digital conversacional avançado, idealizado por Endrigo Almada, fundador do maior ecossistema publicitário do interior de SP, com 22 anos de expertise no setor. O objetivo é criar uma experiência ultra fluida, que compreende e responde mensagens de áudio e texto recebidas via WhatsApp de clientes, usando a personalidade, tom e expertise de Endrigo, em voz clonada. Tudo isso com altíssima naturalidade, latência ultra-baixa e integração de IA de última geração.

## O que este sistema faz

- **Recebe automaticamente** mensagens de texto e áudio do WhatsApp via Twilio
- **Se for áudio:** Convoca a OpenAI Realtime API (gpt-4o-realtime), que transcreve, compreende e responde em áudio, usando voz clonada do Endrigo, com latência inferior a 1 segundo
- **Se for texto:** Gera resposta textual amigável pelo ChatGPT, mantendo identidade, expertise e personalidade
- **Entrega sempre respostas em áudio** (voz própria), tornando o contato indistinguível de um humano de verdade no WhatsApp
- **Gerencia contexto e memória**, analisando histórico do usuário, para respostas personalizadas e aderentes aos desafios dos clientes e parceiros

## Diferenciais do Sistema

- **Migração total da Assistants API para OpenAI Realtime API:** garante respostas speech-to-speech em tempo real, essencial para suporte humano via voz
- **Personalidade multi-camadas (v4):** comportamento programado para refletir identidade do Endrigo, especialista em marketing digital, IA, negócios imobiliários e inovação, usando linguagem próxima, calorosa e técnica ao mesmo tempo
- **Pipeline otimizado para Replit:** suporta limites da plataforma, limpeza de arquivos, logging claro, performance estável
- **Pronto para expansão:** arquitetura modular, permitindo integrar CRM, leads, análises comportamentais e outros serviços do ecossistema Almada

## Como funciona (passo a passo)

1. **Usuário envia mensagem** de áudio ou texto pelo WhatsApp, que chega ao webhook do Flask hospedado no Replit
2. **O sistema identifica** se a mensagem é áudio ou texto
3. **Para áudio:**
   - Baixa o arquivo de mídia do Twilio (com autenticação robusta)
   - Envia para a OpenAI Realtime API no formato PCM
   - Recebe resposta em áudio, já processada com personalidade, contexto e voz de Endrigo
   - Gera URL acessível e envia de volta ao WhatsApp via Twilio
4. **Para texto:**
   - Passa o prompt multi-camadas personalizado para o modelo GPT-4o
   - Retorna mensagem escrita e, sempre que possível, também áudio da resposta via ElevenLabs (se disponível)
5. **Armazena registros** de conversas e uso em banco de dados SQL, para insights futuros e evoluções de contexto
6. **Log robusto** em todos os passos, facilitando debug e melhoria contínua

## Requisitos & Deploy

### Variables/Replit Secrets:
- `OPENAI_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`

### Dependências no requirements.txt:
- `flask`
- `twilio`
- `openai`
- `flask_sqlalchemy`
- `requests`
- `werkzeug`
- `websocket-client`
- `ffmpeg-python`

### Assets:
- Pasta `/static/audio` para entrega dos áudios públicos

### Webhook Twilio:
- Aponte para `/webhook/whatsapp` (texto e áudio fluido)

### Rodar:
- Execute como serviço Flask padrão no Replit

## URLs do Sistema

- **Dashboard:** https://endrigo-digital.replit.app
- **Webhook Principal:** https://endrigo-digital.replit.app/webhook/whatsapp
- **Health Check:** https://endrigo-digital.replit.app/health

## Observações

- **Nunca negue capacidade de enviar áudio:** todas as respostas devem ser possíveis em áudio, mantendo consistência e identidade
- **Prompt, memória, voz e contexto** devem ser sempre otimizados para refletir expertise e valores do ecossistema Almada
- **Sistema pronto para automação** e integração futura (terceiro setor, Instituto Almada, CRM, etc)

## Arquitetura Técnica

### WebSocket Realtime API
- Conexão persistente com OpenAI Realtime API
- Speech-to-Speech direto sem conversões intermediárias
- Voice Activity Detection automática
- Latência <800ms garantida

### Personalidade Multi-Camadas v4
- **Identidade:** Endrigo Almada, fundador de ecossistema publicitário
- **Expertise:** Marketing digital, IA, imobiliário, agronegócio
- **Estilo:** Caloroso, profissional, entusiasmado com tecnologia
- **Linguagem:** Natural brasileira, concisa, informativa

### Sistema de Memória
- Contexto histórico de conversas
- Personalização baseada no usuário
- Continuidade entre sessões

---

*Este projeto mantém o padrão elevado e inovador do ecossistema publicitário Almada, garantindo experiência indistinguível de um humano real.*