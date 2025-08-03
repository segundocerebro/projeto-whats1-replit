"""
Sistema de Memória Avançado para Clone Digital
Gerencia memória de curto e longo prazo com insights contextuais
"""
import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

@dataclass
class MemoryFact:
    """Estrutura para fatos da memória"""
    type: str  # 'preference', 'business_context', 'personal_info', 'insight'
    content: str
    timestamp: datetime
    importance: int  # 1-10 scale
    context: str
    user_phone: str

class AdvancedMemorySystem:
    def __init__(self):
        self.short_term_memory = {}  # Sessão atual (RAM)
        self.long_term_memory = {}   # Persistente (Banco de Dados)
        self.contextual_insights = {}  # Padrões aprendidos
        self.conversation_summaries = {}  # Resumos por usuário
        self.fact_extractor = FactExtractor()
        
    def process_conversation(self, user_phone: str, user_message: str, ai_response: str):
        """Processa conversa completa e atualiza memórias"""
        # 1. Extrai fatos relevantes
        facts = self.fact_extractor.extract_facts(user_message, ai_response, user_phone)
        
        # 2. Atualiza memórias
        for fact in facts:
            self.update_memory(fact)
        
        # 3. Atualiza resumo contextual
        self.update_contextual_summary(user_phone, user_message, ai_response)
        
        # 4. Gera insights comportamentais
        self.generate_behavioral_insights(user_phone, user_message)
        
        logging.info(f"Processada conversa para {user_phone}: {len(facts)} fatos extraídos")
    
    def update_memory(self, fact: MemoryFact):
        """Atualiza sistema de memória com novo fato"""
        user_phone = fact.user_phone
        
        # Inicializa estruturas se necessário
        if user_phone not in self.long_term_memory:
            self.long_term_memory[user_phone] = {
                'preferences': [],
                'business_context': [],
                'personal_info': [],
                'insights': []
            }
        
        # Categoriza e armazena fato
        memory_category = self.long_term_memory[user_phone]
        fact_dict = asdict(fact)
        fact_dict['timestamp'] = fact.timestamp.isoformat()
        
        if fact.type in memory_category:
            # Evita duplicatas
            existing_contents = [f['content'] for f in memory_category[fact.type]]
            if fact.content not in existing_contents:
                memory_category[fact.type].append(fact_dict)
                
                # Mantém apenas os 50 fatos mais importantes por categoria
                memory_category[fact.type].sort(key=lambda x: x['importance'], reverse=True)
                memory_category[fact.type] = memory_category[fact.type][:50]
    
    def update_contextual_summary(self, user_phone: str, user_msg: str, ai_response: str):
        """Atualiza resumo contextual da conversa"""
        if user_phone not in self.conversation_summaries:
            self.conversation_summaries[user_phone] = {
                'last_topics': [],
                'interaction_style': 'formal',
                'current_session': [],
                'key_themes': {}
            }
        
        summary = self.conversation_summaries[user_phone]
        
        # Adiciona à sessão atual
        summary['current_session'].append({
            'user': user_msg[:200],  # Primeiros 200 chars
            'ai': ai_response[:200],
            'timestamp': datetime.now().isoformat()
        })
        
        # Mantém apenas últimas 10 interações na sessão
        summary['current_session'] = summary['current_session'][-10:]
        
        # Extrai tópicos principais
        topics = self.extract_topics(user_msg)
        for topic in topics:
            if topic not in summary['last_topics']:
                summary['last_topics'].append(topic)
        summary['last_topics'] = summary['last_topics'][-15:]  # Últimos 15 tópicos
    
    def extract_topics(self, text: str) -> List[str]:
        """Extrai tópicos principais do texto"""
        # Palavras-chave relevantes para negócios/IA
        business_keywords = [
            'marketing', 'publicidade', 'vendas', 'cliente', 'empresa', 'negócio',
            'ia', 'inteligência artificial', 'automação', 'bot', 'whatsapp',
            'estratégia', 'campanha', 'roi', 'conversão', 'lead', 'funil'
        ]
        
        text_lower = text.lower()
        found_topics = []
        
        for keyword in business_keywords:
            if keyword in text_lower:
                found_topics.append(keyword)
        
        return found_topics[:5]  # Máximo 5 tópicos por mensagem
    
    def generate_behavioral_insights(self, user_phone: str, message: str):
        """Gera insights comportamentais baseado na mensagem"""
        if user_phone not in self.contextual_insights:
            self.contextual_insights[user_phone] = {
                'communication_style': 'discovering',
                'technical_level': 'unknown',
                'business_maturity': 'unknown',
                'preferred_topics': {},
                'interaction_patterns': []
            }
        
        insights = self.contextual_insights[user_phone]
        
        # Detecta estilo de comunicação
        if len(message) > 100:
            insights['communication_style'] = 'detailed'
        elif len(message) < 20:
            insights['communication_style'] = 'concise'
        
        # Detecta nível técnico
        tech_terms = ['api', 'webhook', 'integração', 'sql', 'python', 'javascript']
        if any(term in message.lower() for term in tech_terms):
            insights['technical_level'] = 'high'
        
        # Detecta maturidade empresarial
        business_terms = ['estratégia', 'roi', 'kpi', 'métricas', 'funil', 'conversão']
        if any(term in message.lower() for term in business_terms):
            insights['business_maturity'] = 'advanced'
    
    def get_context_for_prompt(self, user_phone: str) -> Dict[str, Any]:
        """Retorna contexto completo para geração de prompt"""
        context = {
            'recent_conversation': '',
            'user_preferences': [],
            'business_context': [],
            'insights': [],
            'conversation_summary': '',
            'behavioral_patterns': {}
        }
        
        # Conversa recente
        if user_phone in self.conversation_summaries:
            summary = self.conversation_summaries[user_phone]
            recent_session = summary.get('current_session', [])[-3:]  # Últimas 3 interações
            
            context['recent_conversation'] = '\n'.join([
                f"Usuário: {interaction['user'][:100]}..."
                f"Endrigo: {interaction['ai'][:100]}..."
                for interaction in recent_session
            ])
            
            context['conversation_summary'] = f"Tópicos recentes: {', '.join(summary.get('last_topics', []))}"
        
        # Memória de longo prazo
        if user_phone in self.long_term_memory:
            memory = self.long_term_memory[user_phone]
            
            context['user_preferences'] = [
                fact['content'] for fact in memory.get('preferences', [])[-10:]
            ]
            context['business_context'] = [
                fact['content'] for fact in memory.get('business_context', [])[-10:]
            ]
            context['insights'] = [
                fact['content'] for fact in memory.get('insights', [])[-10:]
            ]
        
        # Padrões comportamentais
        if user_phone in self.contextual_insights:
            context['behavioral_patterns'] = self.contextual_insights[user_phone]
        
        return context
    
    def get_memory_stats(self, user_phone: str) -> Dict[str, Any]:
        """Retorna estatísticas da memória para debugging"""
        stats = {
            'total_facts': 0,
            'conversation_interactions': 0,
            'insights_generated': 0,
            'memory_categories': {}
        }
        
        if user_phone in self.long_term_memory:
            memory = self.long_term_memory[user_phone]
            for category, facts in memory.items():
                stats['memory_categories'][category] = len(facts)
                stats['total_facts'] += len(facts)
        
        if user_phone in self.conversation_summaries:
            stats['conversation_interactions'] = len(
                self.conversation_summaries[user_phone].get('current_session', [])
            )
        
        if user_phone in self.contextual_insights:
            stats['insights_generated'] = len(
                self.contextual_insights[user_phone].get('interaction_patterns', [])
            )
        
        return stats

class FactExtractor:
    """Extrator inteligente de fatos relevantes"""
    
    def extract_facts(self, user_msg: str, ai_response: str, user_phone: str) -> List[MemoryFact]:
        """Extrai fatos relevantes da conversa"""
        facts = []
        timestamp = datetime.now()
        
        # Extrai preferências
        preferences = self.extract_preferences(user_msg)
        for pref in preferences:
            facts.append(MemoryFact(
                type='preferences',
                content=pref,
                timestamp=timestamp,
                importance=7,
                context=user_msg[:100],
                user_phone=user_phone
            ))
        
        # Extrai contexto de negócios
        business_context = self.extract_business_context(user_msg)
        for context in business_context:
            facts.append(MemoryFact(
                type='business_context',
                content=context,
                timestamp=timestamp,
                importance=8,
                context=user_msg[:100],
                user_phone=user_phone
            ))
        
        # Extrai informações pessoais
        personal_info = self.extract_personal_info(user_msg)
        for info in personal_info:
            facts.append(MemoryFact(
                type='personal_info',
                content=info,
                timestamp=timestamp,
                importance=6,
                context=user_msg[:100],
                user_phone=user_phone
            ))
        
        return facts
    
    def extract_preferences(self, text: str) -> List[str]:
        """Extrai preferências explícitas"""
        preferences = []
        text_lower = text.lower()
        
        # Padrões de preferência
        preference_patterns = [
            r'eu gosto de (.+?)(?:\.|,|$)',
            r'eu prefiro (.+?)(?:\.|,|$)', 
            r'minha preferência é (.+?)(?:\.|,|$)',
            r'eu sempre (.+?)(?:\.|,|$)',
            r'não gosto de (.+?)(?:\.|,|$)'
        ]
        
        for pattern in preference_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 3:  # Evita matches muito curtos
                    preferences.append(f"Preferência: {match.strip()}")
        
        return preferences
    
    def extract_business_context(self, text: str) -> List[str]:
        """Extrai contexto empresarial"""
        business_contexts = []
        text_lower = text.lower()
        
        # Padrões de negócio
        business_patterns = [
            r'minha empresa (.+?)(?:\.|,|$)',
            r'meu negócio (.+?)(?:\.|,|$)',
            r'trabalho com (.+?)(?:\.|,|$)',
            r'nosso cliente (.+?)(?:\.|,|$)',
            r'estou desenvolvendo (.+?)(?:\.|,|$)'
        ]
        
        for pattern in business_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 5:
                    business_contexts.append(f"Contexto empresarial: {match.strip()}")
        
        return business_contexts
    
    def extract_personal_info(self, text: str) -> List[str]:
        """Extrai informações pessoais relevantes"""
        personal_info = []
        text_lower = text.lower()
        
        # Padrões de informação pessoal
        personal_patterns = [
            r'meu nome é (.+?)(?:\.|,|$)',
            r'me chamo (.+?)(?:\.|,|$)',
            r'sou de (.+?)(?:\.|,|$)',
            r'moro em (.+?)(?:\.|,|$)',
            r'tenho (.+?) anos'
        ]
        
        for pattern in personal_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 2:
                    personal_info.append(f"Info pessoal: {match.strip()}")
        
        return personal_info