import React, { useState, useEffect } from 'react';
import api from './services/api';
import './App.css';

function App() {
  const [backendData, setBackendData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [authState, setAuthState] = useState({
    isAuthenticated: !!localStorage.getItem('token'),
    user: null
  });

  // Function to fetch data from backend
  const fetchBackendData = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/');
      const data = await response.json();
      setBackendData(data);
    } catch (error) {
      console.error('Error fetching data from backend:', error);
      setBackendData({ error: 'Failed to connect to backend' });
    } finally {
      setLoading(false);
    }
  };

  // Function to test authentication
  const testAuth = async () => {
    setLoading(true);
    try {
      const result = await api.userAPI.getProfile();
      if (result.success) {
        setAuthState({
          ...authState,
          isAuthenticated: true,
          user: result.data
        });
        alert(`Authenticated as: ${result.data.name || result.data.email}`);
      } else {
        alert(`Not authenticated: ${result.error}`);
        setAuthState({
          ...authState,
          isAuthenticated: false,
          user: null
        });
      }
    } catch (error) {
      console.error('Error testing auth:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch backend data on component mount
  useEffect(() => {
    fetchBackendData();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>ExperLinx Frontend</h1>
        <p>Connecting to the backend API</p>
        
        <div className="auth-status">
          <p>Status: {authState.isAuthenticated ? '✅ Authenticated' : '❌ Not Authenticated'}</p>
          {authState.user && <p>User: {authState.user.name || authState.user.email}</p>}
        </div>
        
        <div className="actions">
          <button onClick={fetchBackendData} disabled={loading}>
            {loading ? 'Loading...' : 'Test Backend Connection'}
          </button>
          
          <button onClick={testAuth} disabled={loading}>
            {loading ? 'Loading...' : 'Test Auth Status'}
          </button>
        </div>
        
        {backendData && (
          <div className="backend-response">
            <h2>Backend Response:</h2>
            <pre>{JSON.stringify(backendData, null, 2)}</pre>
          </div>
        )}
        
        <div className="api-endpoints">
          <h3>Available API Endpoints:</h3>
          <ul>
            <li><code>GET /api/v1/health</code> - Health check</li>
            <li><code>GET /api/v1/ready</code> - Readiness check</li>
            <li><code>POST /api/v1/auth/register</code> - User registration</li>
            <li><code>POST /api/v1/auth/login</code> - User login</li>
            <li><code>GET /api/v1/users/me</code> - Get user profile</li>
            <li><code>GET /api/v1/tools</code> - List available tools</li>
          </ul>
        </div>
        
        <div className="api-usage">
          <h3>How to Use the API:</h3>
          <ol>
            <li>Register a user via <code>POST /api/v1/auth/register</code></li>
            <li>Login via <code>POST /api/v1/auth/login</code> to get tokens</li>
            <li>Include the access token in the Authorization header: <code>Authorization: Bearer &lt;token&gt;</code></li>
            <li>Access protected endpoints with the token</li>
          </ol>
        </div>
      </header>
    </div>
  );
}

export default App;