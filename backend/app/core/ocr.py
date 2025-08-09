import easyocr
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict, Any
import time

from app.models.document import OCRResult

class OCREngine:
    def __init__(self):
        # Initialize EasyOCR with English
        self.reader = easyocr.Reader(['en'], gpu=False)
        
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Read image
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh
    
    def detect_math(self, text: str) -> Tuple[bool, List[str]]:
        """Simple math detection based on common patterns"""
        math_indicators = ['=', '∫', '∑', '√', 'π', '±', '≤', '≥', '≠']
        math_expressions = []
        
        has_math = any(indicator in text for indicator in math_indicators)
        
        # Simple regex for basic equations
        import re
        equation_pattern = r'[a-zA-Z0-9\s\+\-\*\/\=\(\)]+='
        equations = re.findall(equation_pattern, text)
        math_expressions.extend(equations)
        
        return has_math, math_expressions
    
    def process_image(self, image_path: str) -> OCRResult:
        """Process image and extract text"""
        start_time = time.time()
        
        # Preprocess image
        processed_image = self.preprocess_image(image_path)
        
        # Perform OCR
        results = self.reader.readtext(processed_image)
        
        # Extract text and calculate confidence
        text_blocks = []
        confidence_scores = []
        
        for (bbox, text, confidence) in results:
            text_blocks.append(text)
            confidence_scores.append(confidence)
        
        full_text = ' '.join(text_blocks)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Detect math
        has_math, math_expressions = self.detect_math(full_text)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return OCRResult(
            text=full_text,
            confidence=avg_confidence,
            processing_time=processing_time,
            detected_languages=['en'],
            has_math=has_math,
            math_expressions=math_expressions if math_expressions else None
        )

# Global OCR engine instance
ocr_engine = OCREngine()