#!/usr/bin/env python3
"""
Script para testar o webhook Realtime Audio
Simula uma mensagem do WhatsApp com áudio para verificar o fluxo completo
"""
import requests
import json
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)

def test_realtime_webhook():
    """Testa o webhook /webhook/whatsapp/realtime"""
    
    # URL do webhook Realtime
    webhook_url = "http://localhost:5000/webhook/whatsapp/realtime"
    
    # Dados simulados do Twilio WhatsApp
    test_data = {
        'From': 'whatsapp:+5511999999999',
        'To': 'whatsapp:+14155238886',
        'Body': '',  # Mensagem de áudio não tem body
        'MediaUrl0': 'https://api.twilio.com/test/audio.ogg',  # URL simulada
        'MediaContentType0': 'audio/ogg',
        'MessageSid': 'test_message_sid_123',
        'AccountSid': 'test_account_sid',
        'NumMedia': '1'
    }
    
    print("🎤 Testando webhook Realtime Audio...")
    print(f"URL: {webhook_url}")
    print(f"Dados: {json.dumps(test_data, indent=2)}")
    
    try:
        # Envia request POST para o webhook
        response = requests.post(
            webhook_url,
            data=test_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"\n✅ Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.text:
            print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 Webhook Realtime funcionando!")
        else:
            print(f"\n❌ Erro no webhook: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro na requisição: {e}")

def test_text_message():
    """Testa mensagem de texto no webhook Realtime"""
    
    webhook_url = "http://localhost:5000/webhook/whatsapp/realtime"
    
    test_data = {
        'From': 'whatsapp:+5511999999999',
        'To': 'whatsapp:+14155238886',
        'Body': 'Olá Endrigo! Como você pode me ajudar?',
        'MessageSid': 'test_text_message_123',
        'AccountSid': 'test_account_sid',
        'NumMedia': '0'
    }
    
    print("\n💬 Testando mensagem de texto...")
    
    try:
        response = requests.post(
            webhook_url,
            data=test_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.text:
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🧪 TESTE DO SISTEMA REALTIME AUDIO")
    print("=" * 50)
    
    # Testa status do sistema
    try:
        status_response = requests.get("http://localhost:5000/test/realtime-audio")
        print(f"Status do sistema: {status_response.json()}")
        print("-" * 50)
    except:
        print("❌ Erro obtendo status do sistema")
    
    # Testa webhook com áudio
    test_realtime_webhook()
    
    # Testa webhook com texto
    test_text_message()
    
    print("\n✅ Testes concluídos!")