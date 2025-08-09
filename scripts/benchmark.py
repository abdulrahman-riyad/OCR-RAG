import time
import statistics
import concurrent.futures
import requests
import os
import sys

class OCRBenchmark:
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        self.results = []
    
    def benchmark_single_file(self, file_path):
        """Benchmark processing of a single file"""
        start_time = time.time()
        
        # Upload
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'image/jpeg')}
            response = requests.post(f"{self.api_base}/api/v1/upload/single", files=files)
        
        if response.status_code != 200:
            return None
        
        document_id = response.json()['document_id']
        upload_time = time.time() - start_time
        
        # Start processing
        process_start = time.time()
        requests.post(f"{self.api_base}/api/v1/process/{document_id}")
        
        # Wait for completion
        max_wait = 60  # seconds
        completed = False
        
        while (time.time() - process_start) < max_wait:
            status_response = requests.get(f"{self.api_base}/api/v1/process/{document_id}/status")
            
            if status_response.status_code == 200:
                status = status_response.json().get('status')
                if status == 'completed':
                    completed = True
                    break
                elif status == 'failed':
                    break
            
            time.sleep(0.5)
        
        process_time = time.time() - process_start
        total_time = time.time() - start_time
        
        return {
            'file': os.path.basename(file_path),
            'upload_time': upload_time,
            'process_time': process_time,
            'total_time': total_time,
            'completed': completed
        }
    
    def benchmark_concurrent(self, file_paths, max_workers=4):
        """Benchmark concurrent processing"""
        print(f"Starting concurrent benchmark with {max_workers} workers...")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.benchmark_single_file, fp): fp for fp in file_paths}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    self.results.append(result)
                    print(f"Completed: {result['file']} in {result['total_time']:.2f}s")
        
        total_time = time.time() - start_time
        
        return {
            'total_files': len(file_paths),
            'successful': len(self.results),
            'total_time': total_time,
            'avg_time_per_file': total_time / len(file_paths) if file_paths else 0
        }
    
    def print_statistics(self):
        """Print benchmark statistics"""
        if not self.results:
            print("No results to analyze")
            return
        
        print("\n" + "=" * 50)
        print("BENCHMARK RESULTS")
        print("=" * 50)
        
        upload_times = [r['upload_time'] for r in self.results]
        process_times = [r['process_time'] for r in self.results]
        total_times = [r['total_time'] for r in self.results]
        
        print(f"\nProcessed {len(self.results)} files")
        print(f"Success rate: {sum(1 for r in self.results if r['completed']) / len(self.results) * 100:.1f}%")
        
        print("\nUpload Times:")
        print(f"  Min: {min(upload_times):.2f}s")
        print(f"  Max: {max(upload_times):.2f}s")
        print(f"  Avg: {statistics.mean(upload_times):.2f}s")
        print(f"  Median: {statistics.median(upload_times):.2f}s")
        
        print("\nProcessing Times:")
        print(f"  Min: {min(process_times):.2f}s")
        print(f"  Max: {max(process_times):.2f}s")
        print(f"  Avg: {statistics.mean(process_times):.2f}s")
        print(f"  Median: {statistics.median(process_times):.2f}s")
        
        print("\nTotal Times:")
        print(f"  Min: {min(total_times):.2f}s")
        print(f"  Max: {max(total_times):.2f}s")
        print(f"  Avg: {statistics.mean(total_times):.2f}s")
        print(f"  Median: {statistics.median(total_times):.2f}s")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark OCR pipeline performance")
    parser.add_argument("files", nargs="+", help="Image files to process")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent workers")
    parser.add_argument("--api", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    # Verify files exist
    valid_files = []
    for f in args.files:
        if os.path.exists(f):
            valid_files.append(f)
        else:
            print(f"Warning: File not found: {f}")
    
    if not valid_files:
        print("No valid files to process")
        sys.exit(1)
    
    # Run benchmark
    benchmark = OCRBenchmark(args.api)
    
    if len(valid_files) == 1:
        # Single file benchmark
        result = benchmark.benchmark_single_file(valid_files[0])
        if result:
            print(f"File: {result['file']}")
            print(f"Upload: {result['upload_time']:.2f}s")
            print(f"Process: {result['process_time']:.2f}s")
            print(f"Total: {result['total_time']:.2f}s")
    else:
        # Multiple files benchmark
        summary = benchmark.benchmark_concurrent(valid_files, args.workers)
        benchmark.print_statistics()
        
        print(f"\nConcurrent Processing Summary:")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Total time: {summary['total_time']:.2f}s")
        print(f"  Avg per file: {summary['avg_time_per_file']:.2f}s")