import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from app.services.text_service import generate_context, enhance_context, analyze_sentiment
from app.services.image_service import image_processor

class AdvancedImageProcessor:
    def __init__(self):
        self.image = None
        self.image_array = None
        self.color_clusters = 5  # Number of dominant colors to detect

    def load_image(self, image_path):
        """Load and prepare image for processing"""
        try:
            self.image = Image.open(image_path)
            # Convert image to RGB mode if it isn't already
            if self.image.mode != 'RGB':
                self.image = self.image.convert('RGB')
            self.image_array = np.array(self.image)
            return self.image, self.image_array
        except Exception as e:
            raise ValueError(f"Error loading image: {str(e)}")

    def generate_image_context(self):
        """Generate BLIP description for the image"""
        try:
            if self.image is None:
                raise ValueError("No image loaded")
            
            alt_text = image_processor.generate_alt_text(self.image)
            context_result = generate_context(alt_text)
            
            if not context_result['success']:
                raise ValueError(context_result['error'])
                
            return context_result['data']['context']
        except Exception as e:
            raise ValueError(f"Error generating image context: {str(e)}")

    def generate_enhanced_text(self, base_description):
        """Generate enhanced description using GPT"""
        try:
            enhanced_result = enhance_context(base_description)
            if not enhanced_result['success']:
                raise ValueError(enhanced_result['error'])
            
            # Extract enhanced text from the correct response structure
            if 'data' in enhanced_result and 'enhanced_context' in enhanced_result['data']:
                return enhanced_result['data']['enhanced_context']
            elif 'data' in enhanced_result and 'context' in enhanced_result['data']:
                return enhanced_result['data']['context']
            else:
                raise ValueError("Enhanced text not found in response")
                
        except Exception as e:
            raise ValueError(f"Error generating enhanced text: {str(e)}")

    def analyze_colors(self):
        """Analyze color distribution and dominant colors"""
        try:
            if self.image_array is None:
                raise ValueError("No image loaded")

            # Reshape the image array for color analysis
            pixels = self.image_array.reshape(-1, 3)
            
            # Create color histogram
            plt.figure(figsize=(8, 4))
            hist_data = np.mean(pixels, axis=0)
            plt.plot(range(3), hist_data, marker='o')
            plt.xticks(range(3), ['R', 'G', 'B'])
            plt.title('Color Distribution')
            plt.grid(True)
            hist_fig = plt.gcf()
            plt.close()

            # Find dominant colors using K-means
            kmeans = KMeans(n_clusters=self.color_clusters, random_state=42)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_
            
            # Calculate color percentages
            labels = kmeans.labels_
            unique_labels, label_counts = np.unique(labels, return_counts=True)
            percentages = (label_counts / len(labels)) * 100
            
            # Sort colors by percentage
            sorted_indices = np.argsort(percentages)[::-1]
            colors = colors[sorted_indices]
            percentages = percentages[sorted_indices]
            
            # Create pie chart of dominant colors
            plt.figure(figsize=(6, 6))
            
            # Convert colors to RGB format for plotting
            rgb_colors = colors / 255.0
            
            # Create pie chart with percentage labels
            patches, texts, autotexts = plt.pie(percentages, 
                                              colors=rgb_colors, 
                                              autopct='%1.1f%%',
                                              labels=[f'Color {i+1}' for i in range(len(colors))])
            
            plt.title('Dominant Colors')
            
            # Format percentage texts
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(8)
            
            pie_fig = plt.gcf()
            plt.close()

            # Convert color data for JSON response
            color_data = {
                'bins': list(range(3)),  # R, G, B channels
                'distribution': hist_data.tolist(),  # Color distribution data
                'dominant_colors': colors.astype(int).tolist(),  # RGB values of dominant colors
                'percentages': percentages.tolist()  # Percentage of each dominant color
            }

            return hist_fig, pie_fig, color_data
        except Exception as e:
            logger.error(f"Color analysis error details: {str(e)}")
            raise ValueError(f"Error analyzing colors: {str(e)}")

    def sentiment_analysis(self, text):
        """Analyze sentiment of the description"""
        try:
            sentiment_result = analyze_sentiment(text)
            if not sentiment_result['success']:
                raise ValueError(sentiment_result['error'])
                
            sentiment_data = sentiment_result['data']['sentiment']
            return pd.DataFrame([{
                'Sentiment': sentiment_data['category'],
                'Confidence': sentiment_data['score']
            }])
        except Exception as e:
            raise ValueError(f"Error analyzing sentiment: {str(e)}") 