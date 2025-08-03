# main.py
from app import create_app

app = create_app()

# Este bloco só é usado se você rodar 'python main.py' localmente.
# No Replit, o Gunicorn é quem manda.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)