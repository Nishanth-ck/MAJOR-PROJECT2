// API Configuration
// Use environment variable for backend URL, fallback to relative path for development
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

// Helper function to get full API URL
export const getApiUrl = (endpoint) => {
  // Remove leading slash from endpoint if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  
  // If API_BASE_URL is set, use it, otherwise use relative path
  if (API_BASE_URL) {
    // Remove trailing slash from base URL if present
    const cleanBaseUrl = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
    return `${cleanBaseUrl}/${cleanEndpoint}`;
  }
  
  // For development or when no base URL is set, use relative path
  return `/${cleanEndpoint}`;
};

export default getApiUrl;

