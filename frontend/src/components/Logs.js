import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchLogs = async () => {
    try {
      const response = await axios.get('/api/logs?limit=100');
      if (response.data.success) {
        setLogs(response.data.logs);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching logs:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchLogs, 3000); // Refresh every 3 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const getLogIcon = (type) => {
    switch (type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      default:
        return 'ℹ️';
    }
  };

  const getLogClass = (type) => {
    return `log-item log-${type}`;
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const clearLogs = () => {
    if (window.confirm('This will clear the displayed logs (they will repopulate on next event). Continue?')) {
      setLogs([]);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <div className="flex justify-between items-center mb-6 flex-wrap gap-4">
          <h2 className="text-indigo-600 text-3xl font-bold">System Logs</h2>
          <div className="flex gap-2 items-center flex-wrap">
            <label className="flex items-center gap-2 cursor-pointer px-4 py-2 bg-gray-50 rounded-lg select-none">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="cursor-pointer"
              />
              <span className="text-gray-700 font-medium">Auto-refresh</span>
            </label>
            <button 
              className="px-4 py-2 bg-gray-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-gray-600"
              onClick={fetchLogs}
            >
              🔄 Refresh
            </button>
            <button 
              className="px-4 py-2 bg-red-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-red-600"
              onClick={clearLogs}
            >
              🗑️ Clear Display
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500 italic">Loading logs...</div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <div className="text-6xl mb-4 opacity-50">📋</div>
            <p className="text-lg">No logs yet</p>
            <p className="text-sm text-gray-400 mt-2">Logs will appear here when events occur</p>
          </div>
        ) : (
          <div className="max-h-[600px] overflow-y-auto border border-gray-200 rounded-lg bg-gray-50 scrollbar-thin scrollbar-thumb-indigo-500 scrollbar-track-gray-100">
            {logs.map((log, index) => (
              <div 
                key={index} 
                className={`flex items-center p-3 border-b border-gray-200 gap-3 transition-colors hover:bg-white ${
                  log.type === 'error' ? 'bg-red-50' : ''
                } ${log.type === 'info' ? 'border-l-3 border-blue-500' : log.type === 'success' ? 'border-l-3 border-green-500' : log.type === 'warning' ? 'border-l-3 border-yellow-500' : 'border-l-3 border-red-500'}`}
              >
                <span className="text-xl flex-shrink-0">{getLogIcon(log.type)}</span>
                <span className="font-mono text-gray-500 text-sm flex-shrink-0 min-w-[100px]">{formatTime(log.timestamp)}</span>
                <span className="flex-1 text-gray-700 break-words">{log.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-4 text-3xl font-bold">Log Types</h2>
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <span className="px-4 py-2 bg-blue-100 text-blue-900 rounded-full font-medium text-sm flex-shrink-0">ℹ️ INFO</span>
            <span className="text-gray-700">General information and system status updates</span>
          </div>
          <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <span className="px-4 py-2 bg-green-100 text-green-900 rounded-full font-medium text-sm flex-shrink-0">✅ SUCCESS</span>
            <span className="text-gray-700">Successful operations (monitoring started, uploads completed)</span>
          </div>
          <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <span className="px-4 py-2 bg-yellow-100 text-yellow-900 rounded-full font-medium text-sm flex-shrink-0">⚠️ WARNING</span>
            <span className="text-gray-700">Warning messages (monitoring stopped, connection issues)</span>
          </div>
          <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <span className="px-4 py-2 bg-red-100 text-red-900 rounded-full font-medium text-sm flex-shrink-0">❌ ERROR</span>
            <span className="text-gray-700">Error messages requiring attention</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Logs;

