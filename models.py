import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    message_type = Column(String(10), default='text')  # 'text' or 'audio'
    transcribed_text = Column(Text)  # Para mensagens de áudio
    thread_id = Column(String(100))  # ID do thread OpenAI
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.phone_number}>'

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    first_message_date = Column(DateTime, default=datetime.utcnow)
    last_message_date = Column(DateTime, default=datetime.utcnow)
    total_messages = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f'<User {self.phone_number}>'