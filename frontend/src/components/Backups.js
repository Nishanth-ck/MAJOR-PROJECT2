import React, { useState, useEffect } from 'react';
import axios from 'axios';
import getApiUrl from '../config/api';
import InfoModal from './InfoModal';
import ConfirmModal from './ConfirmModal';

function Backups() {
  const [localBackups, setLocalBackups] = useState([]);
  const [cloudBackups, setCloudBackups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('local');
  const [downloading, setDownloading] = useState({});
  const [deleting, setDeleting] = useState({});
  const [modal, setModal] = useState({ isOpen: false, type: 'info', title: '', message: '' });
  const [confirmModal, setConfirmModal] = useState({ 
    isOpen: false, 
    type: 'warning', 
    title: '', 
    message: '',
    onConfirm: null 
  });

  const showModal = (type, title, message) => {
    setModal({ isOpen: true, type, title, message });
  };

  const closeModal = () => {
    setModal({ isOpen: false, type: 'info', title: '', message: '' });
  };

  const closeConfirmModal = () => {
    setConfirmModal({ isOpen: false, type: 'warning', title: '', message: '', onConfirm: null });
  };

  const showConfirmModal = (type, title, message, onConfirm) => {
    setConfirmModal({ isOpen: true, type, title, message, onConfirm });
  };

  const fetchBackups = async () => {
    setLoading(true);
    try {
      const [localRes, cloudRes] = await Promise.all([
        axios.get(getApiUrl('api/backups/local')),
        axios.get(getApiUrl('api/backups/cloud'))
      ]);
      
      if (localRes.data.success) {
        setLocalBackups(localRes.data.files);
      }
      
      if (cloudRes.data.success) {
        setCloudBackups(cloudRes.data.files);
      }
    } catch (error) {
      console.error('Error fetching backups:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBackups();
    const interval = setInterval(fetchBackups, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleDownload = async (filename) => {
    try {
      setDownloading(prev => ({ ...prev, [filename]: true }));
      
      const response = await axios.post(getApiUrl('api/backups/cloud/download'), { filename });
      
      if (response.data.success) {
        showModal('success', 'Download Complete', response.data.message);
        // Refresh the list to show the newly downloaded file
        fetchBackups();
      } else {
        showModal('error', 'Download Failed', 'Download failed: ' + (response.data.error || 'Unknown error'));
      }
    } catch (error) {
        showModal('error', 'Download Error', 'Download failed: ' + (error.response?.data?.error || error.message));
    } finally {
      setDownloading(prev => ({ ...prev, [filename]: false }));
    }
  };

  const handleDelete = async (filename, backupType) => {
    showConfirmModal(
      'danger',
      'Delete File',
      `Are you sure you want to delete:\n${filename}\n\nThis action cannot be undone!`,
      async () => {
        closeConfirmModal();
        try {
          setDeleting(prev => ({ ...prev, [filename]: true }));
          
          const endpoint = backupType === 'local' 
            ? getApiUrl('api/backups/local/delete')
            : getApiUrl('api/backups/cloud/delete');
          
          const response = await axios.post(endpoint, { filename });
          
          if (response.data.success) {
            showModal('success', 'File Deleted', response.data.message);
            fetchBackups(); // Refresh the list
          } else {
            showModal('error', 'Delete Failed', 'Delete failed: ' + (response.data.error || 'Unknown error'));
          }
        } catch (error) {
          showModal('error', 'Delete Error', 'Delete failed: ' + (error.response?.data?.error || error.message));
        } finally {
          setDeleting(prev => ({ ...prev, [filename]: false }));
        }
      }
    );
  };

  const handleDeleteAll = async (backupType) => {
    const count = backupType === 'local' ? localBackups.length : cloudBackups.length;
    const typeName = backupType === 'local' ? 'local' : 'cloud';
    
    showConfirmModal(
      'danger',
      'Delete All Backups',
      `Are you sure you want to delete ALL ${count} ${typeName} backups?\n\nThis action cannot be undone!`,
      async () => {
        closeConfirmModal();
        try {
          const endpoint = backupType === 'local' 
            ? getApiUrl('api/backups/local/delete-all')
            : getApiUrl('api/backups/cloud/delete-all');
          
          const response = await axios.post(endpoint);
          
          if (response.data.success) {
            showModal('success', 'All Backups Deleted', response.data.message);
            fetchBackups(); // Refresh the list
          } else {
            showModal('error', 'Delete Failed', 'Delete failed: ' + (response.data.error || 'Unknown error'));
          }
        } catch (error) {
          showModal('error', 'Delete Error', 'Delete failed: ' + (error.response?.data?.error || error.message));
        }
      }
    );
  };

  const renderBackupList = (backups, type) => {
    if (loading) {
      return <div className="text-center py-8 text-gray-500 italic">Loading backups...</div>;
    }

    if (backups.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500">
          <div className="text-6xl mb-4 opacity-50">{type === 'local' ? '📁' : '☁️'}</div>
          <p className="text-lg">No {type} backups found</p>
        </div>
      );
    }

    return (
      <div className="flex flex-col gap-3">
        {backups.map((file, index) => (
          <div key={index} className="flex items-center p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-white hover:border-indigo-500 transition-all hover:shadow-md">
            <div className="text-3xl mr-4">📄</div>
            <div className="flex-1">
              <div className="font-medium text-gray-700 mb-1 break-all">{file.name}</div>
              <div className="flex gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1">📦 {formatBytes(file.size)}</span>
                <span className="flex items-center gap-1">🕒 {formatDate(file.modified || file.uploaded)}</span>
              </div>
            </div>
            <div className="flex gap-2 ml-2">
              {type === 'cloud' && (
                <button
                  onClick={() => handleDownload(file.name)}
                  disabled={downloading[file.name]}
                  className="px-4 py-2 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-lg transition-all duration-300 font-medium hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                >
                  {downloading[file.name] ? '⬇️ Downloading...' : '⬇️ Download'}
                </button>
              )}
              <button
                onClick={() => handleDelete(file.name, type)}
                disabled={deleting[file.name]}
                className="px-4 py-2 bg-red-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                {deleting[file.name] ? '🗑️ Deleting...' : '🗑️ Delete'}
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <>
      <InfoModal 
        isOpen={modal.isOpen}
        onClose={closeModal}
        type={modal.type}
        title={modal.title}
        message={modal.message}
      />
      <ConfirmModal
        isOpen={confirmModal.isOpen}
        onClose={closeConfirmModal}
        onConfirm={confirmModal.onConfirm}
        type={confirmModal.type}
        title={confirmModal.title}
        message={confirmModal.message}
      />
      <div className="animate-fade-in">
      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-6 text-3xl font-bold">Backup Files</h2>
        
        <div className="flex gap-2 mb-6 border-b-2 border-gray-200">
          <button
            className={`px-6 py-3 font-medium transition-all ${
              activeTab === 'local' 
                ? 'text-indigo-600 border-b-3 border-indigo-600 pb-3' 
                : 'text-gray-500 hover:text-indigo-600'
            }`}
            onClick={() => setActiveTab('local')}
          >
            💾 Local Backups ({localBackups.length})
          </button>
          <button
            className={`px-6 py-3 font-medium transition-all ${
              activeTab === 'cloud' 
                ? 'text-indigo-600 border-b-3 border-indigo-600 pb-3' 
                : 'text-gray-500 hover:text-indigo-600'
            }`}
            onClick={() => setActiveTab('cloud')}
          >
            ☁️ Cloud Backups ({cloudBackups.length})
          </button>
        </div>

        <div className="min-h-[300px]">
          {activeTab === 'local' 
            ? renderBackupList(localBackups, 'local')
            : renderBackupList(cloudBackups, 'cloud')
          }
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200 flex justify-between items-center flex-wrap gap-3">
          <div className="flex gap-3">
            <button 
              className="px-6 py-3 bg-gray-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-gray-600"
              onClick={fetchBackups}
            >
              🔄 Refresh
            </button>
            {activeTab === 'local' && localBackups.length > 0 && (
              <button 
                className="px-6 py-3 bg-red-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-red-600"
                onClick={() => handleDeleteAll('local')}
              >
                🗑️ Delete All Local Backups
              </button>
            )}
            {activeTab === 'cloud' && cloudBackups.length > 0 && (
              <button 
                className="px-6 py-3 bg-red-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-red-600"
                onClick={() => handleDeleteAll('cloud')}
              >
                🗑️ Delete All Cloud Backups
              </button>
            )}
          </div>
          <div className="text-sm text-gray-600">
            {activeTab === 'local' ? `${localBackups.length} files` : `${cloudBackups.length} files`}
          </div>
        </div>
      </div>

      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-4 text-3xl font-bold">ℹ️ About Backups</h2>
        <div className="leading-relaxed">
          <p className="mb-4 text-gray-700">
            <strong className="text-indigo-600">Local Backups:</strong> Files stored on your computer in the backup folder. 
            These are created immediately when changes are detected.
          </p>
          <p className="mb-4 text-gray-700">
            <strong className="text-indigo-600">Cloud Backups:</strong> Files uploaded to MongoDB Atlas for remote storage. 
            Uploads happen automatically every 30 minutes or can be triggered manually from the Dashboard.
          </p>
          <p className="mb-4 text-gray-700">
            <strong className="text-indigo-600">Downloading from Cloud:</strong> Click the <strong className="text-purple-600">⬇️ Download</strong> button next to any cloud backup file to retrieve it from MongoDB and save it to your local backup folder. 
            This allows you to recover complete files that were uploaded to the cloud.
          </p>
          <p className="mb-4 text-gray-700">
            <strong className="text-indigo-600">Backup Naming:</strong> Files are saved with suffixes like <code className="bg-gray-100 px-2 py-1 rounded font-mono text-purple-600">_modified</code> or 
            <code className="bg-gray-100 px-2 py-1 rounded font-mono text-purple-600">_deleted</code> to indicate the type of change detected.
          </p>
        </div>
      </div>
    </div>
    </>
  );
}

export default Backups;

