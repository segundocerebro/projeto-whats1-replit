import os
import logging
import tempfile
import requests
from flask import Blueprint, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from openai_service import transcribe_audio_message, get_endrigo_response
from twilio_service import download_media_file

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages from Twilio"""
    try:
        logging.info("Received webhook request")
        
        # Get message data from Twilio
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        media_url = request.values.get('MediaUrl0', '')
        media_content_type = request.values.get('MediaContentType0', '')
        
        logging.info(f"Message from {from_number}: {incoming_msg}")
        logging.info(f"Media URL: {media_url}, Content Type: {media_content_type}")
        
        # Create response object
        response = MessagingResponse()
        
        # Process the message
        if media_url and 'audio' in media_content_type:
            # Handle audio message
            logging.info("Processing audio message")
            try:
                # Download and transcribe audio
                audio_file_path = download_media_file(media_url)
                if audio_file_path:
                    transcribed_text = transcribe_audio_message(audio_file_path)
                    logging.info(f"Transcribed text: {transcribed_text}")
                    
                    # Get Endrigo's response to the transcribed text
                    endrigo_response = get_endrigo_response(transcribed_text)
                    
                    # Clean up temp file
                    try:
                        os.unlink(audio_file_path)
                    except:
                        pass
                else:
                    endrigo_response = "Desculpe, não consegui processar o áudio. Tente novamente."
                    
            except Exception as e:
                logging.error(f"Error processing audio: {str(e)}")
                endrigo_response = "Desculpe, houve um erro ao processar seu áudio. Tente enviar uma mensagem de texto."
                
        elif incoming_msg:
            # Handle text message
            logging.info("Processing text message")
            try:
                endrigo_response = get_endrigo_response(incoming_msg)
            except Exception as e:
                logging.error(f"Error getting Endrigo response: {str(e)}")
                endrigo_response = "Desculpe, estou com dificuldades técnicas no momento. Tente novamente em alguns instantes."
        else:
            # No message content
            endrigo_response = "Olá! Sou o Endrigo Digital. Envie uma mensagem de texto ou áudio que eu respondo!"
        
        # Send response back via WhatsApp
        msg = response.message()
        msg.body(endrigo_response)
        
        logging.info(f"Sending response: {endrigo_response}")
        
        return Response(str(response), content_type='application/xml')
        
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        
        # Send error response
        response = MessagingResponse()
        msg = response.message()
        msg.body("Desculpe, houve um erro interno. Tente novamente em alguns instantes.")
        
        return Response(str(response), content_type='application/xml')

@webhook_bp.route('/webhook', methods=['GET'])
def webhook_verification():
    """Handle Twilio webhook verification"""
    return "Endrigo Digital WhatsApp Bot - Webhook Active", 200
