import os
import logging
import tempfile
import requests
from twilio.rest import Client

# Twilio credentials
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "your-twilio-account-sid")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "your-twilio-auth-token")

def download_media_file(media_url):
    """Download media file from Twilio and save to temporary file"""
    try:
        logging.info(f"Downloading media file from: {media_url}")
        
        # Twilio requires authentication for media downloads
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Download the media file
        response = requests.get(media_url, auth=auth, stream=True)
        response.raise_for_status()
        
        # Determine file extension based on content type
        content_type = response.headers.get('content-type', '')
        if 'ogg' in content_type:
            suffix = '.ogg'
        elif 'mp3' in content_type:
            suffix = '.mp3'
        elif 'wav' in content_type:
            suffix = '.wav'
        elif 'mp4' in content_type:
            suffix = '.mp4'
        else:
            suffix = '.audio'
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        logging.info(f"Media file downloaded to: {temp_file_path}")
        return temp_file_path
        
    except Exception as e:
        logging.error(f"Error downloading media file: {str(e)}")
        return None

def send_whatsapp_message(to_number, message):
    """Send WhatsApp message via Twilio (optional utility function)"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Twilio Sandbox number
            to=f'whatsapp:{to_number}'
        )
        
        logging.info(f"Message sent with SID: {message.sid}")
        return message.sid
        
    except Exception as e:
        logging.error(f"Error sending WhatsApp message: {str(e)}")
        raise e
