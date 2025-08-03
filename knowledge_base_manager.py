import os
import logging
import pdfplumber
import re
from typing import List, Dict

class KnowledgeBase:
    """Sistema RAG simples para busca de contexto em documentos PDF"""
    
    def __init__(self, file_paths: List[str]):
        self.chunks = []
        self.file_paths = file_paths
        self.load_files()
        
    def load_files(self):
        """Carrega e processa arquivos PDF e TXT"""
        for path in self.file_paths:
            if os.path.exists(path):
                try:
                    text = ""
                    if path.endswith('.pdf'):
                        # Processa PDFs
                        with pdfplumber.open(path) as pdf:
                            for page in pdf.pages:
                                if page.extract_text():
                                    text += page.extract_text() + "\n"
                    elif path.endswith('.txt'):
                        # Processa arquivos de texto
                        with open(path, 'r', encoding='utf-8') as f:
                            text = f.read()
                    
                    # Divide em chunks de 400 caracteres
                    chunks = [text[i:i+400] for i in range(0, len(text), 300)]
                    self.chunks.extend(chunks)
                    logging.info(f"✅ Carregado {len(chunks)} chunks de {path}")
                    
                except Exception as e:
                    logging.error(f"❌ Erro carregando {path}: {e}")
            else:
                logging.warning(f"⚠️ Arquivo não encontrado: {path}")
    
    def retrieve_relevant(self, query: str, top_k: int = 3) -> List[str]:
        """Busca chunks relevantes usando correspondência de palavras-chave"""
        if not self.chunks:
            return []
            
        query_words = set(re.findall(r'\w+', query.lower()))
        scored_chunks = []
        
        for chunk in self.chunks:
            chunk_words = set(re.findall(r'\w+', chunk.lower()))
            # Score baseado em intersecção de palavras
            score = len(query_words.intersection(chunk_words))
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Ordena por score e retorna top_k
        scored_chunks.sort(reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]
    
    def get_context_for_query(self, query: str) -> str:
        """Retorna contexto formatado para a query"""
        relevant_chunks = self.retrieve_relevant(query)
        if relevant_chunks:
            context = "\n\n".join(relevant_chunks)
            return f"CONTEXTO RELEVANTE DA BIOGRAFIA:\n{context}\n"
        return ""

# Instância global para reutilização
knowledge_base = None

def initialize_knowledge_base():
    """Inicializa a base de conhecimento"""
    global knowledge_base
    if knowledge_base is None:
        file_paths = [
            "documents/bio_endrigo.pdf",
            "documents/biografia_endrigo_completa.txt"
        ]
        knowledge_base = KnowledgeBase(file_paths)
    return knowledge_base