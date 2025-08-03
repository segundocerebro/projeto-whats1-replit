#!/usr/bin/env python3
"""
Teste do sistema de áudio Realtime - Simula mensagem de áudio real
"""
import requests

def test_audio_realtime():
    """Simula uma mensagem de áudio real do WhatsApp"""
    
    webhook_url = "http://localhost:5000/webhook/whatsapp/realtime"
    
    # Dados simulando mensagem de áudio real do Twilio
    audio_data = {
        'From': 'whatsapp:+5518991976211',
        'To': 'whatsapp:+14155238886',
        'Body': '',  # Áudio não tem body
        'MediaUrl0': 'https://api.twilio.com/test/audio.ogg',  # URL simulada
        'MediaContentType0': 'audio/ogg',
        'MessageSid': 'SM_audio_test_realtime',
        'AccountSid': 'AC_test_account',
        'NumMedia': '1'
    }
    
    print("🎤 TESTANDO SISTEMA REALTIME AUDIO")
    print("=" * 50)
    print(f"Webhook: {webhook_url}")
    print(f"Simulando áudio de: {audio_data['From']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            webhook_url,
            data=audio_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.text:
            print(f"Resposta:")
            print(response.text)
        
        if response.status_code == 200:
            print("\n✅ SUCESSO: Sistema processou áudio!")
        else:
            print(f"\n❌ ERRO: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")

if __name__ == "__main__":
    test_audio_realtime()