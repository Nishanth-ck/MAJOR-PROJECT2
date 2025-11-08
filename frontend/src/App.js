import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import Backups from './components/Backups';
import Logs from './components/Logs';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [state, setState] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch state and status
  const fetchData = async () => {
    try {
      const [stateRes, statusRes] = await Promise.all([
        axios.get('/api/state'),
        axios.get('/api/status')
      ]);
      setState(stateRes.data.state);
      setStatus(statusRes.data.status);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const renderContent = () => {
    if (loading) {
      return <div className="text-center text-2xl text-white py-12">Loading...</div>;
    }

    switch (activeTab) {
      case 'dashboard':
        return <Dashboard state={state} status={status} refreshData={fetchData} />;
      case 'settings':
        return <Settings state={state} refreshData={fetchData} />;
      case 'backups':
        return <Backups />;
      case 'logs':
        return <Logs />;
      default:
        return <Dashboard state={state} status={status} refreshData={fetchData} />;
    }
  };

  return (
    <div className="min-h-screen pb-8">
      <header className="bg-white/95 shadow-md p-8 text-center mb-8">
        <div>
          <h1 className="text-5xl text-indigo-600 mb-2">🛡️ File Protector</h1>
          <p className="text-gray-600 text-lg">Real-time file monitoring and backup system</p>
        </div>
      </header>

      <nav className="flex justify-center gap-4 my-0 mx-auto mb-8 max-w-3xl px-4 flex-wrap">
        <button 
          className={`px-6 py-3 rounded-lg transition-all duration-300 font-medium shadow-md hover:-translate-y-0.5 hover:shadow-lg ${
            activeTab === 'dashboard' 
              ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-indigo-400' 
              : 'bg-white/90 text-gray-700 hover:bg-white'
          }`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={`px-6 py-3 rounded-lg transition-all duration-300 font-medium shadow-md hover:-translate-y-0.5 hover:shadow-lg ${
            activeTab === 'settings' 
              ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-indigo-400' 
              : 'bg-white/90 text-gray-700 hover:bg-white'
          }`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
        <button 
          className={`px-6 py-3 rounded-lg transition-all duration-300 font-medium shadow-md hover:-translate-y-0.5 hover:shadow-lg ${
            activeTab === 'backups' 
              ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-indigo-400' 
              : 'bg-white/90 text-gray-700 hover:bg-white'
          }`}
          onClick={() => setActiveTab('backups')}
        >
          💾 Backups
        </button>
        <button 
          className={`px-6 py-3 rounded-lg transition-all duration-300 font-medium shadow-md hover:-translate-y-0.5 hover:shadow-lg ${
            activeTab === 'logs' 
              ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-indigo-400' 
              : 'bg-white/90 text-gray-700 hover:bg-white'
          }`}
          onClick={() => setActiveTab('logs')}
        >
          📋 Logs
        </button>
      </nav>

      <main className="max-w-6xl mx-auto px-4">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;

