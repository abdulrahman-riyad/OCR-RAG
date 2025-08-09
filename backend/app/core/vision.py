import base64
from openai import OpenAI
from typing import Dict, Any, Optional
import json

from app.config import settings

class VisionAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    async def analyze_image(self, image_path: str, ocr_text: str) -> Dict[str, Any]:
        """Use GPT-4V to understand the image better"""
        
        # For now, return a placeholder if API key is not set
        if settings.OPENAI_API_KEY == "placeholder-openai-key":
            return {
                "enhanced_text": ocr_text,
                "structure": {
                    "has_equations": False,
                    "has_diagrams": False,
                    "has_tables": False,
                    "sections": []
                },
                "suggestions": []
            }
        
        try:
            base64_image = self.encode_image(image_path)
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing handwritten notes. Extract and enhance the text, identify mathematical equations, diagrams, and document structure."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Analyze this handwritten note. The OCR extracted: '{ocr_text}'. Please provide: 1) Enhanced/corrected text, 2) Document structure, 3) Identified equations or diagrams"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Parse response
            result = response.choices[0].message.content
            
            # Try to extract structured data
            return self._parse_vision_response(result, ocr_text)
            
        except Exception as e:
            print(f"Vision API error: {str(e)}")
            return {
                "enhanced_text": ocr_text,
                "structure": {},
                "suggestions": []
            }
    
    def _parse_vision_response(self, response: str, original_text: str) -> Dict[str, Any]:
        """Parse GPT-4V response into structured format"""
        # This is a simple parser - enhance based on your needs
        return {
            "enhanced_text": response or original_text,
            "structure": {
                "has_equations": "equation" in response.lower() or "=" in response,
                "has_diagrams": "diagram" in response.lower() or "figure" in response.lower(),
                "has_tables": "table" in response.lower(),
                "sections": []  # TODO: Extract sections
            },
            "suggestions": []
        }

# Global instance
vision_analyzer = VisionAnalyzer()