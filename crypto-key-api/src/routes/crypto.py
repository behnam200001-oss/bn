import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, jsonify, request
from src.modules.key_generation import generate_private_key
from src.modules.address_derivation import private_key_to_btc_address, private_key_to_eth_address
from src.modules.bloom_filter_manager import load_addresses_into_bloom_filter
import time

# Try to import GPU acceleration
try:
    import gpu_key_generator_python
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

crypto_bp = Blueprint('crypto', __name__)

# Global variables for caching
gpu_generator = None
bloom_filter = None

if GPU_AVAILABLE:
    gpu_generator = gpu_key_generator_python.HighPerformanceKeyGenerator()

@crypto_bp.route('/status', methods=['GET'])
def get_status():
    """Get the status of the crypto key generator service."""
    return jsonify({
        'status': 'online',
        'gpu_acceleration': GPU_AVAILABLE,
        'bloom_filter_loaded': bloom_filter is not None,
        'version': '1.0.0'
    })

@crypto_bp.route('/generate-key', methods=['POST'])
def generate_key():
    """Generate a single private key and derive addresses."""
    try:
        data = request.get_json() or {}
        use_gpu = data.get('use_gpu', True) and GPU_AVAILABLE
        
        start_time = time.time()
        
        if use_gpu:
            private_key = gpu_generator.generate_private_key()
            method = "GPU-accelerated"
        else:
            private_key = generate_private_key()
            method = "CPU"
        
        btc_address = private_key_to_btc_address(private_key)
        eth_address = private_key_to_eth_address(private_key)
        
        generation_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'data': {
                'private_key': private_key,
                'btc_address': btc_address,
                'eth_address': eth_address,
                'method': method,
                'generation_time': generation_time
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/generate-batch', methods=['POST'])
def generate_batch():
    """Generate a batch of private keys."""
    try:
        data = request.get_json() or {}
        count = data.get('count', 10)
        use_gpu = data.get('use_gpu', True) and GPU_AVAILABLE
        num_threads = data.get('num_threads', 4)
        
        # Limit batch size for safety
        if count > 100000:
            return jsonify({
                'success': False,
                'error': 'Batch size too large. Maximum is 100,000 keys.'
            }), 400
        
        start_time = time.time()
        
        if use_gpu:
            private_keys = gpu_generator.generate_batch_keys_parallel(count, num_threads)
            method = "GPU-accelerated"
        else:
            private_keys = [generate_private_key() for _ in range(count)]
            method = "CPU"
        
        generation_time = time.time() - start_time
        
        # For large batches, only derive addresses for a sample
        sample_size = min(10, count)
        sample_keys = private_keys[:sample_size]
        
        sample_results = []
        for pk in sample_keys:
            btc_addr = private_key_to_btc_address(pk)
            eth_addr = private_key_to_eth_address(pk)
            sample_results.append({
                'private_key': pk,
                'btc_address': btc_addr,
                'eth_address': eth_addr
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_keys': count,
                'sample_results': sample_results,
                'all_keys': private_keys if count <= 100 else None,  # Only return all keys for small batches
                'performance': {
                    'generation_time': generation_time,
                    'keys_per_second': count / generation_time,
                    'method': method
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/benchmark', methods=['POST'])
def benchmark():
    """Run a performance benchmark."""
    try:
        data = request.get_json() or {}
        key_count = data.get('key_count', 10000)
        
        # Limit benchmark size
        if key_count > 1000000:
            return jsonify({
                'success': False,
                'error': 'Benchmark size too large. Maximum is 1,000,000 keys.'
            }), 400
        
        results = {}
        
        # CPU benchmark
        start_time = time.time()
        cpu_keys = [generate_private_key() for _ in range(key_count)]
        cpu_time = time.time() - start_time
        cpu_performance = key_count / cpu_time
        
        results['cpu'] = {
            'time': cpu_time,
            'keys_per_second': cpu_performance,
            'method': 'CPU'
        }
        
        # GPU benchmark (if available)
        if GPU_AVAILABLE:
            gpu_performance = gpu_generator.benchmark_performance(key_count)
            results['gpu'] = {
                'keys_per_second': gpu_performance,
                'method': 'GPU-accelerated',
                'speedup': gpu_performance / cpu_performance
            }
        
        return jsonify({
            'success': True,
            'data': {
                'key_count': key_count,
                'results': results,
                'gpu_available': GPU_AVAILABLE
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/load-bloom-filter', methods=['POST'])
def load_bloom_filter_endpoint():
    """Load addresses into Bloom filter for verification."""
    global bloom_filter
    
    try:
        data = request.get_json() or {}
        addresses = data.get('addresses', [])
        max_elements = data.get('max_elements', 1000000)
        error_rate = data.get('error_rate', 0.001)
        
        if not addresses:
            return jsonify({
                'success': False,
                'error': 'No addresses provided'
            }), 400
        
        # Create temporary file with addresses
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            for addr in addresses:
                f.write(f"{addr}\n")
            temp_file = f.name
        
        try:
            bloom_filter = load_addresses_into_bloom_filter(temp_file, max_elements, error_rate)
            os.unlink(temp_file)  # Clean up temp file
            
            return jsonify({
                'success': True,
                'data': {
                    'addresses_loaded': len(addresses),
                    'max_elements': max_elements,
                    'error_rate': error_rate
                }
            })
        
        except Exception as e:
            os.unlink(temp_file)  # Clean up temp file on error
            raise e
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@crypto_bp.route('/check-addresses', methods=['POST'])
def check_addresses():
    """Check if addresses exist in the loaded Bloom filter."""
    try:
        if bloom_filter is None:
            return jsonify({
                'success': False,
                'error': 'No Bloom filter loaded. Please load addresses first.'
            }), 400
        
        data = request.get_json() or {}
        addresses = data.get('addresses', [])
        
        if not addresses:
            return jsonify({
                'success': False,
                'error': 'No addresses provided'
            }), 400
        
        results = {}
        for addr in addresses:
            results[addr] = addr in bloom_filter
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'total_checked': len(addresses)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

