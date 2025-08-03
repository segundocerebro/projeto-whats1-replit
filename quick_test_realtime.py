#!/usr/bin/env python3
"""
Teste rápido do sistema Realtime - Simula uma mensagem real do WhatsApp
"""
import requests
import json

def test_webhook_realtime():
    """Teste completo do webhook v3 Realtime"""
    
    webhook_url = "http://localhost:5000/webhook/whatsapp/realtime"
    
    # Simula dados reais do Twilio WhatsApp
    whatsapp_data = {
        'From': 'whatsapp:+5511999999999',
        'To': 'whatsapp:+14155238886', 
        'Body': 'Olá Endrigo! Como você pode me ajudar com marketing digital?',
        'MessageSid': 'SM_test_realtime_123',
        'AccountSid': 'AC_test_account',
        'NumMedia': '0'  # Mensagem de texto
    }
    
    print("🎤 TESTE WEBHOOK REALTIME v3")
    print("=" * 50)
    print(f"URL: {webhook_url}")
    print(f"Mensagem: {whatsapp_data['Body']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            webhook_url,
            data=whatsapp_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=45  # Maior timeout para Realtime
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.text:
            print(f"Resposta TwiML:")
            print(response.text)
        
        if response.status_code == 200:
            print("\n✅ SUCESSO: Webhook v3 Realtime funcionando!")
            print("🎯 Sistema pronto para receber áudio do WhatsApp")
        else:
            print(f"\n❌ ERRO: Status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO na requisição: {e}")

def check_system_status():
    """Verifica status de todos os sistemas"""
    
    endpoints = [
        ('/test/realtime-audio', 'Realtime Audio'),
        ('/system/advanced-status', 'Sistema Avançado'),
        ('/upgrade-webhook', 'Upgrade Info')
    ]
    
    print("\n📊 STATUS DOS SISTEMAS")
    print("=" * 30)
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: Erro {response.status_code}")
        except:
            print(f"❌ {name}: Indisponível")

if __name__ == "__main__":
    # Verifica status primeiro
    check_system_status()
    
    # Testa webhook Realtime
    test_webhook_realtime()
    
    print("\n🚀 CONFIGURAÇÃO PRONTA!")
    print("Configure o webhook no Twilio:")
    print("https://6771fe47-1a6d-4a14-a791-ac9ee41dd82d-00-ys74xr6dg9hv.worf.replit.dev/webhook/whatsapp/realtime")