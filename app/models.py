"""
Modelos do banco de dados
"""
from datetime import datetime
from app import db

class User(db.Model):
    """Modelo para usuários do WhatsApp"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    total_messages = db.Column(db.Integer, default=0, nullable=False)
    first_message_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.phone_number}>'

class Conversation(db.Model):
    """Modelo para conversas"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(10), default='text')  # 'text' ou 'audio'
    transcribed_text = db.Column(db.Text)  # Para mensagens de áudio
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.phone_number}>'