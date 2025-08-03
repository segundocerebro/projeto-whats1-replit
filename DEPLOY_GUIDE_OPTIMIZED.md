# Guia de Deploy Otimizado - Endrigo Digital v3.0

## Problema Identificado: "Exército de Clones Gulosos"

### O Diagnóstico
O erro de memória não era por falta de RAM (8GB é suficiente), mas por como o Gunicorn gerencia workers:

- **Problema**: Cada worker do Gunicorn carregava uma cópia separada dos embeddings (3GB cada)
- **Resultado**: 3 workers × 3GB = 9GB de uso, excedendo os 8GB disponíveis
- **Sintoma**: SIGKILL e crashes com "Perhaps out of memory?"

### A Solução: Flag --preload

A flag `--preload` faz o Gunicorn:
1. Carregar a aplicação e embeddings UMA vez na memória principal
2. Compartilhar essa memória entre todos os workers
3. Reduzir drasticamente o consumo de RAM

## Implementação

### Opção 1: Script Otimizado (Recomendado)
```bash
python start_optimized.py
```

### Opção 2: Comando Direto
```bash
gunicorn -w 3 --preload --bind 0.0.0.0:$PORT main:app
```

### Opção 3: Para Deploy no Replit
Editar `.replit` (se permitido):
```toml
run = ["sh", "-c", "gunicorn -w 3 --preload --bind 0.0.0.0:$PORT main:app"]
```

## Benefícios da Otimização

- **Memória**: Reduz uso de ~9GB para ~3GB
- **Performance**: Workers compartilham dados pré-carregados
- **Estabilidade**: Elimina crashes por falta de memória
- **Padrão da Indústria**: Configuração recomendada para aplicações com dados grandes

## Validação

✅ Sistema v3.0 com otimização de memória implementada
✅ RAG semântico funcionando (threshold 0.35)
✅ Audio pipeline bulletproof com FFmpeg
✅ Pronto para deploy em produção

## Próximos Passos

1. Use `python start_optimized.py` para desenvolvimento
2. Configure deploy no Replit com a flag --preload
3. Monitore uso de memória (deve ficar ~3GB)
4. Sistema pronto para produção em larga escala