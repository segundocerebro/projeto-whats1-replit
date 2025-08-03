"""
Sistema de Personalidade Multi-Camadas v4
Gerencia personalidade contextual e adaptativa
"""
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

class PersonalityManager:
    def __init__(self):
        self.base_personality = self.load_base_personality()
        self.conversation_memory = {}
        self.context_history = []
        self.behavioral_patterns = {}
        
    def load_base_personality(self) -> Dict[str, Any]:
        """Carrega personalidade base multi-camadas"""
        return {
            # Camada 1: Identidade Central
            "core": {
                "name": "Endrigo Almada",
                "role": "Fundador/CEO Ecossistema Publicitário",
                "location": "Birigui, SP", 
                "experience": "22+ anos",
                "expertise": ["Publicidade", "IA", "Inovação", "Marketing Digital", "Automação"]
            },
            
            # Camada 2: Estilo Conversacional
            "style": {
                "tone": "caloroso_profissional",
                "language": "português_brasileiro",
                "formality": "semi_formal",
                "enthusiasm": "alto_para_tecnologia",
                "humor": "sutil_inteligente",
                "energy_level": "dinâmico_motivador"
            },
            
            # Camada 3: Conhecimento Contextual  
            "context": {
                "business_focus": "otimização_empresarial_com_ia",
                "target_audience": "empresários_inovadores",
                "communication_preference": "prático_com_insights",
                "decision_style": "data_driven_humanizado",
                "value_proposition": "eficiência_através_da_tecnologia"
            },
            
            # Camada 4: Padrões Comportamentais
            "behavior": {
                "greeting_style": "personalizado_caloroso",
                "explanation_method": "analogias_práticas",
                "follow_up": "proativo_com_valor",
                "problem_solving": "consultivo_experiente",
                "learning_approach": "iterativo_adaptativo"
            }
        }
    
    def generate_contextual_prompt(self, conversation_history: List[Dict], user_phone: str) -> str:
        """Gera prompt contextual baseado no histórico"""
        recent_context = self.extract_recent_context(conversation_history)
        user_profile = self.get_user_profile(user_phone)
        
        return f"""
{self.base_personality['core']['name']} - Clone Digital Profissional Avançado

CONTEXTO ATUAL DA CONVERSA:
{recent_context}

PERFIL DO USUÁRIO:
{user_profile}

INSTRUÇÕES DE PERSONALIDADE v4:
1. Tom: {self.base_personality['style']['tone']} com {self.base_personality['style']['energy_level']}
2. Linguagem: {self.base_personality['style']['language']} com expressões naturais
3. Expertise: Demonstre conhecimento em {', '.join(self.base_personality['core']['expertise'])}
4. Método: Use {self.base_personality['behavior']['explanation_method']} 
5. Abordagem: Seja {self.base_personality['behavior']['problem_solving']}
6. Valor: Entregue {self.base_personality['context']['value_proposition']}

MEMÓRIA DE CONVERSA ATIVA:
{self.format_conversation_memory(user_phone)}

PADRÕES COMPORTAMENTAIS APRENDIDOS:
{self.get_behavioral_insights(user_phone)}
        """
    
    def extract_recent_context(self, conversation_history: List[Dict]) -> str:
        """Extrai contexto relevante das últimas conversas"""
        if not conversation_history:
            return "Primeira interação com o usuário"
        
        recent_msgs = conversation_history[-5:]  # Últimas 5 mensagens
        context_summary = []
        
        for msg in recent_msgs:
            timestamp = msg.get('timestamp', datetime.now())
            content = msg.get('message_text', '')[:100]  # Primeiros 100 chars
            context_summary.append(f"[{timestamp}] {content}")
        
        return "\n".join(context_summary)
    
    def get_user_profile(self, user_phone: str) -> str:
        """Recupera perfil específico do usuário"""
        if user_phone not in self.conversation_memory:
            return "Novo usuário - sem histórico anterior"
        
        profile = self.conversation_memory[user_phone]
        return f"""
Interações anteriores: {profile.get('interaction_count', 0)}
Tópicos de interesse: {', '.join(profile.get('interests', []))}
Estilo preferido: {profile.get('preferred_style', 'não definido')}
Última conversa: {profile.get('last_interaction', 'não registrada')}
        """
    
    def format_conversation_memory(self, user_phone: str) -> str:
        """Formata memória de conversa para o prompt"""
        if user_phone not in self.conversation_memory:
            return "Nenhuma memória anterior registrada"
        
        memory = self.conversation_memory[user_phone]
        key_memories = memory.get('key_memories', [])
        
        if not key_memories:
            return "Memórias sendo construídas..."
        
        return "\n".join([f"- {mem}" for mem in key_memories[-10:]])  # Últimas 10 memórias
    
    def get_behavioral_insights(self, user_phone: str) -> str:
        """Retorna insights comportamentais aprendidos"""
        if user_phone not in self.behavioral_patterns:
            return "Coletando padrões comportamentais..."
        
        patterns = self.behavioral_patterns[user_phone]
        insights = []
        
        if patterns.get('prefers_voice', False):
            insights.append("Usuário prefere comunicação por áudio")
        if patterns.get('business_focused', False):
            insights.append("Foco em aplicações empresariais")
        if patterns.get('technical_level') == 'high':
            insights.append("Nível técnico avançado")
        
        return "; ".join(insights) if insights else "Padrões em análise"
    
    def update_user_profile(self, user_phone: str, interaction_data: Dict[str, Any]):
        """Atualiza perfil do usuário com nova interação"""
        if user_phone not in self.conversation_memory:
            self.conversation_memory[user_phone] = {
                'interaction_count': 0,
                'interests': [],
                'key_memories': [],
                'preferred_style': None,
                'last_interaction': None
            }
        
        profile = self.conversation_memory[user_phone]
        profile['interaction_count'] += 1
        profile['last_interaction'] = datetime.now().isoformat()
        
        # Analisa interesses
        message_text = interaction_data.get('message_text', '').lower()
        if 'marketing' in message_text or 'publicidade' in message_text:
            if 'marketing' not in profile['interests']:
                profile['interests'].append('marketing')
        if 'ia' in message_text or 'inteligência artificial' in message_text:
            if 'ia' not in profile['interests']:
                profile['interests'].append('ia')
        
        # Salva memórias importantes
        if len(message_text) > 50:  # Mensagens substanciais
            profile['key_memories'].append(f"[{datetime.now().strftime('%d/%m')}] {message_text[:150]}")
            # Mantém apenas últimas 20 memórias
            profile['key_memories'] = profile['key_memories'][-20:]
        
        logging.info(f"Perfil atualizado para {user_phone}: {profile['interaction_count']} interações")
    
    def learn_behavioral_pattern(self, user_phone: str, pattern_data: Dict[str, Any]):
        """Aprende padrões comportamentais do usuário"""
        if user_phone not in self.behavioral_patterns:
            self.behavioral_patterns[user_phone] = {}
        
        patterns = self.behavioral_patterns[user_phone]
        
        # Detecta preferência por áudio
        if pattern_data.get('message_type') == 'audio':
            patterns['prefers_voice'] = patterns.get('prefers_voice', 0) + 1 > 2
        
        # Detecta foco em negócios
        if any(word in pattern_data.get('content', '').lower() 
               for word in ['empresa', 'negócio', 'cliente', 'vendas']):
            patterns['business_focused'] = True
        
        # Detecta nível técnico
        tech_words = ['api', 'webhook', 'integração', 'automatização']
        if any(word in pattern_data.get('content', '').lower() for word in tech_words):
            patterns['technical_level'] = 'high'