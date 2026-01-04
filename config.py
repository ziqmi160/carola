import os
from dotenv import load_dotenv

load_dotenv()

# Oracle Database Configuration
DB_CONFIG = {
    'user': 'carola',
    'password': 'carola',
    'dsn': 'localhost:1521/FREEPDB1'
}

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

