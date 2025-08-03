import os
import logging
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Import and register webhook blueprint
from webhook import webhook_bp
app.register_blueprint(webhook_bp)

@app.route('/')
def index():
    """Status page to verify the webhook is running"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Endrigo Digital WhatsApp Bot"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
