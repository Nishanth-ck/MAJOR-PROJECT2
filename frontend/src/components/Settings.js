import React, { useState, useEffect } from 'react';
import axios from 'axios';
import getApiUrl from '../config/api';
import InfoModal from './InfoModal';

function Settings({ state, refreshData }) {
  const [monitorFolders, setMonitorFolders] = useState([]);
  const [newFolder, setNewFolder] = useState('');
  const [backupFolder, setBackupFolder] = useState('');
  const [saving, setSaving] = useState(false);
  const [modal, setModal] = useState({ isOpen: false, type: 'info', title: '', message: '' });

  const showModal = (type, title, message) => {
    setModal({ isOpen: true, type, title, message });
  };

  const closeModal = () => {
    setModal({ isOpen: false, type: 'info', title: '', message: '' });
  };

  useEffect(() => {
    if (state) {
      // Support both old format (single folder) and new format (multiple folders)
      if (state.monitor_folders && Array.isArray(state.monitor_folders)) {
        setMonitorFolders(state.monitor_folders);
      } else if (state.monitor_folder) {
        setMonitorFolders([state.monitor_folder]);
      }
      
      setBackupFolder(state.backup_folder || '');
    }
  }, [state]);

  const validateFolder = async (path) => {
    try {
      const response = await axios.post(await getApiUrl('api/folders/validate'), { path });
      return response.data.exists;
    } catch (error) {
      return false;
    }
  };

  const handleAddFolder = async () => {
    if (!newFolder.trim()) {
      showModal('warning', 'Input Required', 'Please enter a folder path');
      return;
    }

    // Normalize the path - remove trailing backslash except for root drives
    let normalizedPath = newFolder.trim();
    if (normalizedPath.endsWith('\\') && normalizedPath.length > 3) {
      normalizedPath = normalizedPath.slice(0, -1);
    }

    // Check if user is adding a root drive
    const trimmedFolder = normalizedPath.toUpperCase();
    if (trimmedFolder === 'C:\\' || trimmedFolder === 'C:' || 
        trimmedFolder === 'D:\\' || trimmedFolder === 'D:' ||
        trimmedFolder === 'E:\\' || trimmedFolder === 'E:' ||
        trimmedFolder === 'F:\\' || trimmedFolder === 'F:' ||
        trimmedFolder.match(/^[A-Z]:\\?$/)) {
      const confirmed = window.confirm(
        '⚠️ WARNING!\n\n' +
        'You are about to monitor an entire drive (' + newFolder + ')\n\n' +
        'This will backup ALL files on this drive, including:\n' +
        '• System files\n' +
        '• Temp files\n' +
        '• Program files\n' +
        '• Windows files\n\n' +
        'This can create THOUSANDS of backup files very quickly and may fill up your backup folder!\n\n' +
        'Recommended: Monitor specific folders instead like:\n' +
        '• C:\\Users\\YourName\\Documents\n' +
        '• C:\\Users\\YourName\\Desktop\n\n' +
        'Are you sure you want to continue?'
      );
      
      if (!confirmed) {
        return;
      }
    }

    const exists = await validateFolder(normalizedPath);
    if (!exists) {
      showModal('error', 'Invalid Folder', `Folder does not exist: ${normalizedPath}\n\nPlease enter a valid folder path.`);
      return;
    }

    setSaving(true);
    try {
      await axios.post(await getApiUrl('api/state'), {
        add_monitor_folder: normalizedPath
      });
      
      setNewFolder('');
      showModal('success', 'Folder Added', 'Monitor folder added successfully!');
      refreshData();
    } catch (error) {
      showModal('error', 'Error', 'Error adding folder: ' + (error.response?.data?.error || error.message));
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveFolder = async (folderToRemove) => {
    const confirmed = window.confirm(`Remove monitoring for:\n${folderToRemove}`);
    if (!confirmed) {
      return;
    }

    setSaving(true);
    try {
      await axios.post(await getApiUrl('api/state'), {
        remove_monitor_folder: folderToRemove
      });
      
      showModal('success', 'Folder Removed', 'Monitor folder removed successfully!');
      refreshData();
    } catch (error) {
      showModal('error', 'Error', 'Error removing folder: ' + (error.response?.data?.error || error.message));
    } finally {
      setSaving(false);
    }
  };

  const handleSaveBackupFolder = async () => {
    const backupExists = await validateFolder(backupFolder);

    if (!backupExists) {
      if (!window.confirm('Backup folder does not exist. Create it now?')) {
        return;
      }
    }

    setSaving(true);
    try {
      await axios.post(await getApiUrl('api/state'), {
        backup_folder: backupFolder
      });

      showModal('success', 'Settings Saved', 'Backup folder saved successfully!');
      refreshData();
    } catch (error) {
      showModal('error', 'Error', 'Error saving settings: ' + (error.response?.data?.error || error.message));
    } finally {
      setSaving(false);
    }
  };

  if (!state) {
    return <div className="text-center text-2xl text-white py-12">Loading settings...</div>;
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
      {/* Monitor Folders Section */}
      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-6 text-3xl font-bold">📁 Monitor Folders</h2>
        
        {/* Add New Monitor Folder */}
        <div className="mb-6">
          <label className="block mb-2 text-gray-700 font-medium">
            Add Monitor Folder
            <span className="block text-sm font-normal text-gray-500 mt-1">Add folders to monitor for changes (you can add multiple folders)</span>
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={newFolder}
              onChange={(e) => setNewFolder(e.target.value)}
              placeholder="e.g., C:\Users\YourName\Documents"
              className="flex-1 px-3 py-3 text-base border-2 border-gray-200 rounded-lg transition-colors focus:outline-none focus:border-indigo-500"
            />
            <button
              type="button"
              onClick={handleAddFolder}
              disabled={saving}
              className="px-6 py-3 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-lg transition-all duration-300 font-medium hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              ➕ Add
            </button>
          </div>
        </div>

        {/* List of Monitor Folders */}
        <div className="mb-6">
          <h3 className="text-gray-700 font-medium mb-3">Currently Monitored Folders:</h3>
          {monitorFolders.length === 0 ? (
            <p className="text-gray-500 italic">No folders added yet. Add a folder above to start monitoring.</p>
          ) : (
            <div className="space-y-2">
              {monitorFolders.map((folder, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <span className="text-gray-700 flex-1 break-all font-mono text-sm">{folder}</span>
                  <button
                    onClick={() => handleRemoveFolder(folder)}
                    className="ml-3 px-4 py-2 bg-red-500 text-white rounded-lg transition-all duration-300 font-medium hover:bg-red-600 text-sm whitespace-nowrap"
                  >
                    🗑️ Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Backup Folder Section */}
      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-6 text-3xl font-bold">💾 Backup Folder</h2>
        
        <div className="mb-6">
          <label className="block mb-2 text-gray-700 font-medium">
            Where backups will be stored locally
            <span className="block text-sm font-normal text-gray-500 mt-1">All backup files from monitored folders will be saved here</span>
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={backupFolder}
              onChange={(e) => setBackupFolder(e.target.value)}
              placeholder="e.g., C:\Users\YourName\Documents\Backups"
              className="flex-1 px-3 py-3 text-base border-2 border-gray-200 rounded-lg transition-colors focus:outline-none focus:border-indigo-500"
            />
            <button
              type="button"
              onClick={handleSaveBackupFolder}
              disabled={saving}
              className="px-6 py-3 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-lg transition-all duration-300 font-medium hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {saving ? '💾 Saving...' : '💾 Save'}
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white/95 rounded-xl p-8 shadow-xl mb-6">
        <h2 className="text-indigo-600 mb-6 text-3xl font-bold">ℹ️ Information</h2>
        <div className="mb-6">
          <h3 className="text-purple-600 mb-3 text-2xl font-semibold">How It Works</h3>
          <ul className="list-none p-0">
            <li className="p-3 mb-2 bg-gray-50 border-l-4 border-indigo-500 rounded">
              <strong className="text-indigo-600">Multiple Monitor Folders:</strong> You can now monitor multiple folders simultaneously! Add as many folders as you need to protect.
            </li>
            <li className="p-3 mb-2 bg-gray-50 border-l-4 border-indigo-500 rounded">
              <strong className="text-indigo-600">Backup Folder:</strong> All backups from all monitored folders are saved to one central backup location.
            </li>
            <li className="p-3 mb-2 bg-gray-50 border-l-4 border-indigo-500 rounded">
              <strong className="text-indigo-600">Cloud Backup:</strong> Every 30 minutes (or manually), local backups are uploaded to MongoDB Atlas.
            </li>
          </ul>
        </div>

        <div className="mb-6">
          <h3 className="text-purple-600 mb-3 text-2xl font-semibold">💡 Usage Tips</h3>
          <ul className="list-none p-0">
            <li className="p-3 mb-2 bg-gray-50 border-l-4 border-indigo-500 rounded">
              <strong className="text-indigo-600">Monitor Entire Drives:</strong> You can monitor entire drives like <code className="bg-gray-100 px-2 py-1 rounded font-mono text-purple-600">C:\</code> or <code className="bg-gray-100 px-2 py-1 rounded font-mono text-purple-600">D:\</code>
              <span className="block text-xs text-orange-600 mt-1">⚠️ Warning: Monitoring C:\ will backup ALL system files and may create many backups!</span>
            </li>
            <li className="p-3 mb-2 bg-gray-50 border-l-4 border-indigo-500 rounded">
              <strong className="text-indigo-600">Monitored Folders:</strong> You can add multiple folders - each folder is monitored independently.
            </li>
            <li className="p-3 mb-2 bg-gray-50 border-l-4 border-indigo-500 rounded">
              <strong className="text-indigo-600">Recommended:</strong> Instead of monitoring C:\, monitor specific folders like <code className="bg-gray-100 px-2 py-1 rounded font-mono text-purple-600">C:\Users\YourName\Documents</code> or <code className="bg-gray-100 px-2 py-1 rounded font-mono text-purple-600">C:\Users\YourName\Desktop</code>
            </li>
            <li className="p-3 mb-2 bg-gray-50 border-l-4 border-indigo-500 rounded">
              Stop monitoring before adding/removing folders.
            </li>
            <li className="p-3 mb-2 bg-gray-50 border-l-4 border-indigo-500 rounded">
              Use absolute paths (full folder paths) for best results.
            </li>
          </ul>
        </div>
      </div>
    </div>
    </>
  );
}

export default Settings;

