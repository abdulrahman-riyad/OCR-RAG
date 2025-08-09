import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.processor import document_processor
import argparse

async def test_processing(image_path: str):
    """Test the full processing pipeline"""
    print(f"Testing processing pipeline on: {image_path}")
    
    # Generate a test document ID
    document_id = "test_" + os.path.basename(image_path).split('.')[0]
    
    # Process the document
    result = await document_processor.process_document(document_id, image_path)
    
    print("\nProcessing Result:")
    print(f"Status: {result['status']}")
    
    for step, details in result.get('steps', {}).items():
        print(f"\n{step.upper()}:")
        print(f"  Status: {details.get('status')}")
        if 'confidence' in details:
            print(f"  Confidence: {details['confidence']:.1%}")
        if 'path' in details:
            print(f"  Output: {details['path']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test document processing pipeline")
    parser.add_argument("image", help="Path to image file")
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: File not found: {args.image}")
        sys.exit(1)
    
    asyncio.run(test_processing(args.image))