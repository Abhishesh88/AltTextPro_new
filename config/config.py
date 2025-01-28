import os
from dotenv import load_dotenv

load_dotenv()  # Add this at the top of the file

# Flask Config
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# OpenAI Config
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Model Config
BLIP_MODEL = "Salesforce/blip-image-captioning-base" 