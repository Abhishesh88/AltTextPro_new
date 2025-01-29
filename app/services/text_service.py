from nltk.sentiment.vader import SentimentIntensityAnalyzer
import httpx
from config.ai_config import get_openai_client, format_success_response, format_error_response, GPT_CONFIG
import logging

logger = logging.getLogger(__name__)

def generate_context(alt_text):
    """
    Generates context from alt text using OpenAI.
    Args:
        alt_text (str): Alt text to generate context from
    Returns:
        dict: Response containing generated context
    """
    prompt = f"Generate a brief context (maximum 70 words) for this image description:\n\n{alt_text}"
    try:
        openai = get_openai_client()
        response = openai.ChatCompletion.create(
            model=GPT_CONFIG["model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise context for images. Keep responses under 50 words."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=GPT_CONFIG["temperature"]
        )
        context = response.choices[0].message['content'].strip()
        words = context.split()
        if len(words) > 70:
            context = ' '.join(words[:70]) + '...'
        return format_success_response({'context': context})
    except Exception as e:
        return format_error_response(
            error_message=f"Error generating context: {str(e)}",
            error_code="CONTEXT_GENERATION_ERROR"
        )

def enhance_context(context):
    """
    Enhances the context with additional details.
    Args:
        context (str): Original context to enhance
    Returns:
        dict: Response containing enhanced context
    """
    try:
        openai = get_openai_client()
        prompt = f"""Enhance this context with more descriptive details while maintaining accuracy:

Original: {context}

Requirements:
1. Add sensory details
2. Include specific measurements or technical details if applicable
3. Maintain factual accuracy
4. Keep the enhanced version under 100 words"""

        response = openai.ChatCompletion.create(
            model=GPT_CONFIG["model"],
            messages=[
                {"role": "system", "content": "You are a detail-oriented writer that enhances descriptions while maintaining accuracy."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        enhanced = response.choices[0].message['content'].strip()
        return format_success_response({'enhanced_context': enhanced})
    except Exception as e:
        return format_error_response(
            error_message=f"Error enhancing context: {str(e)}",
            error_code="CONTEXT_ENHANCEMENT_ERROR"
        )

def social_media_caption(context):
    """
    Generates social media caption with hashtags.
    Args:
        context (str): Context to generate caption from
    Returns:
        dict: Response containing caption and hashtags
    """
    try:
        openai = get_openai_client()
        prompt = f"""Create an engaging social media caption with relevant hashtags based on this context:

Context: {context}

Requirements:
1. Engaging and conversational tone
2. Include 3-5 relevant hashtags
3. Maximum 2-3 sentences
4. Include emojis where appropriate"""

        response = openai.ChatCompletion.create(
            model=GPT_CONFIG["model"],
            messages=[
                {"role": "system", "content": "You are a social media expert that creates engaging captions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.8
        )
        
        caption = response.choices[0].message['content'].strip()
        return format_success_response({'caption': caption})
    except Exception as e:
        return format_error_response(
            error_message=f"Error generating social media caption: {str(e)}",
            error_code="CAPTION_GENERATION_ERROR"
        )

def analyze_sentiment(text):
    """
    Analyzes sentiment of text using VADER.
    Args:
        text (str): Text to analyze
    Returns:
        dict: Response containing sentiment analysis
    """
    try:
        if not text:
            return format_error_response(
                error_message="No text provided for sentiment analysis",
                error_code="EMPTY_TEXT_ERROR"
            )

        try:
            analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            logger.error(f"Error initializing sentiment analyzer: {str(e)}")
            return format_error_response(
                error_message="Error initializing sentiment analyzer. Please ensure NLTK data is properly installed.",
                error_code="SENTIMENT_INIT_ERROR"
            )

        try:
            scores = analyzer.polarity_scores(text)
        except Exception as e:
            logger.error(f"Error calculating sentiment scores: {str(e)}")
            return format_error_response(
                error_message="Error calculating sentiment scores",
                error_code="SENTIMENT_CALCULATION_ERROR"
            )
        
        # Determine sentiment category
        compound = scores['compound']
        if compound >= 0.05:
            category = 'Positive'
        elif compound <= -0.05:
            category = 'Negative'
        else:
            category = 'Neutral'
            
        return format_success_response({
            'sentiment': {
                'score': compound,
                'category': category,
                'details': scores
            }
        })
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return format_error_response(
            error_message=f"Error analyzing sentiment: {str(e)}",
            error_code="SENTIMENT_ANALYSIS_ERROR"
        )

def analyze_medical_image(image, alt_text):
    """
    Analyzes medical image and generates detailed report.
    Args:
        image (PIL.Image): Medical image to analyze
        alt_text (str): Generated alt text of the image
    Returns:
        dict: Response containing medical analysis
    """
    try:
        if not image or not alt_text:
            return format_error_response(
                error_message="Image and alt text are required for analysis",
                error_code="MISSING_INPUT"
            )

        openai = get_openai_client()
        prompt = f"""Analyze this medical image description and provide a detailed medical report:

Image Description: {alt_text}

Please provide a comprehensive analysis following this exact format:

1. Key Findings:
- List all visible anatomical structures
- Note any abnormalities or unusual patterns
- Describe tissue characteristics and density variations
- Identify any visible medical devices or artifacts
- Highlight areas of particular interest

2. Potential Observations:
- Describe possible interpretations of the findings
- Note any patterns consistent with common conditions
- Consider differential possibilities
- Mention any limitations in the analysis
- Indicate areas that may need closer examination

3. Recommendations:
- Suggest appropriate follow-up imaging if needed
- Recommend additional tests or examinations if relevant
- Provide general guidance for healthcare providers
- Note any urgent findings requiring immediate attention
- Suggest documentation and monitoring protocols

Please maintain a professional, medical tone and be specific with anatomical terminology.
If you cannot make specific observations, please provide general anatomical descriptions and standard medical imaging protocols."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a medical imaging specialist providing detailed analysis. Remember to:
                    - Use precise medical terminology
                    - Be thorough but concise
                    - Maintain professional objectivity
                    - Acknowledge limitations
                    - Focus on observable findings
                    - Avoid definitive diagnoses
                    - Consider multiple interpretations
                    - Always provide complete analysis even if limited information"""
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.4
        )
        
        analysis = response.choices[0].message['content'].strip()
        
        # Parse sections
        sections = {}
        current_section = None
        current_content = []
        confidence_score = 0.7  # Base confidence score
        
        for line in analysis.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith(('1. Key Findings:', '2. Potential Observations:', '3. Recommendations:')):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.split(':')[1].strip().lower() if ':' in line else line.lower()
                current_content = []
            else:
                current_content.append(line)
                
        if current_section:
            sections[current_section] = '\n'.join(current_content)
            
        # Ensure all sections exist with defaults
        if not sections.get('key findings'):
            sections['key findings'] = "Standard medical image analysis protocol should be followed. Detailed examination of anatomical structures is recommended."
            
        if not sections.get('potential observations'):
            sections['potential observations'] = "Further clinical correlation and detailed examination is recommended for accurate interpretation."
            
        if not sections.get('recommendations'):
            sections['recommendations'] = "Follow standard medical imaging protocols. Consult with healthcare providers for proper interpretation and next steps."
            
        # Adjust confidence score based on content
        if sections:
            # More detailed findings increase confidence
            findings_length = len(sections.get('key findings', '').split())
            confidence_score += min(0.1, findings_length / 1000)
            
            # More recommendations suggest better analysis
            recommendations_length = len(sections.get('recommendations', '').split())
            confidence_score += min(0.1, recommendations_length / 500)
            
            # Cap confidence score at 0.95
            confidence_score = min(0.95, confidence_score)
            
        return format_success_response({
            'findings': sections['key findings'],
            'diagnosis': sections['potential observations'],
            'recommendations': sections['recommendations'],
            'confidence_score': confidence_score
        })
        
    except Exception as e:
        logger.error(f"Error analyzing medical image: {str(e)}")
        return format_error_response(
            error_message=f"Error analyzing medical image: {str(e)}",
            error_code="MEDICAL_ANALYSIS_ERROR"
        )