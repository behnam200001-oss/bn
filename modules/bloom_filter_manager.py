
from bloom_filter2 import BloomFilter

def load_addresses_into_bloom_filter(filepath, max_elements, error_rate):
    """Loads addresses from a file into a Bloom filter."""
    bf = BloomFilter(max_elements=max_elements, error_rate=error_rate)
    with open(filepath, 'r') as f:
        for line in f:
            bf.add(line.strip())
    return bf


