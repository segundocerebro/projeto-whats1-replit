import requests
import os
import tempfile
import logging

class ElevenlabsVoice:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.base_url = "https://api.elevenlabs.io/v1"

    def text_to_speech(self, text, output_path=None):
        """
        Converte texto em áudio usando a voz clonada do Endrigo
        
        Args:
            text (str): Texto para converter em áudio
            output_path (str, optional): Caminho para salvar o arquivo. Se None, usa arquivo temporário.
        
        Returns:
            str: Caminho do arquivo de áudio gerado
        """
        try:
            if not self.api_key or not self.voice_id:
                logging.warning("ELEVENLABS_API_KEY ou ELEVENLABS_VOICE_ID não configurado")
                return None
            
            # Usar texto diretamente (já limpo)
            clean_text = text.strip()
                
            # URL da API
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            
            # Headers para ElevenLabs
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': self.api_key
            }
            
            # Dados da requisição com texto limpo
            data = {
                'text': clean_text,
                'model_id': 'eleven_multilingual_v2',
                'voice_settings': {
                    'stability': 0.6,
                    'similarity_boost': 0.8,
                    'style': 0.2,  # Adicionar variação
                    'use_speaker_boost': True
                }
            }
            
            logging.info(f"Convertendo texto em áudio: {text[:50]}...")
            
            # Fazer requisição
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                # Definir caminho do arquivo
                if output_path is None:
                    # Criar arquivo temporário
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                    output_path = temp_file.name
                    temp_file.close()
                
                # Salvar áudio
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logging.info(f"Áudio gerado com sucesso: {output_path}")
                return output_path
            else:
                logging.error(f"Erro na API ElevenLabs: {response.status_code}")
                logging.error(f"Resposta: {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Erro ao converter texto em áudio: {e}")
            return None

    def get_voice_info(self):
        """
        Obtém informações sobre a voz configurada
        """
        try:
            if not self.api_key or not self.voice_id:
                return None
                
            url = f"{self.base_url}/voices/{self.voice_id}"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Erro ao obter informações da voz: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Erro ao obter informações da voz: {e}")
            return None

# Instância global para uso no bot
elevenlabs_voice = ElevenlabsVoice()

def generate_voice_response(text, output_path=None):
    """Função wrapper para compatibilidade com o código existente"""
    return elevenlabs_voice.text_to_speech(text, output_path)

def get_voice_info():
    """Função wrapper para obter informações da voz"""
    return elevenlabs_voice.get_voice_info()

def test_elevenlabs():
    """
    Testa a integração com ElevenLabs
    """
    logging.info("Testando integração com ElevenLabs...")
    
    try:
        # Testar informações da voz
        logging.info("Informações da voz configurada:")
        voice_info = get_voice_info()
        if voice_info:
            logging.info(f"Nome: {voice_info.get('name', 'N/A')}")
            logging.info(f"ID: {voice_info.get('voice_id', 'N/A')}")
            logging.info(f"Categoria: {voice_info.get('category', 'N/A')}")
        
        # Testar conversão de texto
        test_text = "Olá! Aqui é o Endrigo. Este é um teste da minha voz clonada para o WhatsApp."
        logging.info(f"Testando conversão de texto: {test_text}")
        audio_path = generate_voice_response(test_text)
        
        if audio_path:
            logging.info("Áudio gerado com sucesso!")
            logging.info(f"Arquivo salvo em: {audio_path}")
            
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(audio_path)
            logging.info(f"Tamanho do arquivo: {file_size} bytes")
            
            return audio_path
        else:
            logging.error("Falha ao gerar áudio")
            return None
            
    except Exception as e:
        logging.error(f"Erro no teste: {e}")
        return None