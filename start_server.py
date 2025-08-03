#!/usr/bin/env python3
"""
Script para iniciar o servidor na porta correta (8080) para Replit
Solução para o problema de porta identificado no diagnóstico
"""
import os
import subprocess
import sys

def main():
    print("🔧 Iniciando servidor na porta 8080 (correção para Replit)")
    
    # Forçar porta 8080 
    os.environ['PORT'] = '8080'
    
    # Comando corrigido do gunicorn
    cmd = [
        "gunicorn", 
        "--bind", "0.0.0.0:8080",
        "--reuse-port", 
        "--reload",
        "main:app"
    ]
    
    print(f"📡 Executando: {' '.join(cmd)}")
    
    # Executar gunicorn
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()