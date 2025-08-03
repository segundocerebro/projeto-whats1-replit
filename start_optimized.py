#!/usr/bin/env python3
"""
Startup script otimizado para produção com flag --preload
Soluciona o problema de memória identificado pelos especialistas
"""
import os
import subprocess
import sys

def start_server():
    port = os.environ.get('PORT', '5000')
    
    # Comando otimizado com --preload para compartilhar memória entre workers
    cmd = [
        'gunicorn',
        '-w', '3',           # 3 workers fixos
        '--preload',         # Carrega app uma vez e compartilha entre workers
        '--bind', f'0.0.0.0:{port}',
        'main:app'
    ]
    
    print(f"🚀 Iniciando servidor otimizado na porta {port}")
    print(f"📝 Comando: {' '.join(cmd)}")
    print(f"💾 Flag --preload ativa: compartilhamento de memória entre workers")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_server()