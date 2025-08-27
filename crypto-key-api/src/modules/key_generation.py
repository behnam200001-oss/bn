
import os

def generate_private_key():
    """Generates a random 32-byte private key."""
    return os.urandom(32).hex()


