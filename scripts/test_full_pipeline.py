import asyncio
import requests
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_full_pipeline(image_path: str, api_base: str = "http://localhost:8000"):
    """Test the complete OCR pipeline via API"""
    
    print(f"Testing full pipeline with: {image_path}")
    print("=" * 50)
    
    # Step 1: Upload file
    print("\n1. Uploading file...")
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
        response = requests.post(f"{api_base}/api/v1/upload/single", files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return
    
    upload_result = response.json()
    document_id = upload_result['document_id']
    print(f"✓ Uploaded successfully. Document ID: {document_id}")
    
    # Step 2: Start processing
    print("\n2. Starting processing...")
    response = requests.post(f"{api_base}/api/v1/process/{document_id}")
    
    if response.status_code != 200:
        print(f"Processing start failed: {response.text}")
        return
    
    print("✓ Processing started")
    
    # Step 3: Monitor processing status
    print("\n3. Monitoring processing status...")
    max_attempts = 30  # 30 seconds timeout
    attempts = 0
    
    while attempts < max_attempts:
        response = requests.get(f"{api_base}/api/v1/process/{document_id}/status")
        
        if response.status_code == 200:
            status_data = response.json()
            status = status_data.get('status', 'unknown')
            
            print(f"   Status: {status}")
            
            if status == 'completed':
                print("✓ Processing completed!")
                
                # Print processing steps
                if 'steps' in status_data:
                    print("\n   Processing steps:")
                    for step, details in status_data['steps'].items():
                        print(f"   - {step}: {details.get('status', 'unknown')}")
                
                # Print summary
                if 'summary' in status_data:
                    print("\n   Summary:")
                    summary = status_data['summary']
                    print(f"   - Text length: {summary.get('text_length', 0)} characters")
                    print(f"   - Confidence: {summary.get('confidence', 0) * 100:.1f}%")
                    print(f"   - Has math: {summary.get('has_math', False)}")
                
                break
            elif status == 'failed':
                print("✗ Processing failed!")
                print(f"   Error: {status_data.get('error', 'Unknown error')}")
                return
        
        time.sleep(1)
        attempts += 1
    
    if attempts >= max_attempts:
        print("✗ Processing timeout!")
        return
    
    # Step 4: Test document retrieval
    print("\n4. Retrieving document...")
    response = requests.get(f"{api_base}/api/v1/documents/{document_id}")
    
    doc_data = None  # Initialize doc_data
    
    if response.status_code == 200:
        doc_data = response.json()
        print("✓ Document retrieved")
        print(f"   Title: {doc_data.get('title', 'Unknown')}")
        
        if 'ocr_text' in doc_data and doc_data['ocr_text']:
            preview = doc_data['ocr_text'][:200] + "..." if len(doc_data['ocr_text']) > 200 else doc_data['ocr_text']
            print(f"   Text preview: {preview}")
    else:
        print("✗ Failed to retrieve document")
        return
    
    # Step 5: Test search
    print("\n5. Testing search...")
    
    # Extract a word from the OCR text for searching
    if doc_data and 'ocr_text' in doc_data and doc_data['ocr_text']:
        words = doc_data['ocr_text'].split()
        if words:
            search_term = words[min(5, len(words)-1)]  # Pick a word
            
            response = requests.post(
                f"{api_base}/api/v1/search",
                json={"query": search_term, "limit": 5}
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"✓ Search for '{search_term}' returned {len(results)} results")
                
                for i, result in enumerate(results[:2]):
                    print(f"\n   Result {i+1}:")
                    print(f"   - Document: {result.get('document_id', '')[:8]}...")
                    print(f"   - Score: {result.get('score', 0):.2f}")
                    print(f"   - Snippet: {result.get('snippet', '')[:100]}...")
            else:
                print("✗ Search failed")
    else:
        print("   Skipping search - no OCR text available")
    
    # Step 6: Download processed files
    print("\n6. Testing file downloads...")
    
    for file_type in ['pdf', 'text']:
        response = requests.get(f"{api_base}/api/v1/process/{document_id}/download/{file_type}")
        
        if response.status_code == 200:
            print(f"✓ {file_type.upper()} download successful ({len(response.content)} bytes)")
        else:
            print(f"✗ {file_type.upper()} download failed")
    
    print("\n" + "=" * 50)
    print("Pipeline test completed!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test full OCR pipeline")
    parser.add_argument("image", help="Path to test image")
    parser.add_argument("--api", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: File not found: {args.image}")
        sys.exit(1)
    
    test_full_pipeline(args.image, args.api)