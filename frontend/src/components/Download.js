import React, { useState } from 'react';
import axios from 'axios';
import getApiUrl from '../config/api';

function Download() {
  const [downloading, setDownloading] = useState({});

  const handleDownload = async (platform) => {
    setDownloading(prev => ({ ...prev, [platform]: true }));
    
    try {
      // Get the API URL for the backend
      const apiUrl = await getApiUrl(`api/client/download/${platform}`);
      
      // Download from MongoDB via backend API
      const response = await axios({
        url: apiUrl,
        method: 'GET',
        responseType: 'blob', // Important: download as binary
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `file-protector-client-${platform}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setDownloading(prev => ({ ...prev, [platform]: false }));
    } catch (error) {
      console.error('Download error:', error);
      alert(`Download failed: ${error.response?.data?.error || error.message}\n\nMake sure the client files have been uploaded to MongoDB first.`);
      setDownloading(prev => ({ ...prev, [platform]: false }));
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-4 text-3xl font-bold">📥 Download Desktop Client</h2>
        <p className="text-gray-700 mb-6 text-lg">
          The desktop client is required to enable file monitoring and cloud backup features. 
          Web browsers cannot access your local file system for security reasons, so the desktop client 
          runs locally on your computer and bridges the gap between your files and the web application.
        </p>

        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-yellow-400 text-xl">⚠️</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <strong>Important:</strong> Without the desktop client, the "Start Monitoring" and "Upload to Cloud" 
                buttons will be disabled. The client must be running for these features to work.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border-2 border-indigo-200">
            <div className="text-4xl mb-4 text-center">🪟</div>
            <h3 className="text-xl font-bold text-indigo-600 mb-2 text-center">Windows</h3>
            <p className="text-gray-600 mb-4 text-sm text-center">Windows 10/11</p>
            <button
              onClick={() => handleDownload('windows')}
              disabled={downloading.windows}
              className="w-full px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {downloading.windows ? '⏳ Downloading...' : 'Download for Windows'}
            </button>
          </div>

          <div className="bg-gradient-to-br from-gray-50 to-slate-50 rounded-lg p-6 border-2 border-gray-200">
            <div className="text-4xl mb-4 text-center">🍎</div>
            <h3 className="text-xl font-bold text-gray-700 mb-2 text-center">macOS</h3>
            <p className="text-gray-600 mb-4 text-sm text-center">macOS 10.14+</p>
            <button
              onClick={() => handleDownload('macos')}
              disabled={downloading.macos}
              className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {downloading.macos ? '⏳ Downloading...' : 'Download for macOS'}
            </button>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-lg p-6 border-2 border-orange-200">
            <div className="text-4xl mb-4 text-center">🐧</div>
            <h3 className="text-xl font-bold text-orange-600 mb-2 text-center">Linux</h3>
            <p className="text-gray-600 mb-4 text-sm text-center">Ubuntu, Debian, etc.</p>
            <button
              onClick={() => handleDownload('linux')}
              disabled={downloading.linux}
              className="w-full px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {downloading.linux ? '⏳ Downloading...' : 'Download for Linux'}
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border-2 border-gray-200 mb-6">
          <h3 className="text-xl font-bold text-indigo-600 mb-4">📋 Installation Instructions</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Step 1: Download</h4>
              <p className="text-gray-600 text-sm">Click the download button for your operating system above.</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Step 2: Extract</h4>
              <p className="text-gray-600 text-sm">Extract the ZIP file to a folder of your choice (e.g., <code className="bg-gray-100 px-2 py-1 rounded">C:\FileProtector\</code> on Windows or <code className="bg-gray-100 px-2 py-1 rounded">~/FileProtector/</code> on Mac/Linux).</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Step 3: Install Dependencies</h4>
              <p className="text-gray-600 text-sm mb-2">Open a terminal/command prompt in the extracted folder and run:</p>
              <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm">
                <div className="mb-1"># Windows</div>
                <div className="text-white">install.bat</div>
                <div className="mt-2 mb-1"># macOS/Linux</div>
                <div className="text-white">./install.sh</div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Step 4: Configure</h4>
              <p className="text-gray-600 text-sm">Open <code className="bg-gray-100 px-2 py-1 rounded">client.py</code> in a text editor and set <code className="bg-gray-100 px-2 py-1 rounded">API_BASE_URL</code> to your deployed website URL.</p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Step 5: Run</h4>
              <p className="text-gray-600 text-sm mb-2">Start the client:</p>
              <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm">
                <div className="mb-1"># Windows</div>
                <div className="text-white">python client.py</div>
                <div className="mt-2 mb-1"># macOS/Linux</div>
                <div className="text-white">python3 client.py</div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Step 6: Verify</h4>
              <p className="text-gray-600 text-sm">Go to the Dashboard tab and verify that "Client: 🟢 Connected" is displayed. The buttons should now be enabled!</p>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg p-6 border-2 border-blue-200">
          <h3 className="text-xl font-bold text-blue-600 mb-3">💡 Quick Start Video</h3>
          <p className="text-gray-700 mb-4">
            For a visual guide, check out our installation tutorial on YouTube or refer to the 
            <a href="https://github.com/yourusername/your-repo/blob/main/DESKTOP_CLIENT_GUIDE.md" 
               target="_blank" 
               rel="noopener noreferrer"
               className="text-blue-600 hover:underline font-semibold"> detailed guide</a>.
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-6 border-2 border-gray-200 mt-6">
          <h3 className="text-xl font-bold text-gray-800 mb-3">❓ Troubleshooting</h3>
          <div className="space-y-3 text-sm text-gray-700">
            <div>
              <strong className="text-gray-800">Client won't start?</strong>
              <p className="mt-1">Make sure Python 3.8+ is installed. Check with <code className="bg-gray-200 px-2 py-1 rounded">python --version</code></p>
            </div>
            <div>
              <strong className="text-gray-800">Buttons still disabled?</strong>
              <p className="mt-1">Ensure the client is running and check the Dashboard for connection status.</p>
            </div>
            <div>
              <strong className="text-gray-800">Need more help?</strong>
              <p className="mt-1">See the <a href="https://github.com/yourusername/your-repo/blob/main/DESKTOP_CLIENT_GUIDE.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Desktop Client Guide</a> for detailed instructions.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Download;

