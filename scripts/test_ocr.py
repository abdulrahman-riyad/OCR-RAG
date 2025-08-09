import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.ocr import OCREngine
import argparse

def test_ocr(image_path):
    """Test OCR on a single image"""
    print(f"Testing OCR on: {image_path}")
    
    engine = OCREngine()
    result = engine.process_image(image_path)
    
    print(f"\nExtracted Text:\n{result.text}")
    print(f"\nConfidence: {result.confidence:.2%}")
    print(f"Processing Time: {result.processing_time:.2f}s")
    print(f"Has Math: {result.has_math}")
    
    if result.math_expressions:
        print(f"Math Expressions: {result.math_expressions}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test OCR on an image")
    parser.add_argument("image", help="Path to image file")
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: File not found: {args.image}")
        sys.exit(1)
    
    test_ocr(args.image)