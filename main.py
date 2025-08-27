
from modules.key_generation import generate_private_key
from modules.address_derivation import private_key_to_btc_address, private_key_to_eth_address
from modules.bloom_filter_manager import load_addresses_into_bloom_filter

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


