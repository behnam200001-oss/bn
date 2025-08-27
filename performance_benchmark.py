#!/usr/bin/env python3.11

import time
import statistics
import sys
import os
from modules.key_generation import generate_private_key
from modules.address_derivation import private_key_to_btc_address, private_key_to_eth_address

try:
    import gpu_key_generator_python
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

def benchmark_key_generation():
    """Benchmark different key generation methods."""
    print("🚀 Performance Benchmark: Key Generation")
    print("=" * 50)
    
    test_sizes = [1000, 10000, 100000]
    
    for size in test_sizes:
        print(f"\n📊 Testing with {size:,} keys:")
        
        # CPU benchmark
        cpu_times = []
        for run in range(3):
            start_time = time.time()
            keys = [generate_private_key() for _ in range(size)]
            end_time = time.time()
            cpu_times.append(end_time - start_time)
        
        cpu_avg = statistics.mean(cpu_times)
        cpu_keys_per_sec = size / cpu_avg
        
        print(f"   CPU (Pure Python):")
        print(f"     Average time: {cpu_avg:.3f}s")
        print(f"     Performance:  {cpu_keys_per_sec:,.0f} keys/second")
        
        # GPU benchmark (if available)
        if GPU_AVAILABLE:
            generator = gpu_key_generator_python.HighPerformanceKeyGenerator()
            
            gpu_times = []
            for run in range(3):
                start_time = time.time()
                keys = generator.generate_batch_keys_parallel(size, 4)
                end_time = time.time()
                gpu_times.append(end_time - start_time)
            
            gpu_avg = statistics.mean(gpu_times)
            gpu_keys_per_sec = size / gpu_avg
            speedup = gpu_keys_per_sec / cpu_keys_per_sec
            
            print(f"   GPU (C++ Extension):")
            print(f"     Average time: {gpu_avg:.3f}s")
            print(f"     Performance:  {gpu_keys_per_sec:,.0f} keys/second")
            print(f"     Speedup:      {speedup:.1f}x")

def benchmark_address_derivation():
    """Benchmark address derivation performance."""
    print("\n🔐 Performance Benchmark: Address Derivation")
    print("=" * 50)
    
    # Generate test keys
    test_keys = [generate_private_key() for _ in range(1000)]
    
    # Benchmark BTC address derivation
    start_time = time.time()
    btc_addresses = [private_key_to_btc_address(key) for key in test_keys]
    btc_time = time.time() - start_time
    btc_per_sec = len(test_keys) / btc_time
    
    print(f"📊 BTC Address Derivation:")
    print(f"   Time for 1,000 addresses: {btc_time:.3f}s")
    print(f"   Performance: {btc_per_sec:,.0f} addresses/second")
    
    # Benchmark ETH address derivation
    start_time = time.time()
    eth_addresses = [private_key_to_eth_address(key) for key in test_keys]
    eth_time = time.time() - start_time
    eth_per_sec = len(test_keys) / eth_time
    
    print(f"📊 ETH Address Derivation:")
    print(f"   Time for 1,000 addresses: {eth_time:.3f}s")
    print(f"   Performance: {eth_per_sec:,.0f} addresses/second")

def benchmark_memory_usage():
    """Benchmark memory usage for different batch sizes."""
    print("\n💾 Memory Usage Benchmark")
    print("=" * 50)
    
    import psutil
    import gc
    
    process = psutil.Process(os.getpid())
    
    batch_sizes = [1000, 10000, 100000]
    
    for size in batch_sizes:
        gc.collect()  # Clean up before measurement
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate keys
        if GPU_AVAILABLE:
            generator = gpu_key_generator_python.HighPerformanceKeyGenerator()
            keys = generator.generate_batch_keys_parallel(size, 4)
        else:
            keys = [generate_private_key() for _ in range(size)]
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = peak_memory - initial_memory
        memory_per_key = memory_used * 1024 / size  # KB per key
        
        print(f"📊 Batch size: {size:,} keys")
        print(f"   Memory used: {memory_used:.1f} MB")
        print(f"   Per key: {memory_per_key:.2f} KB")
        
        # Clean up
        del keys
        gc.collect()

def benchmark_scalability():
    """Test scalability with increasing workloads."""
    print("\n📈 Scalability Benchmark")
    print("=" * 50)
    
    if not GPU_AVAILABLE:
        print("⚠️  GPU acceleration not available, skipping scalability test")
        return
    
    generator = gpu_key_generator_python.HighPerformanceKeyGenerator()
    
    # Test different thread counts
    thread_counts = [1, 2, 4, 8]
    test_size = 100000
    
    print(f"📊 Testing {test_size:,} keys with different thread counts:")
    
    for threads in thread_counts:
        times = []
        for run in range(3):
            start_time = time.time()
            keys = generator.generate_batch_keys_parallel(test_size, threads)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        keys_per_sec = test_size / avg_time
        
        print(f"   {threads} threads: {keys_per_sec:,.0f} keys/second ({avg_time:.3f}s)")

def generate_performance_report():
    """Generate a comprehensive performance report."""
    print("📋 Generating Performance Report")
    print("=" * 50)
    
    report_lines = []
    report_lines.append("# Crypto Key Generator Performance Report")
    report_lines.append("=" * 50)
    report_lines.append("")
    
    # System info
    import platform
    report_lines.append("## System Information")
    report_lines.append(f"- OS: {platform.system()} {platform.release()}")
    report_lines.append(f"- Python: {platform.python_version()}")
    report_lines.append(f"- GPU Acceleration: {'Available' if GPU_AVAILABLE else 'Not Available'}")
    report_lines.append("")
    
    # Quick benchmark
    if GPU_AVAILABLE:
        generator = gpu_key_generator_python.HighPerformanceKeyGenerator()
        perf = generator.benchmark_performance(100000)
        report_lines.append("## Performance Summary")
        report_lines.append(f"- GPU-accelerated key generation: {perf:,.0f} keys/second")
    
    # CPU benchmark
    start_time = time.time()
    cpu_keys = [generate_private_key() for _ in range(10000)]
    cpu_time = time.time() - start_time
    cpu_perf = 10000 / cpu_time
    
    report_lines.append(f"- CPU key generation: {cpu_perf:,.0f} keys/second")
    
    if GPU_AVAILABLE:
        speedup = perf / cpu_perf
        report_lines.append(f"- Performance improvement: {speedup:.1f}x")
    
    report_lines.append("")
    report_lines.append("## Address Derivation Performance")
    
    # Quick address derivation test
    test_key = generate_private_key()
    
    start_time = time.time()
    for _ in range(1000):
        btc_addr = private_key_to_btc_address(test_key)
    btc_time = time.time() - start_time
    btc_perf = 1000 / btc_time
    
    start_time = time.time()
    for _ in range(1000):
        eth_addr = private_key_to_eth_address(test_key)
    eth_time = time.time() - start_time
    eth_perf = 1000 / eth_time
    
    report_lines.append(f"- BTC address derivation: {btc_perf:,.0f} addresses/second")
    report_lines.append(f"- ETH address derivation: {eth_perf:,.0f} addresses/second")
    
    # Save report
    with open('performance_report.md', 'w') as f:
        f.write('\n'.join(report_lines))
    
    print("✅ Performance report saved to 'performance_report.md'")
    
    # Print summary
    print("\n📊 Performance Summary:")
    if GPU_AVAILABLE:
        print(f"   GPU Key Generation: {perf:,.0f} keys/second")
    print(f"   CPU Key Generation: {cpu_perf:,.0f} keys/second")
    print(f"   BTC Address Derivation: {btc_perf:,.0f} addresses/second")
    print(f"   ETH Address Derivation: {eth_perf:,.0f} addresses/second")

def main():
    print("🔬 Crypto Key Generator - Performance Benchmark Suite")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "keys":
            benchmark_key_generation()
        elif test_type == "addresses":
            benchmark_address_derivation()
        elif test_type == "memory":
            benchmark_memory_usage()
        elif test_type == "scalability":
            benchmark_scalability()
        elif test_type == "report":
            generate_performance_report()
        else:
            print(f"Unknown test type: {test_type}")
    else:
        # Run all benchmarks
        benchmark_key_generation()
        benchmark_address_derivation()
        benchmark_memory_usage()
        benchmark_scalability()
        generate_performance_report()

if __name__ == "__main__":
    main()

