from config.ai_config import get_openai_client, format_success_response, format_error_response, GPT_CONFIG

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
        openai = get_openai_client()
        
        # Generate SEO title
        title_prompt = f"""Create an SEO-optimized title based on this image context and alt text:

Context: {context}
Alt Text: {alt_text}

Requirements:
1. Maximum 60 characters
2. Include key descriptive elements
3. Use proper capitalization
4. Make it compelling and descriptive
5. Focus on the main subject/theme"""

        title_response = openai.ChatCompletion.create(
            model=GPT_CONFIG["model"],
            messages=[
                {"role": "system", "content": "You are an SEO expert that creates optimized titles."},
                {"role": "user", "content": title_prompt}
            ],
            temperature=0.7,
            max_tokens=60
        )
        
        seo_title = title_response.choices[0].message['content'].strip()
        
        # Generate detailed sections
        sections_prompt = f"""Generate a detailed product description with the following sections based on this image:

Context: {context}
Alt Text: {alt_text}

Required Sections:
1. About: A compelling product overview (2-3 sentences)
2. Technical: Key technical specifications or features (3-4 bullet points)
3. Additional: Extra features or use cases (2-3 bullet points)

Format each section with clear headers and bullet points where appropriate."""

        sections_response = openai.ChatCompletion.create(
            model=GPT_CONFIG["model"],
            messages=[
                {"role": "system", "content": "You are an expert product copywriter focusing on SEO-optimized content."},
                {"role": "user", "content": sections_prompt}
            ],
            temperature=0.7,
            max_tokens=GPT_CONFIG["max_tokens"]
        )
        
        sections_text = sections_response.choices[0].message['content'].strip()
        
        # Parse sections
        sections = {}
        current_section = None
        current_content = []
        
        for line in sections_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith(('about:', 'technical:', 'additional:')):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.split(':')[0].lower()
                current_content = []
            else:
                current_content.append(line)
                
        if current_section:
            sections[current_section] = '\n'.join(current_content)
            
        return format_success_response({
            'title': seo_title,
            'sections': sections
        })
        
    except Exception as e:
        return format_error_response(
            error_message=f"Error generating SEO description: {str(e)}",
            error_code="SEO_GENERATION_ERROR"
        ) 