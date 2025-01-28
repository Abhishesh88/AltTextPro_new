from transformers import BlipProcessor, BlipForConditionalGeneration
from config.config import BLIP_MODEL

# Initialize BLIP model and processor
processor = BlipProcessor.from_pretrained(BLIP_MODEL)
model = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL)

def generate_alt_text(image):
    """Generates alt text for an image using BLIP model."""
    try:
        # Preprocess the image for BLIP model
        inputs = processor(images=image, return_tensors="pt")
        
        # Generate alt text
        out = model.generate(**inputs)
        
        # Decode the generated text
        alt_text = processor.decode(out[0], skip_special_tokens=True)
        
        return alt_text
    except Exception as e:
        return f"Error generating alt text: {e}" 