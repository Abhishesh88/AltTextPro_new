import openai
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from config.config import OPENAI_API_KEY
import httpx

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

def generate_context(alt_text):
    """Generates context from alt text using OpenAI."""
    prompt = f"Generate a brief context (maximum 70 words) for this image description:\n\n{alt_text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise context for images. Keep responses under 50 words."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        context = response.choices[0].message['content'].strip()
        words = context.split()
        if len(words) > 70:
            context = ' '.join(words[:70]) + '...'
        return context
    except Exception as e:
        return f"Error generating context: {e}"

def enhance_context(context):
    """Enhances the alt text using OpenAI 4 model."""
    prompt = f"Enhance this context of a image into a brief, creative caption (maximum 50 words):\n\n{context}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Keep responses under 30 words."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=75,
            temperature=0.7
        )
        enhanced = response.choices[0].message['content'].strip()
        words = enhanced.split()
        if len(words) > 50:
            enhanced = ' '.join(words[:50]) + '...'
        return enhanced
    except Exception as e:
        return f"Error generating enhanced caption: {e}"

def social_media_caption(context):
    """Enhances the generated context into a social media caption using OpenAI 4 model."""
    prompt = f"Enhance this context of a image into a brief, creative caption along with related hashtags for my social media platform:\n\n{context}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a great social media manager. Keep responses accurate and relevant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=75,
            temperature=0.7
        )
        caption = response.choices[0].message['content'].strip()
        return caption
    except Exception as e:
        return f"Error generating Social Media caption: {e}"

def analyze_sentiment(text):
    """Analyzes the sentiment of the text using VADER Sentiment Analyzer."""
    try:
        if not text or not isinstance(text, str):
            return {
                'category': 'Neutral',
                'score': 50,
                'raw_score': 0,
                'detailed_scores': {'neg': 0, 'neu': 1, 'pos': 0, 'compound': 0}
            }

        sid = SentimentIntensityAnalyzer()
        scores = sid.polarity_scores(text)
        compound_score = scores['compound']
        
        if compound_score >= 0.05:
            category = "Positive"
        elif compound_score <= -0.05:
            category = "Negative"
        else:
            category = "Neutral"
            
        return {
            'category': category,
            'score': (compound_score + 1) * 50,  # Convert to 0-100 scale
            'raw_score': compound_score,
            'detailed_scores': scores
        }
    except Exception as e:
        print(f"Sentiment analysis error: {str(e)}")
        return {
            'category': 'Neutral',
            'score': 50,
            'raw_score': 0,
            'detailed_scores': {'neg': 0, 'neu': 1, 'pos': 0, 'compound': 0}
        }

def analyze_medical_image(image, alt_text):
    """Analyzes medical images using OpenAI GPT-4 for interpretation.
    
    Args:
        image: PIL Image object
        alt_text: String containing the image description
        
    Returns:
        dict: A structured analysis containing findings, diagnosis, recommendations,
              confidence scores, and metadata
    """
    try:
        prompt = f"""Analyze this medical image description and provide a detailed medical analysis:

Image Description: {alt_text}

Please provide a structured analysis with the following sections:

1. Key Findings:
- List the main observations
- Note any abnormalities
- Describe visible patterns or characteristics

2. Potential Diagnosis:
- List possible diagnoses in order of likelihood
- Include confidence level for each diagnosis
- Note any differential diagnoses to consider

3. Recommendations:
- Suggest next steps for diagnosis confirmation
- Recommend additional tests if needed
- Provide general guidance

Important: This is an AI-assisted analysis and should not replace professional medical diagnosis.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a medical image analysis assistant. Follow these guidelines:
                    - Provide detailed, structured analysis
                    - Use precise medical terminology
                    - Include confidence levels for each finding
                    - Maintain professional tone
                    - Emphasize the importance of professional medical review
                    - Structure response in clear sections
                    - List findings in order of significance"""
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=750,
            temperature=0.3
        )
        
        analysis = response.choices[0].message['content'].strip()
        
        # Parse the response into structured sections
        sections = analysis.split('\n\n')
        findings = []
        diagnoses = []
        recommendations = []
        
        current_section = None
        for section in sections:
            if 'Key Findings:' in section:
                current_section = 'findings'
                section_content = section.replace('Key Findings:', '').strip()
                findings = [item.strip('- ').strip() for item in section_content.split('\n') if item.strip('- ').strip()]
            elif 'Potential Diagnosis:' in section:
                current_section = 'diagnosis'
                section_content = section.replace('Potential Diagnosis:', '').strip()
                diagnoses = [item.strip('- ').strip() for item in section_content.split('\n') if item.strip('- ').strip()]
            elif 'Recommendations:' in section:
                current_section = 'recommendations'
                section_content = section.replace('Recommendations:', '').strip()
                recommendations = [item.strip('- ').strip() for item in section_content.split('\n') if item.strip('- ').strip()]
        
        # Calculate confidence scores
        confidence_indicators = {
            'high': ['clear', 'evident', 'definite', 'certain'],
            'medium': ['likely', 'probable', 'suggests', 'indicates'],
            'low': ['possible', 'may', 'could', 'uncertain']
        }
        
        def calculate_confidence(text):
            text = text.lower()
            for level, indicators in confidence_indicators.items():
                if any(indicator in text for indicator in indicators):
                    return {'high': 0.9, 'medium': 0.7, 'low': 0.5}.get(level, 0.7)
            return 0.7
        
        # Structure the final response
        return {
            'findings': findings,
            'diagnosis': diagnoses,
            'recommendations': recommendations,
            'confidence_scores': {
                'findings': calculate_confidence(' '.join(findings)),
                'diagnosis': calculate_confidence(' '.join(diagnoses)),
                'overall': calculate_confidence(analysis)
            },
            'metadata': {
                'model_version': 'gpt-4',
                'analysis_version': '2.0',
                'disclaimer': 'This AI-generated analysis is for informational purposes only and should not replace professional medical diagnosis.'
            }
        }
        
    except Exception as e:
        print(f"Error in medical image analysis: {str(e)}")
        return {
            'findings': ['Error analyzing image'],
            'diagnosis': ['Analysis not available'],
            'recommendations': ['Please try again or consult a medical professional'],
            'confidence_scores': {
                'findings': 0,
                'diagnosis': 0,
                'overall': 0
            },
            'error': str(e),
            'metadata': {
                'error_type': type(e).__name__,
                'disclaimer': 'This AI-generated analysis is for informational purposes only and should not replace professional medical diagnosis.'
            }
        }