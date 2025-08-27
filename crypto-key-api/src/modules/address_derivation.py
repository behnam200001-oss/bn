
import hashlib
from ecdsa import SigningKey, SECP256k1
import base58
from Crypto.Hash import keccak, RIPEMD160

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


