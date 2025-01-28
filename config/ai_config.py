"""
Centralized configuration for AI services
"""
import openai
from config.config import OPENAI_API_KEY

def configure_ai():
    """Configure AI services with appropriate API keys and settings"""
    openai.api_key = OPENAI_API_KEY

def get_openai_client():
    """Get configured OpenAI client"""
    configure_ai()
    return openai

# Standard model configurations
GPT_CONFIG = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 150
}

# Response formatting helpers
def format_success_response(data):
    """Format successful API response"""
    return {
        'success': True,
        'data': data,
        'error': None,
        'code': 'SUCCESS'
    }

def format_error_response(error_message, error_code, details=None):
    """Format error API response"""
    return {
        'success': False,
        'data': None,
        'error': error_message,
        'code': error_code,
        'details': details
    } 