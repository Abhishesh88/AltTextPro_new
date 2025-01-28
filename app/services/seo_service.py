import openai
from config.config import OPENAI_API_KEY

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

def generate_seo_description(context, alt_text):
    """
    Generates a detailed product description and SEO title with improved formatting.
    
    Args:
        context (str): Context of the image
        alt_text (str): Generated alt text of the image
        
    Returns:
        dict: Contains formatted description and SEO title
    """
    try:
        # Generate SEO title first with direct context
        title_prompt = f"""Create an SEO-optimized title based on this image context and alt text:

Context: {context}
Alt Text: {alt_text}

Requirements:
1. Maximum 60 characters
2. Include key descriptive elements
3. Use proper capitalization
4. Make it compelling and descriptive
5. Focus on the main subject/theme
6. Include any relevant specifications

Example format: "Professional DSLR Camera with 24MP Sensor | Canon EOS 5D"
"""

        title_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an SEO expert. Create compelling, keyword-rich titles that follow SEO best practices. Always return a title, even if information is limited."
                },
                {"role": "user", "content": title_prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        seo_title = title_response.choices[0].message['content'].strip()

        # Generate detailed description
        description_prompt = f"""Based on this image context and alt text, generate a structured product description:

Context: {context}
Alt Text: {alt_text}

Please provide the description in the following exact format:

About this item:
• [First key feature]
• [Second key feature]
• [Third key feature]

Technical Specifications:
• [First specification]
• [Second specification]
• [Third specification]

Additional Features:
• [First additional feature]
• [Second additional feature]
• [Third additional feature]

Requirements:
- Use bullet points with the • character (not hyphens or asterisks)
- Each bullet point should be a complete, informative sentence
- Include specific technical details and measurements where applicable
- Maintain consistent grammatical structure across bullet points
- Ensure each section has at least 3 bullet points
- Total description should be minimum 80 words
"""

        description_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a product description expert. Follow these guidelines:
                    - Always use bullet points with the • character
                    - Maintain consistent formatting
                    - Each bullet point must be a complete sentence
                    - Focus on technical specifications and measurable features
                    - Use parallel structure in bullet points
                    - Separate content into distinct sections as specified in the prompt"""
                },
                {"role": "user", "content": description_prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        detailed_description = description_response.choices[0].message['content'].strip()

        # Post-process the description to ensure proper formatting
        sections = detailed_description.split('\n\n')
        formatted_sections = []
        
        for section in sections:
            if ':' in section:
                title, content = section.split(':', 1)
                # Format bullet points properly
                bullet_points = [point.strip() for point in content.split('\n') if point.strip()]
                formatted_points = [f"• {point.lstrip('•').strip()}" for point in bullet_points]
                formatted_section = f"{title}:\n" + '\n'.join(formatted_points)
                formatted_sections.append(formatted_section)
        
        formatted_description = '\n\n'.join(formatted_sections)

        # Ensure we have a title
        if not seo_title:
            # Generate a simple title from context or alt text
            seo_title = context.split('.')[0] if context else alt_text.split('.')[0]
            # Capitalize the first letter of each word
            seo_title = ' '.join(word.capitalize() for word in seo_title.split())

        return {
            'description': formatted_description,
            'title': seo_title,
            'sections': {
                'about': formatted_sections[0] if len(formatted_sections) > 0 else "",
                'technical': formatted_sections[1] if len(formatted_sections) > 1 else "",
                'additional': formatted_sections[2] if len(formatted_sections) > 2 else ""
            }
        }
        
    except Exception as e:
        return {'error': str(e)} 