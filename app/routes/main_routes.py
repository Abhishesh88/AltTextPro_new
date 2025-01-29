from flask import Blueprint, request, jsonify, render_template, send_file, current_app
from werkzeug.utils import secure_filename
import os
import tempfile
from PIL import Image
from gtts import gTTS
from datetime import datetime
import requests
import time
import logging

from app.utils.file_utils import allowed_file, validate_image
from app.services.image_service import image_processor
from app.services.text_service import (
    generate_context,
    enhance_context,
    social_media_caption,
    analyze_sentiment,
    analyze_medical_image
)
from app.services.advanced_image_service import AdvancedImageProcessor
from app.services.seo_service import generate_seo_description
from config.config import UPLOAD_FOLDER

logger = logging.getLogger(__name__)

# Define allowed extensions for medical images
ALLOWED_MEDICAL_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff', 'dcm'}

main = Blueprint('main', __name__)

@main.route('/')
def landing():
    return render_template('landing.html')

@main.route('/social-media', methods=['GET', 'POST'])
def social_media():
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
            
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
                
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Please upload a PNG, JPG, JPEG, or GIF'}), 400
            
            # Validate image
            if not validate_image(file.stream):
                return jsonify({'error': 'Invalid image file'}), 400
                
            # Save and process image
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                image = Image.open(filepath)
                alt_text = image_processor.generate_alt_text(image)
                context = generate_context(alt_text)
                caption = social_media_caption(context)
                sentiment_result = analyze_sentiment(caption)
                hashtags = generate_hashtags(context)
                
                return jsonify({
                    'caption': caption,
                    'hashtags': hashtags,
                    'sentiment': sentiment_result
                })
                
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                return jsonify({'error': 'Error processing image. Please try again.'}), 500
            
            finally:
                # Clean up uploaded file
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as e:
                    print(f"Error removing file: {str(e)}")
        
        except Exception as e:
            print(f"Server error: {str(e)}")
            return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500
            
    return render_template('social_media.html')

@main.route('/seo', methods=['GET', 'POST'])
def seo():
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No image file provided',
                    'code': 'NO_IMAGE'
                }), 400
            
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No selected file',
                    'code': 'EMPTY_FILE'
                }), 400
                
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type. Please upload a PNG, JPG, JPEG, or GIF',
                    'code': 'INVALID_TYPE'
                }), 400
            
            # Validate image
            if not validate_image(file.stream):
                return jsonify({
                    'success': False,
                    'error': 'Invalid image file',
                    'code': 'INVALID_IMAGE'
                }), 400
                
            # Save and process image
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                image = Image.open(filepath)
                alt_text = image_processor.generate_alt_text(image)
                context = generate_context(alt_text)
                seo_description = generate_seo_description(context, alt_text)
                
                return jsonify(seo_description)
                
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Error processing image. Please try again.',
                    'code': 'PROCESSING_ERROR'
                }), 500
            
            finally:
                # Clean up uploaded file
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as e:
                    print(f"Error removing file: {str(e)}")
        
        except Exception as e:
            print(f"Server error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'An unexpected error occurred. Please try again.',
                'code': 'SERVER_ERROR'
            }), 500
            
    return render_template('seo.html')

@main.route('/general', methods=['GET', 'POST'])
def general():
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
            
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
                
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Please upload a PNG, JPG, JPEG, or GIF'}), 400
            
            # Validate image
            if not validate_image(file.stream):
                return jsonify({'error': 'Invalid image file'}), 400
                
            # Save and process image
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                image = Image.open(filepath)
                alt_text = image_processor.generate_alt_text(image)
                context = generate_context(alt_text)
                enhanced_description = enhance_context(context)
                
                return jsonify({
                    'alt_text': alt_text,
                    'context': context,
                    'enhanced_description': enhanced_description
                })
                
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                return jsonify({'error': 'Error processing image. Please try again.'}), 500
            
            finally:
                # Clean up uploaded file
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as e:
                    print(f"Error removing file: {str(e)}")
        
        except Exception as e:
            print(f"Server error: {str(e)}")
            return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500
            
    return render_template('general.html')

@main.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        text = request.json.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Temporary file for the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts = gTTS(text=text, lang='en')
        tts.save(temp_file.name)
        
        return send_file(
            temp_file.name,
            mimetype='audio/mp3',
            as_attachment=True,
            download_name='speech.mp3'
        )
    except Exception as e:
        print(f"Error generating speech: {str(e)}")  # Add logging
        return jsonify({'error': 'Error generating speech. Please try again.'}), 500

@main.route('/medical-image-analysis', methods=['GET'])
def medical_analysis():
    """
    Route handler for medical analysis page
    """
    return render_template('medical.html')

@main.route('/medical-image-analysis', methods=['POST'])
def analyze_medical_image_route():
    """
    Route handler for medical image analysis
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded',
                'error_code': 'NO_FILE'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'error_code': 'EMPTY_FILENAME'
            }), 400

        # Check file extension
        if not allowed_file(file.filename, ALLOWED_MEDICAL_EXTENSIONS):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Supported types: {", ".join(ALLOWED_MEDICAL_EXTENSIONS)}',
                'error_code': 'INVALID_FILE_TYPE'
            }), 400

        # Validate uploaded file stream first
        if not validate_image(file.stream):
            return jsonify({
                'success': False,
                'error': 'Invalid or corrupted image file',
                'error_code': 'INVALID_IMAGE'
            }), 400
            
        # Reset file stream position after validation
        file.stream.seek(0)

        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        try:
            # Save the image
            filename = secure_filename(file.filename)
            filepath = os.path.join(temp_dir, filename)
            file.save(filepath)

            # Open image for processing
            try:
                image = Image.open(filepath)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Generate alt text
                alt_text = image_processor.generate_alt_text(image)
                if not isinstance(alt_text, str) or not alt_text.strip():
                    raise ValueError("Failed to generate image description")
                
                # Perform medical analysis
                analysis_result = analyze_medical_image(image, alt_text)
                if not analysis_result['success']:
                    raise ValueError(analysis_result.get('error', 'Failed to analyze medical image'))
                
                # Extract data with defaults for missing fields
                data = analysis_result.get('data', {})
                
                # Validate required fields and provide defaults
                findings = data.get('findings')
                if not findings or not isinstance(findings, str):
                    findings = "Standard medical image analysis protocol should be followed. Detailed examination of anatomical structures is recommended."
                    
                diagnosis = data.get('diagnosis')
                if not diagnosis or not isinstance(diagnosis, str):
                    diagnosis = "Further clinical correlation and detailed examination is recommended for accurate interpretation."
                    
                recommendations = data.get('recommendations')
                if not recommendations or not isinstance(recommendations, str):
                    recommendations = "Follow standard medical imaging protocols. Consult with healthcare providers for proper interpretation and next steps."
                
                confidence_score = float(data.get('confidence_score', 0.7))  # Default confidence score
                
                return jsonify({
                    'success': True,
                    'data': {
                        'alt_text': alt_text,
                        'findings': findings,
                        'diagnosis': diagnosis,
                        'recommendations': recommendations,
                        'confidence_score': confidence_score
                    }
                }), 200

            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'error_code': 'PROCESSING_ERROR'
                }), 400

        finally:
            # Clean up temporary files
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"Error cleaning up temporary files: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error in medical analysis route: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred during analysis',
            'error_code': 'SERVER_ERROR'
        }), 500

@main.route('/image-analyzer', methods=['GET', 'POST'])
def image_analyzer():
    if request.method == 'POST':
        try:
            # Check for file upload
            if 'image' in request.files:
                file = request.files['image']
                if file.filename == '':
                    return jsonify({
                        'success': False,
                        'error': 'No selected file',
                        'code': 'EMPTY_FILE'
                    }), 400
                    
                if not allowed_file(file.filename):
                    return jsonify({
                        'success': False,
                        'error': 'Invalid file type. Please upload a PNG, JPG, JPEG, or GIF',
                        'code': 'INVALID_TYPE'
                    }), 400
                
                # Validate image
                if not validate_image(file.stream):
                    return jsonify({
                        'success': False,
                        'error': 'Invalid image file',
                        'code': 'INVALID_IMAGE'
                    }), 400
                    
                # Save and process image
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
            # Check for image URL
            elif 'image_url' in request.form:
                image_url = request.form['image_url']
                try:
                    # Download image from URL
                    response = requests.get(image_url)
                    if response.status_code != 200:
                        return jsonify({
                            'success': False,
                            'error': 'Failed to download image from URL',
                            'code': 'URL_DOWNLOAD_ERROR'
                        }), 400
                    
                    # Save temporary file
                    filename = f"url_image_{int(time.time())}.jpg"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                        
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'Error processing URL: {str(e)}',
                        'code': 'URL_PROCESSING_ERROR'
                    }), 400
            else:
                return jsonify({
                    'success': False,
                    'error': 'No image file or URL provided',
                    'code': 'NO_INPUT'
                }), 400
            
            try:
                # Process the image
                image = Image.open(filepath)
                alt_text = image_processor.generate_alt_text(image)
                context_result = generate_context(alt_text)
                
                if not context_result['success']:
                    raise Exception(context_result['error'])
                    
                context = context_result['data']['context']
                
                # Get sentiment analysis
                sentiment_result = analyze_sentiment(alt_text)
                if not sentiment_result['success']:
                    raise Exception(sentiment_result['error'])
                    
                sentiment_data = sentiment_result['data']['sentiment']
                
                return jsonify({
                    'success': True,
                    'data': {
                        'alt_text': alt_text,
                        'context': context,
                        'sentiment': {
                            'score': sentiment_data['score'],
                            'label': sentiment_data['category'],
                            'details': f"The description has a {sentiment_data['category'].lower()} tone with {sentiment_data['score']*100:.1f}% confidence."
                        }
                    }
                })
                
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Error processing image. Please try again.',
                    'code': 'PROCESSING_ERROR'
                }), 500
            
            finally:
                # Clean up uploaded file
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as e:
                    print(f"Error removing file: {str(e)}")
        
        except Exception as e:
            print(f"Server error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'An unexpected error occurred. Please try again.',
                'code': 'SERVER_ERROR'
            }), 500
            
    return render_template('image_analyzer.html')

def generate_hashtags(context):
    """Generate relevant hashtags from the context using OpenAI"""
    try:
        # Use the existing social_media_caption function but extract hashtags
        caption_with_hashtags = social_media_caption(context)
        words = caption_with_hashtags.split()
        hashtags = [word for word in words if word.startswith('#')]
        
        # If no hashtags found in the caption, generate basic ones from context
        if not hashtags:
            words = context.split()
            hashtags = [f"#{word.lower()}" for word in words if len(word) > 3][:5]
        
        return " ".join(hashtags)
    except Exception as e:
        print(f"Error generating hashtags: {str(e)}")  # Add logging
        return ""

@main.route('/advanced-analysis', methods=['GET'])
def advanced_analysis():
    """
    Route handler for advanced analysis page
    """
    return render_template('advanced_analysis.html')

@main.route('/advanced-analysis', methods=['POST'])
def process_advanced_analysis():
    """
    Route handler for advanced image analysis
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded',
                'error_code': 'NO_FILE'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'error_code': 'EMPTY_FILENAME'
            }), 400

        # Check file extension
        if not allowed_file(file.filename, {'png', 'jpg', 'jpeg'}):
            return jsonify({
                'success': False,
                'error': 'File type not allowed. Supported types: PNG, JPG, JPEG',
                'error_code': 'INVALID_FILE_TYPE'
            }), 400

        # Validate uploaded file stream first
        if not validate_image(file.stream):
            return jsonify({
                'success': False,
                'error': 'Invalid or corrupted image file',
                'error_code': 'INVALID_IMAGE'
            }), 400
            
        # Reset file stream position after validation
        file.stream.seek(0)

        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        try:
            # Save the image
            filename = secure_filename(file.filename)
            filepath = os.path.join(temp_dir, filename)
            file.save(filepath)

            # Process image
            try:
                processor = AdvancedImageProcessor()
                
                # Load and validate image
                try:
                    image, image_array = processor.load_image(filepath)
                    if image is None or image_array is None:
                        raise ValueError("Failed to load image")
                except Exception as e:
                    logger.error(f"Error loading image: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to load image file',
                        'error_code': 'IMAGE_LOAD_ERROR'
                    }), 400
                
                # Generate BLIP description with error handling
                try:
                    blip_description = processor.generate_image_context()
                    if not blip_description or not isinstance(blip_description, str):
                        raise ValueError("Invalid BLIP description generated")
                except Exception as e:
                    logger.error(f"Error generating BLIP description: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to generate image description',
                        'error_code': 'BLIP_ERROR'
                    }), 400
                
                # Generate enhanced description with error handling
                try:
                    enhanced_description = processor.generate_enhanced_text(blip_description)
                    if not enhanced_description or not isinstance(enhanced_description, str):
                        raise ValueError("Invalid enhanced description generated")
                except Exception as e:
                    logger.error(f"Error generating enhanced description: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to enhance description',
                        'error_code': 'ENHANCEMENT_ERROR'
                    }), 400
                
                # Analyze colors with error handling
                try:
                    color_hist_fig, color_pie_fig, color_data = processor.analyze_colors()
                    if color_hist_fig is None or color_pie_fig is None or color_data is None:
                        raise ValueError("Color analysis failed to generate results")
                except Exception as e:
                    logger.error(f"Error analyzing colors: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to analyze image colors',
                        'error_code': 'COLOR_ANALYSIS_ERROR'
                    }), 400
                
                # Analyze sentiment with error handling
                try:
                    sentiment_df = processor.sentiment_analysis(enhanced_description)
                    if sentiment_df is None or sentiment_df.empty:
                        raise ValueError("Sentiment analysis returned no results")
                        
                    sentiment_data = {
                        'label': sentiment_df['Sentiment'].iloc[0],
                        'confidence': float(sentiment_df['Confidence'].iloc[0])
                    }
                except Exception as e:
                    logger.error(f"Error analyzing sentiment: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to analyze sentiment',
                        'error_code': 'SENTIMENT_ERROR'
                    }), 400
                
                return jsonify({
                    'success': True,
                    'data': {
                        'blip_description': blip_description,
                        'enhanced_description': enhanced_description,
                        'color_analysis': color_data,
                        'sentiment': sentiment_data
                    }
                }), 200

            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'error_code': 'PROCESSING_ERROR'
                }), 400

        finally:
            # Clean up temporary files
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"Error cleaning up temporary files: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error in advanced analysis route: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred during analysis',
            'error_code': 'SERVER_ERROR'
        }), 500 