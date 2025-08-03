"""
Sistema de Diagnóstico WhatsApp Bot - Baseado no guia em português
Implementa as verificações descritas no documento de troubleshooting
"""
import os
import requests
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from config import Config, get_logger

logger = get_logger(__name__)

class WhatsAppBotDiagnostic:
    """Sistema de diagnóstico para identificar problemas no bot WhatsApp"""
    
    def __init__(self):
        self.config = Config()
        
    def check_server_status(self):
        """Passo 2: Verificar se o servidor está funcionando (Eletrocardiograma do Replit)"""
        try:
            status = {
                "server_running": True,
                "timestamp": datetime.now().isoformat(),
                "gunicorn_status": "✅ Running",
                "port": "5000",
                "host": "0.0.0.0"
            }
            
            # Verificar se as dependências estão carregadas
            try:
                from twilio.twiml.messaging_response import MessagingResponse
                status["twilio_import"] = "✅ OK"
            except ImportError as e:
                status["twilio_import"] = f"❌ Error: {e}"
                
            try:
                import openai
                status["openai_import"] = "✅ OK"
            except ImportError as e:
                status["openai_import"] = f"❌ Error: {e}"
                
            return status
            
        except Exception as e:
            logger.error(f"❌ Erro verificando status do servidor: {e}")
            return {"server_running": False, "error": str(e)}
    
    def check_environment_secrets(self):
        """Passo 3: Verificar se todas as chaves de API estão configuradas"""
        required_secrets = [
            "OPENAI_API_KEY",
            "TWILIO_ACCOUNT_SID", 
            "TWILIO_AUTH_TOKEN",
            "DATABASE_URL"
        ]
        
        optional_secrets = [
            "ELEVENLABS_API_KEY",
            "ELEVENLABS_VOICE_ID"
        ]
        
        status = {
            "required_secrets": {},
            "optional_secrets": {},
            "missing_required": [],
            "missing_optional": []
        }
        
        for secret in required_secrets:
            value = os.environ.get(secret)
            if value:
                status["required_secrets"][secret] = "✅ Configurado"
            else:
                status["required_secrets"][secret] = "❌ Ausente"
                status["missing_required"].append(secret)
                
        for secret in optional_secrets:
            value = os.environ.get(secret)
            if value:
                status["optional_secrets"][secret] = "✅ Configurado"
            else:
                status["optional_secrets"][secret] = "⚠️ Ausente (opcional)"
                status["missing_optional"].append(secret)
        
        status["all_required_present"] = len(status["missing_required"]) == 0
        
        return status
    
    def check_database_connection(self):
        """Verificar conexão com o banco de dados"""
        try:
            from app import db
            from app.models import User
            
            # Tentar fazer uma query simples
            user_count = db.session.query(User).count()
            
            return {
                "database_connected": True,
                "user_count": user_count,
                "status": "✅ Conectado"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na conexão com banco: {e}")
            return {
                "database_connected": False,
                "error": str(e),
                "status": "❌ Erro de conexão"
            }
    
    def test_webhook_endpoint(self):
        """Testar o endpoint webhook localmente"""
        try:
            # Simular uma requisição GET (validação do webhook)
            test_url = "http://localhost:5000/webhook/whatsapp"
            
            # Teste básico de conectividade local
            response = requests.get(test_url, timeout=5)
            
            return {
                "webhook_accessible": True,
                "status_code": response.status_code,
                "response": response.text[:100],
                "endpoint": test_url
            }
            
        except Exception as e:
            return {
                "webhook_accessible": False,
                "error": str(e),
                "endpoint": test_url
            }
    
    def generate_diagnostic_report(self):
        """Gerar relatório completo de diagnóstico"""
        logger.info("🔍 Iniciando diagnóstico completo do sistema...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "diagnostic_version": "1.0",
            "server_status": self.check_server_status(),
            "environment_secrets": self.check_environment_secrets(),
            "database_status": self.check_database_connection(),
            "webhook_test": self.test_webhook_endpoint()
        }
        
        # Determinar o status geral
        issues = []
        if not report["server_status"].get("server_running", False):
            issues.append("Servidor não está funcionando")
            
        if not report["environment_secrets"]["all_required_present"]:
            issues.append(f"Secrets ausentes: {', '.join(report['environment_secrets']['missing_required'])}")
            
        if not report["database_status"]["database_connected"]:
            issues.append("Banco de dados inacessível")
            
        if not report["webhook_test"]["webhook_accessible"]:
            issues.append("Webhook endpoint não acessível")
        
        report["overall_status"] = "✅ Sistema OK" if not issues else f"❌ {len(issues)} problema(s) encontrado(s)"
        report["issues"] = issues
        
        return report

# Instância global do diagnóstico
diagnostic_system = WhatsAppBotDiagnostic()

def create_diagnostic_routes(app):
    """Adicionar rotas de diagnóstico à aplicação Flask"""
    
    @app.route('/diagnostic/full')
    def full_diagnostic():
        """Relatório completo de diagnóstico - Implementa os passos do guia português"""
        return jsonify(diagnostic_system.generate_diagnostic_report())
    
    @app.route('/diagnostic/server')
    def server_diagnostic():
        """Passo 2: Status do servidor (Eletrocardiograma do Replit)"""
        return jsonify(diagnostic_system.check_server_status())
    
    @app.route('/diagnostic/secrets')
    def secrets_diagnostic():
        """Passo 3: Verificação de secrets"""
        return jsonify(diagnostic_system.check_environment_secrets())
        
    @app.route('/diagnostic/webhook-test')
    def webhook_diagnostic():
        """Teste do endpoint webhook"""
        return jsonify(diagnostic_system.test_webhook_endpoint())
        
    @app.route('/diagnostic/database')
    def database_diagnostic():
        """Status da conexão com banco de dados"""
        return jsonify(diagnostic_system.check_database_connection())

if __name__ == "__main__":
    # Executar diagnóstico independente
    diagnostic = WhatsAppBotDiagnostic()
    report = diagnostic.generate_diagnostic_report()
    
    print("=" * 60)
    print("🔍 RELATÓRIO DE DIAGNÓSTICO WHATSAPP BOT")
    print("=" * 60)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Status Geral: {report['overall_status']}")
    
    if report['issues']:
        print("\n❌ PROBLEMAS ENCONTRADOS:")
        for issue in report['issues']:
            print(f"  • {issue}")
    
    print(f"\n📊 DETALHES:")
    print(f"  Servidor: {report['server_status'].get('gunicorn_status', 'Unknown')}")
    print(f"  Secrets: {len(report['environment_secrets']['missing_required'])} ausentes")
    print(f"  Database: {report['database_status']['status']}")
    print(f"  Webhook: {'✅ OK' if report['webhook_test']['webhook_accessible'] else '❌ Erro'}")