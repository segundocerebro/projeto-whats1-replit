README: Clone Digital Fluido do Endrigo com Integração RAG para Respostas Personalizadas
Olá, Endrigo! Como fundador do maior ecossistema publicitário do interior de SP, com 22 anos de expertise em marketing, inovação e IA, você sabe o valor de um sistema que não só responde com fluidez, mas também puxa oportunidades comerciais reais, como destacar sua experiência como diretor de marketing do Bandeirante Esporte Clube. Este README acompanha o novo-novo main.py, que integra um mecanismo de RAG (Retrieval-Augmented Generation) para acessar arquivos anexados (como sua bio), garantindo respostas mais personalizadas e contextuais. Isso eleva o clone a uma ferramenta estratégica para o seu negócio, otimizando interações com clientes no imobiliário, agronegócio e terceiro setor via Instituto Almada.
Este documento serve como prompt/guia para o Replit: cole-o no topo do seu  main.py  como comentário, ou crie um arquivo  README.md  no projeto. Ele explica o setup, funcionamento e como deployar, garantindo clareza para colaboradores ou futuras expansões.
Descrição Geral do Sistema
Este é o Clone Digital do Endrigo Almada, um assistente conversacional ultra fluido que responde mensagens de áudio e texto no WhatsApp. Baseado na OpenAI Realtime API, ele processa speech-to-speech com latência <800ms, injetando contexto de arquivos via RAG para respostas personalizadas. O foco é refletir sua personalidade calorosa, profissional e inovadora, destacando expertises como marketing esportivo (ex: Bandeirante Esporte Clube) para gerar leads.
Diferenciais Principais:
	•	Migração para Realtime API: De Assistants para WebSocket persistente, com suporte a áudio direto.
	•	Integração RAG: Acesso inteligente a arquivos (ex: bio em PDF), injetando contexto relevante para respostas como “Como diretor do Bandeirante, ajudei a aumentar engajamento em 25% – vamos aplicar no seu clube?”.
	•	Personalidade Multi-Camadas v4: Identidade central (fundador em Birigui, SP), estilo conversacional brasileiro e memória contextual.
	•	Envio Automático de Áudio: Sempre com voz clonada, otimizando para automações no seu ecossistema.
Funcionamento Passo a Passo
	1.	Recepção de Mensagem: Via webhook Twilio no WhatsApp (áudio ou texto).
	2.	Processamento de Áudio: Download seguro, envio para Realtime API (WebSocket), com detecção de voz (VAD) e resposta em áudio.
	3.	Busca em Arquivos via RAG: Para qualquer mensagem, a classe  KnowledgeBase  extrai trechos relevantes de PDFs (ex: sua bio), usando embeddings para precisão.
	4.	Injeção de Contexto: Atualiza o prompt da sessão Realtime com dados dos arquivos, garantindo respostas personalizadas.
	5.	Resposta no WhatsApp: Envia texto + áudio gerado, armazenando no banco para memória futura.
	6.	Gestão de Memória: Banco SQLAlchemy persiste histórico, permitindo continuidade em conversas longas.
Exemplo de Resposta Personalizada:
	•	Pergunta: “Experiência com marketing de clube de futebol?”
	•	RAG Atua: Puxa da bio sobre Bandeirante Esporte Clube.
	•	Resposta: Áudio com voz do Endrigo, destacando cases reais e propondo colaboração.
Requisitos e Instalação no Replit
	•	Secrets (Ambiente):
	•	 OPENAI_API_KEY : Chave da OpenAI.
	•	 TWILIO_ACCOUNT_SID  e  TWILIO_AUTH_TOKEN : Para Twilio.
	•	Dependências (rode no shell do Replit):