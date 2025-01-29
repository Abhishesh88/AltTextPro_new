import nltk
import os
import logging

logger = logging.getLogger(__name__)

def initialize_nltk():
    """Download required NLTK data if not already present"""
    try:
        # Set NLTK data path to a directory in our project
        nltk_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'nltk_data')
        os.makedirs(nltk_data_dir, exist_ok=True)
        nltk.data.path.append(nltk_data_dir)

        # Download required NLTK data
        required_packages = ['vader_lexicon']
        for package in required_packages:
            try:
                nltk.data.find(f'sentiment/{package}')
                logger.info(f"NLTK package '{package}' is already downloaded")
            except LookupError:
                logger.info(f"Downloading NLTK package '{package}'...")
                nltk.download(package, download_dir=nltk_data_dir)
                logger.info(f"Successfully downloaded NLTK package '{package}'")
    except Exception as e:
        logger.error(f"Error initializing NLTK: {str(e)}")
        raise 