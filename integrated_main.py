#!/usr/bin/env python3.11

import sys
import os
import time
import argparse
from modules.key_generation import generate_private_key
from modules.address_derivation import private_key_to_btc_address, private_key_to_eth_address
from modules.bloom_filter_manager import load_addresses_into_bloom_filter

# Import GPU acceleration module if available
try:
    import gpu_key_generator_python
    GPU_AVAILABLE = True
    print("✅ GPU acceleration module loaded successfully")
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️  GPU acceleration module not available, using CPU fallback")

class CryptoKeyGeneratorTool:
    def __init__(self):
        self.bloom_filter = None
        self.gpu_generator = None
        
        if GPU_AVAILABLE:
            self.gpu_generator = gpu_key_generator_python.HighPerformanceKeyGenerator()
    
    def load_address_database(self, filepath, max_elements=1000000, error_rate=0.001):
        """Load addresses into Bloom filter for verification."""
        if os.path.exists(filepath):
            print(f"📂 Loading address database from {filepath}...")
            start_time = time.time()
            self.bloom_filter = load_addresses_into_bloom_filter(filepath, max_elements, error_rate)
            load_time = time.time() - start_time
            print(f"✅ Address database loaded in {load_time:.2f} seconds")
        else:
            print(f"⚠️  Address database file not found: {filepath}")
            print("   Creating sample database for demonstration...")
            self._create_sample_database(filepath)
            self.bloom_filter = load_addresses_into_bloom_filter(filepath, max_elements, error_rate)
    
    def _create_sample_database(self, filepath):
        """Create a sample address database for testing."""
        sample_addresses = [
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Bitcoin Genesis
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",  # Ethereum DAO
            "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",  # Bitcoin address
            "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Vitalik's address
            "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",  # Bitcoin P2SH
        ]
        
        with open(filepath, 'w') as f:
            for addr in sample_addresses:
                f.write(f"{addr}\n")
        
        print(f"📝 Created sample database with {len(sample_addresses)} addresses")
    
    def generate_single_key(self, use_gpu=True):
        """Generate a single private key and derive addresses."""
        if use_gpu and GPU_AVAILABLE:
            private_key = self.gpu_generator.generate_private_key()
            method = "GPU-accelerated"
        else:
            private_key = generate_private_key()
            method = "CPU"
        
        btc_address = private_key_to_btc_address(private_key)
        eth_address = private_key_to_eth_address(private_key)
        
        return {
            'private_key': private_key,
            'btc_address': btc_address,
            'eth_address': eth_address,
            'method': method
        }
    
    def generate_batch_keys(self, count, use_gpu=True, num_threads=4):
        """Generate a batch of keys with performance tracking."""
        print(f"🔄 Generating {count:,} keys...")
        start_time = time.time()
        
        if use_gpu and GPU_AVAILABLE:
            # Use GPU acceleration for private key generation
            private_keys = self.gpu_generator.generate_batch_keys_parallel(count, num_threads)
            method = "GPU-accelerated"
        else:
            # CPU fallback
            private_keys = [generate_private_key() for _ in range(count)]
            method = "CPU"
        
        generation_time = time.time() - start_time
        
        # Derive addresses for a subset (to avoid overwhelming output)
        sample_size = min(10, count)
        sample_keys = private_keys[:sample_size]
        
        print(f"🔄 Deriving addresses for {sample_size} sample keys...")
        derivation_start = time.time()
        
        results = []
        for pk in sample_keys:
            btc_addr = private_key_to_btc_address(pk)
            eth_addr = private_key_to_eth_address(pk)
            results.append({
                'private_key': pk,
                'btc_address': btc_addr,
                'eth_address': eth_addr
            })
        
        derivation_time = time.time() - derivation_start
        total_time = time.time() - start_time
        
        return {
            'total_keys': count,
            'sample_results': results,
            'performance': {
                'generation_time': generation_time,
                'derivation_time': derivation_time,
                'total_time': total_time,
                'keys_per_second': count / generation_time,
                'method': method
            }
        }
    
    def check_addresses_in_bloom_filter(self, addresses):
        """Check if addresses exist in the Bloom filter."""
        if not self.bloom_filter:
            print("⚠️  No Bloom filter loaded")
            return {}
        
        results = {}
        for addr in addresses:
            results[addr] = addr in self.bloom_filter
        
        return results
    
    def run_comprehensive_test(self):
        """Run a comprehensive test of all components."""
        print("🧪 Running Comprehensive Integration Test")
        print("=" * 50)
        
        # Test 1: Single key generation
        print("\n1️⃣  Single Key Generation Test:")
        single_result = self.generate_single_key()
        print(f"   Method: {single_result['method']}")
        print(f"   Private Key: {single_result['private_key'][:16]}...{single_result['private_key'][-16:]}")
        print(f"   BTC Address: {single_result['btc_address']}")
        print(f"   ETH Address: {single_result['eth_address']}")
        
        # Test 2: Batch generation
        print("\n2️⃣  Batch Generation Test:")
        batch_result = self.generate_batch_keys(1000)
        perf = batch_result['performance']
        print(f"   Method: {perf['method']}")
        print(f"   Keys Generated: {batch_result['total_keys']:,}")
        print(f"   Generation Time: {perf['generation_time']:.3f}s")
        print(f"   Performance: {perf['keys_per_second']:,.0f} keys/second")
        
        # Test 3: Bloom filter verification
        print("\n3️⃣  Bloom Filter Verification Test:")
        test_addresses = [
            single_result['btc_address'],
            single_result['eth_address'],
            "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Should be in filter
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Should be in filter
        ]
        
        bloom_results = self.check_addresses_in_bloom_filter(test_addresses)
        for addr, found in bloom_results.items():
            status = "✅ FOUND" if found else "❌ NOT FOUND"
            print(f"   {addr}: {status}")
        
        # Test 4: Performance comparison
        if GPU_AVAILABLE:
            print("\n4️⃣  Performance Comparison Test:")
            cpu_result = self.generate_batch_keys(10000, use_gpu=False)
            gpu_result = self.generate_batch_keys(10000, use_gpu=True)
            
            cpu_perf = cpu_result['performance']['keys_per_second']
            gpu_perf = gpu_result['performance']['keys_per_second']
            speedup = gpu_perf / cpu_perf
            
            print(f"   CPU Performance:  {cpu_perf:,.0f} keys/second")
            print(f"   GPU Performance:  {gpu_perf:,.0f} keys/second")
            print(f"   Speedup:          {speedup:.1f}x")
        
        print("\n✅ Comprehensive test completed!")

def main():
    parser = argparse.ArgumentParser(description='High-Performance Crypto Key Generator')
    parser.add_argument('--mode', choices=['single', 'batch', 'test'], default='test',
                       help='Operation mode')
    parser.add_argument('--count', type=int, default=1000,
                       help='Number of keys to generate in batch mode')
    parser.add_argument('--database', type=str, default='addresses.txt',
                       help='Address database file for Bloom filter')
    parser.add_argument('--no-gpu', action='store_true',
                       help='Disable GPU acceleration')
    
    args = parser.parse_args()
    
    # Initialize the tool
    tool = CryptoKeyGeneratorTool()
    
    # Load address database
    tool.load_address_database(args.database)
    
    use_gpu = not args.no_gpu
    
    if args.mode == 'single':
        result = tool.generate_single_key(use_gpu=use_gpu)
        print(f"Private Key: {result['private_key']}")
        print(f"BTC Address: {result['btc_address']}")
        print(f"ETH Address: {result['eth_address']}")
        print(f"Method: {result['method']}")
        
    elif args.mode == 'batch':
        result = tool.generate_batch_keys(args.count, use_gpu=use_gpu)
        perf = result['performance']
        print(f"Generated {result['total_keys']:,} keys in {perf['total_time']:.2f}s")
        print(f"Performance: {perf['keys_per_second']:,.0f} keys/second")
        print(f"Method: {perf['method']}")
        
    elif args.mode == 'test':
        tool.run_comprehensive_test()

if __name__ == "__main__":
    main()

