import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [privateKey, setPrivateKey] = useState('')
  const [btcAddress, setBtcAddress] = useState('')
  const [ethAddress, setEthAddress] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [apiStatus, setApiStatus] = useState(null)
  const [error, setError] = useState('')
  const [performance, setPerformance] = useState(null)

  // Check API status on component mount
  useEffect(() => {
    checkApiStatus()
  }, [])

  const checkApiStatus = async () => {
    try {
      const response = await fetch('/api/crypto/status')
      const data = await response.json()
      setApiStatus(data)
    } catch (error) {
      console.error('Failed to check API status:', error)
      setError('Failed to connect to backend API')
    }
  }

  const generateKeys = async () => {
    setIsGenerating(true)
    setError('')
    
    try {
      const response = await fetch('/api/crypto/generate-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          use_gpu: true
        })
      })
      
      const result = await response.json()
      
      if (result.success) {
        const { data } = result
        setPrivateKey(data.private_key)
        setBtcAddress(data.btc_address)
        setEthAddress(data.eth_address)
        setPerformance({
          method: data.method,
          generation_time: data.generation_time
        })
      } else {
        setError(result.error || 'Failed to generate keys')
      }
    } catch (error) {
      console.error('Error generating keys:', error)
      setError('Network error: Failed to generate keys')
    }
    
    setIsGenerating(false)
  }

  const runBenchmark = async () => {
    setIsGenerating(true)
    setError('')
    
    try {
      const response = await fetch('/api/crypto/benchmark', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          key_count: 10000
        })
      })
      
      const result = await response.json()
      
      if (result.success) {
        const { data } = result
        setPerformance({
          cpu_performance: data.results.cpu.keys_per_second,
          gpu_performance: data.results.gpu?.keys_per_second,
          speedup: data.results.gpu?.speedup,
          key_count: data.key_count
        })
      } else {
        setError(result.error || 'Benchmark failed')
      }
    } catch (error) {
      console.error('Error running benchmark:', error)
      setError('Network error: Benchmark failed')
    }
    
    setIsGenerating(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🔑 Crypto Key Generator
          </h1>
          <p className="text-lg text-gray-600">
            High-performance cryptocurrency key generation tool with GPU acceleration
          </p>
          
          {/* API Status */}
          {apiStatus && (
            <div className="flex items-center justify-center mt-4 space-x-2">
              <span className={`px-3 py-1 rounded-full text-sm ${
                apiStatus.status === 'online' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                API: {apiStatus.status}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm ${
                apiStatus.gpu_acceleration 
                  ? 'bg-blue-100 text-blue-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                GPU: {apiStatus.gpu_acceleration ? 'Available' : 'Not Available'}
              </span>
              <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm">₿ Bitcoin</span>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">Ξ Ethereum</span>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">🔄 Key Generation</h2>
          <p className="text-gray-600 mb-6">Generate new private keys and derive corresponding blockchain addresses</p>
          
          <div className="flex space-x-4 mb-6">
            <button 
              onClick={generateKeys} 
              disabled={isGenerating}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-medium py-3 px-6 rounded-lg transition-colors"
            >
              {isGenerating ? '🔄 Generating...' : '🔑 Generate New Keys'}
            </button>
            
            <button 
              onClick={runBenchmark} 
              disabled={isGenerating}
              className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-medium py-3 px-6 rounded-lg transition-colors"
            >
              {isGenerating ? '⏱️ Benchmarking...' : '📊 Run Benchmark'}
            </button>
          </div>

          {/* Performance Info */}
          {performance && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="font-semibold mb-2">⚡ Performance Info</h3>
              {performance.method && (
                <p className="text-sm text-gray-600">
                  Method: {performance.method} 
                  {performance.generation_time && ` (${(performance.generation_time * 1000).toFixed(2)}ms)`}
                </p>
              )}
              {performance.cpu_performance && (
                <div className="text-sm text-gray-600">
                  <p>CPU Performance: {performance.cpu_performance.toLocaleString()} keys/second</p>
                  {performance.gpu_performance && (
                    <>
                      <p>GPU Performance: {performance.gpu_performance.toLocaleString()} keys/second</p>
                      <p>Speedup: {performance.speedup.toFixed(1)}x faster</p>
                    </>
                  )}
                  {performance.key_count && (
                    <p>Benchmark size: {performance.key_count.toLocaleString()} keys</p>
                  )}
                </div>
              )}
            </div>
          )}

          {privateKey && (
            <div className="space-y-4 border-t pt-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Private Key (32 bytes hex)
                </label>
                <input
                  value={privateKey}
                  readOnly
                  className="w-full p-3 border border-gray-300 rounded-lg font-mono text-sm bg-gray-50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ₿ Bitcoin Address
                </label>
                <input
                  value={btcAddress}
                  readOnly
                  className="w-full p-3 border border-gray-300 rounded-lg font-mono text-sm bg-gray-50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ξ Ethereum Address
                </label>
                <input
                  value={ethAddress}
                  readOnly
                  className="w-full p-3 border border-gray-300 rounded-lg font-mono text-sm bg-gray-50"
                />
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">✨ Features</h2>
          <p className="text-gray-600 mb-6">Advanced capabilities for high-performance key generation</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <h3 className="font-semibold mb-2">🚀 GPU Acceleration</h3>
              <p className="text-sm text-gray-600">
                Achieve millions of key generations per second using C++ extensions
              </p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <h3 className="font-semibold mb-2">🔍 Bloom Filter</h3>
              <p className="text-sm text-gray-600">
                Efficient address verification against massive datasets
              </p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <h3 className="font-semibold mb-2">📱 Offline-First</h3>
              <p className="text-sm text-gray-600">
                Generate and filter keys locally before online verification
              </p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <h3 className="font-semibold mb-2">🌐 Multi-Blockchain</h3>
              <p className="text-sm text-gray-600">
                Support for Bitcoin, Ethereum, and other EVM-compatible chains
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

