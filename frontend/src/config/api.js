// API Configuration
// Use environment variable for backend URL, fallback to relative path for development
const API_BASE_URL = process.env.REACT_APP_API_URL || '';
const LOCAL_CLIENT_URL = 'http://localhost:5001';

// Check if local client is available
let useLocalClient = false;
let clientCheckPromise = null;

// Helper function to check if local client is available
export const checkLocalClient = async () => {
  // If already checking, return the existing promise
  if (clientCheckPromise) {
    return clientCheckPromise;
  }
  
  clientCheckPromise = (async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1000);
      
      const response = await fetch(`${LOCAL_CLIENT_URL}/api/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        useLocalClient = true;
        return true;
      }
    } catch (e) {
      // Local client not available
      useLocalClient = false;
    } finally {
      clientCheckPromise = null;
    }
    return false;
  })();
  
  return clientCheckPromise;
};

// Helper function to get full API URL
export const getApiUrl = async (endpoint) => {
  // Remove leading slash from endpoint if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  
  // Check if local client is available for file system operations
  const isFileSystemOperation = (
    endpoint.includes('monitoring') || 
    endpoint.includes('upload') || 
    (endpoint.includes('state') && !endpoint.includes('client')) ||
    endpoint.includes('status')
  );
  
  if (isFileSystemOperation) {
    // Check local client availability
    const clientAvailable = await checkLocalClient();
    if (clientAvailable) {
      return `${LOCAL_CLIENT_URL}/${cleanEndpoint}`;
    }
  }
  
  // If API_BASE_URL is set, use it, otherwise use relative path
  if (API_BASE_URL) {
    // Remove trailing slash from base URL if present
    const cleanBaseUrl = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
    return `${cleanBaseUrl}/${cleanEndpoint}`;
  }
  
  // For development or when no base URL is set, use relative path
  return `/${cleanEndpoint}`;
};

// Initialize local client check on module load
checkLocalClient();

export default getApiUrl;

