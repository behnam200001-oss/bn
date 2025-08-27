#!/usr/bin/env python3.11

import gpu_key_generator_python
import time
import os

def test_gpu_module():
    print("Testing High-Performance Key Generator (C++ Python Extension)")
    print("=" * 65)
    
    # Create generator instance
    generator = gpu_key_generator_python.HighPerformanceKeyGenerator()
    
    # Test single key generation
    print("\n1. Single Key Generation:")
    single_key = generator.generate_private_key()
    print(f"Private Key: {single_key}")
    print(f"Key Length: {len(single_key)} characters")
    
    # Test batch generation
    print("\n2. Batch Key Generation (10 keys):")
    batch_keys = generator.generate_batch_keys(10)
    for i, key in enumerate(batch_keys, 1):
        print(f"Key {i:2d}: {key}")
    
    # Test parallel batch generation
    print("\n3. Parallel Batch Generation (1000 keys):")
    start_time = time.time()
    parallel_keys = generator.generate_batch_keys_parallel(1000, 4)
    end_time = time.time()
    
    print(f"Generated {len(parallel_keys)} keys in {(end_time - start_time)*1000:.2f}ms")
    print(f"First key: {parallel_keys[0]}")
    print(f"Last key:  {parallel_keys[-1]}")
    
    # Performance benchmark
    print("\n4. Performance Benchmark:")
    keys_per_second = generator.benchmark_performance(100000)
    print(f"Performance: {keys_per_second:,.0f} keys/second")
    
    # Compare with Python implementation
    print("\n5. Performance Comparison:")
    print("C++ Extension vs Pure Python:")
    
    # Pure Python implementation for comparison
    def python_generate_key():
        return os.urandom(32).hex()
    
    # Benchmark pure Python
    start_time = time.time()
    python_keys = [python_generate_key() for _ in range(10000)]
    end_time = time.time()
    
    python_keys_per_second = 10000 / (end_time - start_time)
    
    print(f"Pure Python:   {python_keys_per_second:,.0f} keys/second")
    print(f"C++ Extension: {keys_per_second:,.0f} keys/second")
    print(f"Speedup:       {keys_per_second / python_keys_per_second:.1f}x faster")

if __name__ == "__main__":
    test_gpu_module()

