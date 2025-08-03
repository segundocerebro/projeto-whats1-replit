#!/usr/bin/env python3
"""
Solução definitiva para o problema de porta no Replit
Este script inicia o servidor com configuração compatível
"""
import os
import sys
import subprocess

def main():
    print("🔧 Configurando servidor para porta 8080 (compatível com Replit)")
    
    # Definir variáveis de ambiente
    os.environ['PORT'] = '8080'
    
    # Comando correto do gunicorn para porta 8080
    cmd = [
        'gunicorn',
        '--bind', '0.0.0.0:8080',  # Força porta 8080
        '--workers', '1',
        '--timeout', '300',
        '--keepalive', '60',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--preload',
        'main:app'
    ]
    
    print(f"📡 Comando: {' '.join(cmd)}")
    
    try:
        # Executar gunicorn
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Monitorar saída
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
            
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido")
        process.terminate()
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()