
import os
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58
from Crypto.Hash import keccak, RIPEMD160
from bloom_filter2 import BloomFilter

def generate_private_key():
    """Generates a random 32-byte private key."""
    return os.urandom(32).hex()

def private_key_to_btc_address(private_key_hex):
    """Derives a BTC address from a private key (hex string)."""
    private_key_bytes = bytes.fromhex(private_key_hex)
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key_bytes = b'\x04' + vk.to_string()

    sha256_1 = hashlib.sha256(public_key_bytes).digest()
    ripemd160_hash = RIPEMD160.new()
    ripemd160_hash.update(sha256_1)
    ripemd160 = ripemd160_hash.digest()

    # Add network byte (0x00 for mainnet)
    network_byte_public_key = b'\x00' + ripemd160
    sha256_2 = hashlib.sha256(network_byte_public_key).digest()
    sha256_3 = hashlib.sha256(sha256_2).digest()
    checksum = sha256_3[:4]

    btc_address = base58.b58encode(network_byte_public_key + checksum).decode('utf-8')
    return btc_address

def private_key_to_eth_address(private_key_hex):
    """Derives an ETH address from a private key (hex string)."""
    private_key_bytes = bytes.fromhex(private_key_hex)
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key_bytes = vk.to_string()

    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(public_key_bytes)
    ethereum_address = '0x' + keccak_hash.digest()[-20:].hex()
    return ethereum_address

def load_addresses_into_bloom_filter(filepath, max_elements, error_rate):
    """Loads addresses from a file into a Bloom filter."""
    bf = BloomFilter(max_elements=max_elements, error_rate=error_rate)
    with open(filepath, 'r') as f:
        for line in f:
            bf.add(line.strip())
    return bf

if __name__ == "__main__":
    print("Generating a new private key and deriving addresses...")
    private_key = generate_private_key()
    print(f"Private Key: {private_key}")

    btc_address = private_key_to_btc_address(private_key)
    print(f"BTC Address: {btc_address}")

    eth_address = private_key_to_eth_address(private_key)
    print(f"ETH Address: {eth_address}")

    # Example of Bloom filter usage
    # Create a dummy address file for testing
    with open("sample_addresses.txt", "w") as f:
        f.write("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\n") # Bitcoin Genesis address
        f.write("0x742d35Cc6634C0532925a3b844Bc454e4438f44e\n") # Ethereum DAO address

    print("\nLoading sample addresses into Bloom filter...")
    # Adjust max_elements and error_rate based on expected dataset size and acceptable false positive rate
    bloom_filter = load_addresses_into_bloom_filter("sample_addresses.txt", max_elements=1000, error_rate=0.01)

    print(f"Checking if {btc_address} is in Bloom filter: {btc_address in bloom_filter}")
    print(f"Checking if {eth_address} is in Bloom filter: {eth_address in bloom_filter}")
    print(f"Checking if 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa is in Bloom filter: {'1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa' in bloom_filter}")
    print(f"Checking if 0x742d35Cc6634C0532925a3b844Bc454e4438f44e is in Bloom filter: {'0x742d35Cc6634C0532925a3b844Bc454e4438f44e' in bloom_filter}")



