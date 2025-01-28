from nltk.sentiment.vader import SentimentIntensityAnalyzer
import httpx
from config.ai_config import get_openai_client, format_success_response, format_error_response, GPT_CONFIG

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
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        
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
        openai = get_openai_client()
        prompt = f"""Analyze this medical image description and provide a detailed medical report:

Image Description: {alt_text}

Required Sections:
1. Key Findings
2. Potential Diagnosis
3. Recommendations
4. Confidence Level (0-100%)"""

        response = openai.ChatCompletion.create(
            model=GPT_CONFIG["model"],
            messages=[
                {"role": "system", "content": "You are a medical imaging expert providing detailed analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )
        
        analysis = response.choices[0].message['content'].strip()
        
        # Parse sections
        sections = {}
        current_section = None
        current_content = []
        confidence_score = 0
        
        for line in analysis.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if any(line.lower().startswith(s) for s in ['key findings:', 'potential diagnosis:', 'recommendations:', 'confidence level:']):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.split(':')[0].lower().replace(' ', '_')
                current_content = []
                
                # Extract confidence score if present
                if line.lower().startswith('confidence level:'):
                    try:
                        confidence_text = line.split(':')[1].strip()
                        confidence_score = int(confidence_text.replace('%', '')) / 100
                    except:
                        confidence_score = 0.5
            else:
                current_content.append(line)
                
        if current_section:
            sections[current_section] = '\n'.join(current_content)
            
        return format_success_response({
            'findings': sections.get('key_findings', ''),
            'diagnosis': sections.get('potential_diagnosis', ''),
            'recommendations': sections.get('recommendations', ''),
            'confidence_score': confidence_score
        })
    except Exception as e:
        return format_error_response(
            error_message=f"Error analyzing medical image: {str(e)}",
            error_code="MEDICAL_ANALYSIS_ERROR"
        )