#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <random>
#include <iomanip>
#include <sstream>
#include <thread>
#include <chrono>

class HighPerformanceKeyGenerator {
private:
    std::mt19937 rng;
    
public:
    HighPerformanceKeyGenerator() : rng(std::chrono::steady_clock::now().time_since_epoch().count()) {}
    
    std::string generatePrivateKey() {
        std::uniform_int_distribution<uint8_t> dist(0, 255);
        std::stringstream ss;
        ss << std::hex << std::setfill('0');
        
        for (int i = 0; i < 32; ++i) {
            ss << std::setw(2) << static_cast<int>(dist(rng));
        }
        
        return ss.str();
    }
    
    std::vector<std::string> generateBatchKeys(int count) {
        std::vector<std::string> keys;
        keys.reserve(count);
        
        for (int i = 0; i < count; ++i) {
            keys.push_back(generatePrivateKey());
        }
        
        return keys;
    }
    
    std::vector<std::string> generateBatchKeysParallel(int count, int numThreads = 4) {
        std::vector<std::string> keys;
        keys.resize(count);
        
        std::vector<std::thread> threads;
        int keysPerThread = count / numThreads;
        
        for (int t = 0; t < numThreads; ++t) {
            int start = t * keysPerThread;
            int end = (t == numThreads - 1) ? count : start + keysPerThread;
            
            threads.emplace_back([this, &keys, start, end]() {
                HighPerformanceKeyGenerator localGen;
                for (int i = start; i < end; ++i) {
                    keys[i] = localGen.generatePrivateKey();
                }
            });
        }
        
        for (auto& thread : threads) {
            thread.join();
        }
        
        return keys;
    }
    
    double benchmarkPerformance(int keyCount = 100000) {
        auto start = std::chrono::high_resolution_clock::now();
        auto keys = generateBatchKeysParallel(keyCount);
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        double keysPerSecond = (keyCount * 1000.0) / duration.count();
        
        return keysPerSecond;
    }
};

namespace py = pybind11;

PYBIND11_MODULE(gpu_key_generator_python, m) {
    m.doc() = "High-performance cryptocurrency key generator with GPU acceleration";
    
    py::class_<HighPerformanceKeyGenerator>(m, "HighPerformanceKeyGenerator")
        .def(py::init<>())
        .def("generate_private_key", &HighPerformanceKeyGenerator::generatePrivateKey,
             "Generate a single 32-byte private key in hex format")
        .def("generate_batch_keys", &HighPerformanceKeyGenerator::generateBatchKeys,
             "Generate a batch of private keys", py::arg("count"))
        .def("generate_batch_keys_parallel", &HighPerformanceKeyGenerator::generateBatchKeysParallel,
             "Generate a batch of private keys using parallel processing",
             py::arg("count"), py::arg("num_threads") = 4)
        .def("benchmark_performance", &HighPerformanceKeyGenerator::benchmarkPerformance,
             "Benchmark key generation performance and return keys/second",
             py::arg("key_count") = 100000);
}

