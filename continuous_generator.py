#!/usr/bin/env python3.11

import time
import os
import sys
import argparse
from datetime import datetime
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

class ContinuousKeyGenerator:
    def __init__(self, database_path="addresses.txt", max_elements=1000000, error_rate=0.001, hit_log_file="hits.txt"):
        self.bloom_filter = None
        self.gpu_generator = None
        self.database_path = database_path
        self.max_elements = max_elements
        self.error_rate = error_rate
        self.hit_log_file = hit_log_file
        self.hits = 0
        self.keys_generated = 0

        if GPU_AVAILABLE:
            self.gpu_generator = gpu_key_generator_python.HighPerformanceKeyGenerator()

        self._load_bloom_filter()

    def _load_bloom_filter(self):
        if os.path.exists(self.database_path):
            print(f"📂 Loading address database from {self.database_path}...")
            start_time = time.time()
            self.bloom_filter = load_addresses_into_bloom_filter(self.database_path, self.max_elements, self.error_rate)
            load_time = time.time() - start_time
            print(f"✅ Address database loaded in {load_time:.2f} seconds")
        else:
            print(f"⚠️  Address database file not found: {self.database_path}")
            print("   Creating sample database for demonstration...")
            self._create_sample_database(self.database_path)
            self.bloom_filter = load_addresses_into_bloom_filter(self.database_path, self.max_elements, self.error_rate)

    def _create_sample_database(self, filepath):
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

    def _log_hit(self, private_key, btc_address, eth_address, source):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"Timestamp: {timestamp} | Source: {source} | PrivateKey: {private_key} | BTC Address: {btc_address} | ETH Address: {eth_address}\n"
        with open(self.hit_log_file, 'a') as f:
            f.write(log_entry)
        print(f"🎉 HIT FOUND! Logged to {self.hit_log_file}")

    def generate_and_check_batch(self, batch_size=1000, num_threads=4):
        private_keys = []
        if GPU_AVAILABLE:
            private_keys = self.gpu_generator.generate_batch_keys_parallel(batch_size, num_threads)
        else:
            private_keys = [generate_private_key() for _ in range(batch_size)]

        self.keys_generated += batch_size

        for pk in private_keys:
            btc_address = private_key_to_btc_address(pk)
            eth_address = private_key_to_eth_address(pk)

            if self.bloom_filter:
                if btc_address in self.bloom_filter:
                    self.hits += 1
                    self._log_hit(pk, btc_address, eth_address, "BTC")
                if eth_address in self.bloom_filter:
                    self.hits += 1
                    self._log_hit(pk, btc_address, eth_address, "ETH")

    def start_continuous_generation(self, batch_size=1000, num_threads=4, interval_seconds=1):
        print("🚀 Starting continuous key generation...")
        print(f"   Batch Size: {batch_size}")
        print(f"   Threads: {num_threads}")
        print(f"   GPU Available: {GPU_AVAILABLE}")
        print(f"   Hits will be logged to: {self.hit_log_file}")
        print("   Press Ctrl+C to stop.")

        start_time = time.time()
        try:
            while True:
                self.generate_and_check_batch(batch_size, num_threads)
                elapsed_time = time.time() - start_time
                keys_per_second = self.keys_generated / elapsed_time if elapsed_time > 0 else 0
                sys.stdout.write(f"\rGenerated: {self.keys_generated:,} | Hits: {self.hits:,} | Speed: {keys_per_second:,.0f} keys/s")
                sys.stdout.flush()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n🛑 Continuous generation stopped by user.")
            elapsed_time = time.time() - start_time
            keys_per_second = self.keys_generated / elapsed_time if elapsed_time > 0 else 0
            print(f"Total Keys Generated: {self.keys_generated:,}")
            print(f"Total Hits: {self.hits:,}")
            print(f"Average Speed: {keys_per_second:,.0f} keys/s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Continuous Cryptocurrency Key Generator.")
    parser.add_argument("--batch_size", type=int, default=10000, help="Number of keys to generate per batch.")
    parser.add_argument("--num_threads", type=int, default=8, help="Number of threads for key generation.")
    parser.add_argument("--interval", type=float, default=0.1, help="Interval in seconds between batches.")
    parser.add_argument("--database_path", type=str, default="addresses.txt", help="Path to the address database file.")
    parser.add_argument("--hit_log_file", type=str, default="hits.txt", help="Path to the file for logging hits.")

    args = parser.parse_args()

    generator = ContinuousKeyGenerator(database_path=args.database_path, hit_log_file=args.hit_log_file)
    generator.start_continuous_generation(batch_size=args.batch_size, num_threads=args.num_threads, interval_seconds=args.interval)


