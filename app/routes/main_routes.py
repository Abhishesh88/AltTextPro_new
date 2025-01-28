from flask import Blueprint, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
from PIL import Image
from gtts import gTTS
from datetime import datetime

from app.utils.file_utils import allowed_file, validate_image
from app.services.image_service import image_processor
from app.services.text_service import (
    generate_context,
    enhance_context,
    social_media_caption,
    analyze_sentiment,
    analyze_medical_image
)
from app.services.seo_service import generate_seo_description
from config.config import UPLOAD_FOLDER

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

@main.route('/medical-image-analysis', methods=['GET', 'POST'])
def medical_image():
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
                    'error': 'Invalid or corrupted image file',
                    'code': 'INVALID_IMAGE'
                }), 400
                
            # Save and process image
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                image = Image.open(filepath)
                alt_text = image_processor.generate_alt_text(image)
                analysis_result = analyze_medical_image(image, alt_text)
                
                return jsonify(analysis_result)
                
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
            
    return render_template('medical.html')

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