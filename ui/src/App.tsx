import React, { useState, useEffect, useRef } from 'react';
import { FiSettings, FiPlay, FiSquare, FiX } from 'react-icons/fi';
import './App.css';
import { useAppStore } from './store';
import { ConsolePanel } from './components/ConsolePanel';
import { ErrorBanner } from './components/ErrorBanner';
import Settings from './components/Settings';
import { API_BASE_URL } from './config';
import { invoke } from '@tauri-apps/api/tauri';
import { WebviewWindow, getCurrent } from '@tauri-apps/api/window';

const App: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConsole, setShowConsole] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [windowLabel, setWindowLabel] = useState<string>('main');
  const inputRef = useRef<HTMLInputElement>(null);
  
  const { 
    activeJobId, 
    setActiveJobId, 
    isConnected,
    connect,
    disconnect
  } = useAppStore();

  // Focus input when app becomes visible
  useEffect(() => {
    const focusInput = () => {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    };

    window.addEventListener('focus', focusInput);
    focusInput(); // Focus on initial load

    return () => {
      window.removeEventListener('focus', focusInput);
    };
  }, []);

  // Connect to WebSocket on mount
  useEffect(() => {
    connect();
    
    // Check API server status
    checkApiStatus();
    
    // Check if this is a secondary window (settings or console)
    checkWindowType();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);
  
  // Check window type to determine what to render
  const checkWindowType = async () => {
    try {
      const currentWindow = getCurrent();
      const label = currentWindow.label;
      setWindowLabel(label);
      
      if (label === 'settings') {
        setShowSettings(true);
        setShowConsole(false);
      } else if (label === 'console') {
        setShowSettings(false);
        setShowConsole(true);
      }
    } catch (err) {
      console.error('Error checking window type:', err);
    }
  };

  // Check if API server is running
  const checkApiStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/`);
      if (!response.ok) {
        setError('API server is not responding properly');
      }
    } catch (err) {
      setError('Cannot connect to API server. Please make sure it is running.');
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) return;
    if (isLoading) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt, max_retries: 3 }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }
      
      const data = await response.json();
      setActiveJobId(data.job_id);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle stop button click
  const handleStop = async () => {
    if (!activeJobId) return;
    
    try {
      setIsLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_id: activeJobId }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }
      
      // Job stopped successfully
      setActiveJobId(null);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop the job');
    } finally {
      setIsLoading(false);
    }
  };

  // Open settings in a new window
  const openSettings = async () => {
    try {
      await invoke('open_settings');
    } catch (err) {
      console.error('Error opening settings:', err);
      // Fallback to inline settings if window creation fails
      setShowSettings(true);
    }
  };

  // Close settings
  const closeSettings = () => {
    // If this is a settings window, close it
    if (windowLabel === 'settings') {
      const currentWindow = getCurrent();
      currentWindow.close();
    } else {
      // Otherwise just hide the inline settings
      setShowSettings(false);
    }
  };
  
  // Hide the window
  const hideWindow = async () => {
    const currentWindow = getCurrent();
    currentWindow.hide();
  };
  
  // Render settings window content
  if (showSettings) {
    return <Settings onClose={closeSettings} />;
  }
  
  // Render console window content
  if (showConsole) {
    return <ConsolePanel onClose={() => getCurrent().close()} isConnected={isConnected} />;
  }

  // Render main window content (macOS-style spotlight UI)
  return (
    <div data-tauri-drag-region className="spotlight-wrapper">
      {error && <ErrorBanner message={error} onClose={() => setError(null)} />}
      
      <div className="spotlight-pill">
        <div className="spotlight-content">
          <div className="logo-container">
            <img 
              src="https://raw.githubusercontent.com/devdattatalele/Krya.ai/dd43de46ca6e19e7dfcae0a3eff27d889d984531/assests/krya_logo.svg" 
              alt="Krya.AI Logo" 
              className="app-logo" 
            />
          </div>
          
          <form onSubmit={handleSubmit} className="prompt-form">
            <input
              ref={inputRef}
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your automation prompt..."
              disabled={isLoading}
              aria-label="Automation prompt"
              className="prompt-input"
              autoFocus
            />
            
            <div className="spotlight-actions">
              <button
                type="button"
                onClick={openSettings}
                className="icon-button settings-button"
                aria-label="Open settings"
              >
                <FiSettings />
              </button>
              
              {activeJobId ? (
                <button
                  type="button"
                  onClick={handleStop}
                  className="action-button stop-button"
                  disabled={isLoading}
                  aria-label="Stop automation"
                >
                  <FiSquare /> {isLoading ? 'Stopping...' : 'Stop'}
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={isLoading || !prompt.trim()}
                  className="action-button run-button"
                  aria-label="Run automation"
                >
                  <FiPlay /> {isLoading ? 'Running...' : 'Run'}
                </button>
              )}
              
              <button
                type="button"
                onClick={hideWindow}
                className="icon-button close-button"
                aria-label="Close"
              >
                <FiX />
              </button>
            </div>
          </form>
        </div>
        
        <div className="connection-indicator">
          <div className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></div>
        </div>
      </div>
    </div>
  );
};

export default App; 