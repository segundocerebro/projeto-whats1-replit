"""
Pipeline Otimizado para Latência Ultra-Baixa
Implementa processamento streaming e paralelo
"""
import asyncio
import time
import logging
from typing import Dict, Any, Optional
import concurrent.futures
from dataclasses import dataclass

@dataclass
class LatencyMetrics:
    """Métricas de latência do pipeline"""
    asr_latency: float = 0.0  # Automatic Speech Recognition
    llm_latency: float = 0.0  # Large Language Model
    tts_latency: float = 0.0  # Text-to-Speech
    total_latency: float = 0.0
    target_latency: float = 525.0  # ms

class OptimizedPipeline:
    def __init__(self):
        self.streaming_enabled = True
        self.chunk_size = 1024  # bytes para processamento
        self.max_latency_target = 525  # ms
        self.parallel_workers = 3
        self.metrics = LatencyMetrics()
        
    async def process_with_streaming(self, audio_input: bytes, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processamento principal com streaming otimizado"""
        start_time = time.time()
        
        try:
            # Fase 1: Processamento paralelo de chunks
            if self.streaming_enabled and len(audio_input) > self.chunk_size * 2:
                result = await self._process_streaming_chunks(audio_input, context)
            else:
                result = await self._process_single_chunk(audio_input, context)
            
            # Calcula latência total
            total_latency = (time.time() - start_time) * 1000  # ms
            self.metrics.total_latency = total_latency
            
            # Log de performance
            self._log_performance_metrics()
            
            result['latency_metrics'] = self.metrics
            result['performance_score'] = self._calculate_performance_score()
            
            return result
            
        except Exception as e:
            logging.error(f"Erro no pipeline otimizado: {e}")
            return {
                'success': False,
                'error': str(e),
                'latency_metrics': self.metrics
            }
    
    async def _process_streaming_chunks(self, audio_input: bytes, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa áudio em chunks paralelos para reduzir latência"""
        chunks = self._split_into_chunks(audio_input)
        
        # Processa chunks em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            loop = asyncio.get_event_loop()
            
            # Cria tasks para processamento paralelo
            chunk_tasks = []
            for i, chunk in enumerate(chunks):
                task = loop.run_in_executor(
                    executor,
                    self._process_chunk_sync,
                    chunk, context, i
                )
                chunk_tasks.append(task)
            
            # Aguarda todos os chunks processados
            chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
        
        # Combina resultados dos chunks
        return self._combine_chunk_results(chunk_results)
    
    async def _process_single_chunk(self, audio_input: bytes, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa áudio como chunk único (fallback)"""
        return await asyncio.to_thread(self._process_chunk_sync, audio_input, context, 0)
    
    def _process_chunk_sync(self, chunk: bytes, context: Dict[str, Any], chunk_index: int) -> Dict[str, Any]:
        """Processamento síncrono de um chunk individual"""
        start_chunk_time = time.time()
        
        try:
            # Simula processamento do chunk
            # Na implementação real, aqui seria:
            # 1. ASR do chunk
            # 2. Processamento LLM
            # 3. TTS do resultado
            
            chunk_latency = (time.time() - start_chunk_time) * 1000
            
            return {
                'success': True,
                'chunk_index': chunk_index,
                'chunk_latency': chunk_latency,
                'processed_data': f"Chunk {chunk_index} processado",
                'chunk_size': len(chunk)
            }
            
        except Exception as e:
            return {
                'success': False,
                'chunk_index': chunk_index,
                'error': str(e)
            }
    
    def _split_into_chunks(self, audio_data: bytes) -> list:
        """Divide áudio em chunks otimizados"""
        chunks = []
        
        # Calcula tamanho ideal do chunk baseado no tamanho total
        total_size = len(audio_data)
        optimal_chunk_size = min(self.chunk_size, total_size // self.parallel_workers)
        
        if optimal_chunk_size < 512:  # Chunk mínimo
            optimal_chunk_size = 512
        
        # Divide em chunks
        for i in range(0, total_size, optimal_chunk_size):
            chunk = audio_data[i:i + optimal_chunk_size]
            chunks.append(chunk)
        
        logging.info(f"Áudio dividido em {len(chunks)} chunks de ~{optimal_chunk_size} bytes")
        return chunks
    
    def _combine_chunk_results(self, chunk_results: list) -> Dict[str, Any]:
        """Combina resultados dos chunks processados"""
        successful_chunks = [r for r in chunk_results if isinstance(r, dict) and r.get('success')]
        failed_chunks = [r for r in chunk_results if not (isinstance(r, dict) and r.get('success'))]
        
        if not successful_chunks:
            return {
                'success': False,
                'error': 'Nenhum chunk processado com sucesso',
                'failed_chunks': len(failed_chunks)
            }
        
        # Calcula métricas combinadas
        total_chunk_latency = sum(chunk.get('chunk_latency', 0) for chunk in successful_chunks)
        avg_chunk_latency = total_chunk_latency / len(successful_chunks)
        
        # Simula resultado final combinado
        combined_result = {
            'success': True,
            'processed_chunks': len(successful_chunks),
            'failed_chunks': len(failed_chunks),
            'average_chunk_latency': avg_chunk_latency,
            'total_processing_time': total_chunk_latency,
            'combined_output': self._merge_chunk_outputs(successful_chunks)
        }
        
        return combined_result
    
    def _merge_chunk_outputs(self, successful_chunks: list) -> str:
        """Merge outputs dos chunks em resultado final"""
        # Ordena chunks pelo índice
        sorted_chunks = sorted(successful_chunks, key=lambda x: x.get('chunk_index', 0))
        
        # Combina dados processados
        merged_output = " ".join([
            chunk.get('processed_data', '') for chunk in sorted_chunks
        ])
        
        return merged_output
    
    def _calculate_performance_score(self) -> float:
        """Calcula score de performance (0-100)"""
        if self.metrics.total_latency <= 0:
            return 0.0
        
        # Score baseado na latência vs target
        latency_score = max(0, 100 - (self.metrics.total_latency / self.metrics.target_latency) * 50)
        
        # Bonus por usar streaming
        streaming_bonus = 10 if self.streaming_enabled else 0
        
        # Penalty por falhas
        success_penalty = 0  # Implementar baseado em taxa de sucesso
        
        final_score = min(100, latency_score + streaming_bonus - success_penalty)
        return round(final_score, 2)
    
    def _log_performance_metrics(self):
        """Log das métricas de performance"""
        metrics = self.metrics
        
        status = "✅ EXCELENTE" if metrics.total_latency <= metrics.target_latency else "⚠️ ACIMA DO TARGET"
        
        logging.info(f"""
MÉTRICAS DE PERFORMANCE - {status}
=====================================
🎯 Target: {metrics.target_latency}ms
⚡ Total: {metrics.total_latency:.1f}ms
🎤 ASR: {metrics.asr_latency:.1f}ms  
🧠 LLM: {metrics.llm_latency:.1f}ms
🗣️ TTS: {metrics.tts_latency:.1f}ms
📊 Score: {self._calculate_performance_score()}/100
        """)
    
    def optimize_for_latency(self):
        """Otimizações específicas para reduzir latência"""
        # Reduz chunk size para processamento mais rápido
        if self.metrics.total_latency > self.max_latency_target:
            self.chunk_size = max(512, self.chunk_size - 256)
            logging.info(f"Otimizando: chunk_size reduzido para {self.chunk_size}")
        
        # Aumenta workers paralelos se necessário
        if self.metrics.total_latency > self.max_latency_target * 1.5:
            self.parallel_workers = min(6, self.parallel_workers + 1)
            logging.info(f"Otimizando: parallel_workers aumentado para {self.parallel_workers}")
    
    def get_optimization_suggestions(self) -> Dict[str, str]:
        """Retorna sugestões de otimização baseadas na performance"""
        suggestions = {}
        
        if self.metrics.total_latency > self.metrics.target_latency:
            suggestions['latency'] = f"Latência {self.metrics.total_latency:.1f}ms acima do target {self.metrics.target_latency}ms"
        
        if not self.streaming_enabled:
            suggestions['streaming'] = "Ativar streaming pode reduzir latência percebida"
        
        if self.parallel_workers < 4:
            suggestions['parallelism'] = "Aumentar workers paralelos pode melhorar performance"
        
        return suggestions