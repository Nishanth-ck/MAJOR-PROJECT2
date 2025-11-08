import React, { useState } from 'react';
import axios from 'axios';
import getApiUrl from '../config/api';
import InfoModal from './InfoModal';

function Dashboard({ state, status, refreshData }) {
  const [modal, setModal] = useState({ isOpen: false, type: 'info', title: '', message: '' });

  const showModal = (type, title, message) => {
    setModal({ isOpen: true, type, title, message });
  };

  const closeModal = () => {
    setModal({ isOpen: false, type: 'info', title: '', message: '' });
  };

  const handleStartMonitoring = async () => {
    try {
      await axios.post(await getApiUrl('api/monitoring/start'));
      refreshData();
      showModal('success', 'Success', 'Monitoring started successfully!');
    } catch (error) {
      showModal('error', 'Error', 'Error starting monitoring: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleStopMonitoring = async () => {
    try {
      await axios.post(await getApiUrl('api/monitoring/stop'));
      refreshData();
      showModal('info', 'Monitoring Stopped', 'Monitoring has been stopped successfully.');
    } catch (error) {
      showModal('error', 'Error', 'Error stopping monitoring: ' + error.message);
    }
  };

  const handleManualUpload = async () => {
    try {
      await axios.post(await getApiUrl('api/upload'));
      refreshData();
      showModal('success', 'Upload Complete', 'Manual upload completed successfully!');
    } catch (error) {
      showModal('error', 'Upload Failed', 'Error uploading: ' + (error.response?.data?.error || error.message));
    }
  };

  if (!state || !status) {
    return <div className="text-center text-2xl text-white py-12">Loading dashboard...</div>;
  }

  return (
    <>
      <InfoModal 
        isOpen={modal.isOpen}
        onClose={closeModal}
        type={modal.type}
        title={modal.title}
        message={modal.message}
      />
      <div className="animate-fade-in">
      {/* Quick Actions moved to top */}
      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-4 text-3xl font-bold">Quick Actions</h2>
        <div className="flex flex-wrap gap-2 mt-4">
          {!status.monitoring_active ? (
            <button 
              className="px-6 py-3 bg-green-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={handleStartMonitoring}
              disabled={!status.client_connected || !status.all_folders_exist || !status.backup_folder_exists}
              title={!status.client_connected ? "Desktop client not connected. Please install and run the desktop client." : ""}
            >
              ▶️ Start Monitoring
            </button>
          ) : (
            <button 
              className="px-6 py-3 bg-red-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-red-600"
              onClick={handleStopMonitoring}
            >
              ⏸️ Stop Monitoring
            </button>
          )}
          <button 
            className="px-6 py-3 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-lg transition-all duration-300 font-medium hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleManualUpload}
            disabled={!status.client_connected || !status.internet_connected || status.local_backup_count === 0}
            title={!status.client_connected ? "Desktop client not connected. Please install and run the desktop client." : ""}
          >
            ☁️ Upload to Cloud
          </button>
          <button 
            className="px-6 py-3 bg-gray-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-gray-600"
            onClick={refreshData}
          >
            🔄 Refresh Status
          </button>
        </div>
      </div>

      {!status.client_connected && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 mb-6 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <span className="text-yellow-400 text-2xl">⚠️</span>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">Desktop Client Not Connected</h3>
              <p className="text-sm text-yellow-700 mb-3">
                The desktop client is required to enable file monitoring and cloud backup features. 
                Please download and install the desktop client to continue.
              </p>
              <button
                onClick={() => window.location.hash = '#download'}
                className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors font-medium text-sm"
              >
                📥 Download Desktop Client
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-4 text-3xl font-bold">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
            <span className="font-medium text-gray-700">Client:</span>
            <span className={`inline-block px-4 py-2 rounded-full font-medium text-sm ${
              status.client_connected 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {status.client_connected ? '🟢 Connected' : '🔴 Not Connected'}
            </span>
          </div>
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
            <span className="font-medium text-gray-700">Monitoring:</span>
            <span className={`inline-block px-4 py-2 rounded-full font-medium text-sm ${
              status.monitoring_active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {status.monitoring_active ? '🟢 Active' : '🔴 Inactive'}
            </span>
          </div>
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
            <span className="font-medium text-gray-700">Internet:</span>
            <span className={`inline-block px-4 py-2 rounded-full font-medium text-sm ${
              status.internet_connected 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {status.internet_connected ? '🌐 Connected' : '📴 Offline'}
            </span>
          </div>
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
            <span className="font-medium text-gray-700">Monitor Folders:</span>
            <span className={`inline-block px-4 py-2 rounded-full font-medium text-sm ${
              status.all_folders_exist 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {status.all_folders_exist 
                ? `✅ ${status.existing_folders_count}/${status.monitor_folders_count} Exists` 
                : `❌ ${status.existing_folders_count}/${status.monitor_folders_count} Exist`}
            </span>
          </div>
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
            <span className="font-medium text-gray-700">Backup Folder:</span>
            <span className={`inline-block px-4 py-2 rounded-full font-medium text-sm ${
              status.backup_folder_exists 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {status.backup_folder_exists ? '✅ Exists' : '❌ Not Found'}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-4 text-3xl font-bold">Backup Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <div className="text-center p-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl text-white shadow-lg">
            <div className="text-5xl mb-2">💾</div>
            <div className="text-4xl font-bold mb-2">{status.local_backup_count}</div>
            <div className="text-lg opacity-90">Local Backups</div>
          </div>
          <div className="text-center p-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl text-white shadow-lg">
            <div className="text-5xl mb-2">☁️</div>
            <div className="text-4xl font-bold mb-2">
              {status.cloud_backup_count !== null ? status.cloud_backup_count : 'N/A'}
            </div>
            <div className="text-lg opacity-90">Cloud Backups</div>
          </div>
        </div>
      </div>

      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-4 text-3xl font-bold">Current Configuration</h2>
        <div className="mt-4 space-y-4">
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <strong className="block mb-2 text-gray-700">
              📁 Monitor Folders ({state.monitor_folders ? state.monitor_folders.length : (state.monitor_folder ? 1 : 0)}):
            </strong>
            {state.monitor_folders && state.monitor_folders.length > 0 ? (
              <div className="space-y-2">
                {state.monitor_folders.map((folder, index) => (
                  <code key={index} className="block p-2 bg-white border border-gray-200 rounded text-indigo-600 font-mono break-all text-sm">
                    {folder}
                  </code>
                ))}
              </div>
            ) : state.monitor_folder ? (
              <code className="block p-2 bg-white border border-gray-200 rounded text-indigo-600 font-mono break-all text-sm">
                {state.monitor_folder}
              </code>
            ) : (
              <p className="text-gray-500 italic">No folders configured</p>
            )}
          </div>
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <strong className="block mb-2 text-gray-700">💾 Backup Folder:</strong>
            <code className="block p-2 bg-white border border-gray-200 rounded text-indigo-600 font-mono break-all text-sm">
              {state.backup_folder}
            </code>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}

export default Dashboard;

