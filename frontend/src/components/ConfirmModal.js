import React from 'react';

function ConfirmModal({ isOpen, onClose, onConfirm, type = 'warning', title, message }) {
  if (!isOpen) return null;

  const getModalStyle = () => {
    switch (type) {
      case 'danger':
        return {
          border: 'border-red-500',
          bg: 'bg-red-50',
          icon: '⚠️',
          titleColor: 'text-red-700',
        };
      case 'warning':
        return {
          border: 'border-yellow-500',
          bg: 'bg-yellow-50',
          icon: '⚠️',
          titleColor: 'text-yellow-700',
        };
      default:
        return {
          border: 'border-blue-500',
          bg: 'bg-blue-50',
          icon: 'ℹ️',
          titleColor: 'text-blue-700',
        };
    }
  };

  const style = getModalStyle();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className={`bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 border-2 ${style.border}`}>
        {/* Header */}
        <div className={`${style.bg} px-6 py-4 rounded-t-xl border-b-2 ${style.border}`}>
          <div className="flex items-center justify-between">
            <h3 className={`text-xl font-bold ${style.titleColor} flex items-center gap-2`}>
              <span>{style.icon}</span>
              {title}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 transition-colors text-2xl leading-none"
              aria-label="Close"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-gray-700 whitespace-pre-line">{message}</p>
        </div>

        {/* Footer */}
        <div className={`${style.bg} px-6 py-4 rounded-b-xl flex justify-end gap-3`}>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg font-medium transition-all duration-300 hover:bg-gray-400"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className={`px-6 py-2 rounded-lg font-medium transition-all duration-300 ${
              type === 'danger'
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmModal;

