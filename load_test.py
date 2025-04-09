import requests
import threading
import time
import random
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict

DEFAULT_URL = "http://localhost:80"
DEFAULT_DURATION = 60
DEFAULT_THREADS = 10
DEFAULT_REQUESTS_PER_SECOND = 10

class LoadTester:
    def __init__(self, url, duration, threads, requests_per_second):
        self.url = url
        self.duration = duration
        self.threads = threads
        self.requests_per_second = requests_per_second
        self.stop_event = threading.Event()
        self.results = []
        self.server_distribution = defaultdict(int)
        self.response_times = []
        self.error_count = 0
        self.success_count = 0
        
    def worker(self, thread_id):
        delay = 1.0 / (self.requests_per_second / self.threads)
        
        while not self.stop_event.is_set():
            start_time = time.time()
            try:
                response = requests.get(self.url, timeout=5)
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    self.success_count += 1
                    self.response_times.append(response_time)
                    
                    try:
                        data = response.json()
                        server_id = data.get('server_id', 'unknown')
                        self.server_distribution[server_id] += 1
                    except:
                        pass
                else:
                    self.error_count += 1
            except Exception as e:
                self.error_count += 1
                
            elapsed = time.time() - start_time
            if elapsed < delay:
                time.sleep(delay - elapsed)
    
    def run(self):
        print(f"Starting load test with {self.threads} threads at {self.requests_per_second} RPS for {self.duration}s")
        print(f"Target URL: {self.url}")
        
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.worker, args=(i,))
            t.daemon = True
            threads.append(t)
            t.start()
        
        start_time = time.time()
        try:
            while time.time() - start_time < self.duration:
                time.sleep(1)
                elapsed = time.time() - start_time
                print(f"Progress: {elapsed:.1f}/{self.duration}s, Requests: {self.success_count + self.error_count}")
        except KeyboardInterrupt:
            print("Test interrupted by user")
        finally:
            self.stop_event.set()
            
        for t in threads:
            t.join(timeout=1)
            
        self.print_results()
        self.plot_results()
    
    def print_results(self):
        total_requests = self.success_count + self.error_count
        success_rate = (self.success_count / total_requests * 100) if total_requests > 0 else 0
        
        print("\n===== LOAD TEST RESULTS =====")
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {self.success_count}")
        print(f"Failed Requests: {self.error_count}")
        print(f"Success Rate: {success_rate:.2f}%")
        
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            min_response_time = min(self.response_times)
            max_response_time = max(self.response_times)
            
            sorted_times = sorted(self.response_times)
            p50 = sorted_times[int(len(sorted_times) * 0.5)]
            p90 = sorted_times[int(len(sorted_times) * 0.9)]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
            
            print("\n===== RESPONSE TIMES (ms) =====")
            print(f"Average: {avg_response_time:.2f}ms")
            print(f"Min: {min_response_time:.2f}ms")
            print(f"Max: {max_response_time:.2f}ms")
            print(f"P50: {p50:.2f}ms")
            print(f"P90: {p90:.2f}ms")
            print(f"P95: {p95:.2f}ms")
            print(f"P99: {p99:.2f}ms")
        
        if self.server_distribution:
            print("\n===== SERVER DISTRIBUTION =====")
            for server_id, count in sorted(self.server_distribution.items()):
                percentage = (count / self.success_count * 100) if self.success_count > 0 else 0
                print(f"Server {server_id}: {count} requests ({percentage:.2f}%)")
    
    def plot_results(self):
        if not self.response_times:
            return
            
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 1, 1)
        plt.hist(self.response_times, bins=30, alpha=0.7, color='blue')
        plt.title('Response Time Distribution')
        plt.xlabel('Response Time (ms)')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 1, 2)
        servers = list(self.server_distribution.keys())
        counts = [self.server_distribution[s] for s in servers]
        plt.bar(servers, counts, color='green', alpha=0.7)
        plt.title('Server Distribution')
        plt.xlabel('Server ID')
        plt.ylabel('Request Count')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('load_test_results.png')
        print("\nResults plot saved as 'load_test_results.png'")

def main():
    parser = argparse.ArgumentParser(description='HTTP Load Testing Tool')
    parser.add_argument('--url', default=DEFAULT_URL, help='Target URL')
    parser.add_argument('--duration', type=int, default=DEFAULT_DURATION, help='Test duration in seconds')
    parser.add_argument('--threads', type=int, default=DEFAULT_THREADS, help='Number of threads')
    parser.add_argument('--rps', type=int, default=DEFAULT_REQUESTS_PER_SECOND, help='Requests per second')
    
    args = parser.parse_args()
    
    tester = LoadTester(args.url, args.duration, args.threads, args.rps)
    tester.run()

if __name__ == '__main__':
    main()