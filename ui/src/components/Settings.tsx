import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import './Settings.css';

interface SettingsProps {
  onClose: () => void;
}

interface Config {
  api_key?: string;
  api_key_set?: boolean;
  model_name?: string;
  temperature?: number;
  max_output_tokens?: number;
  top_p?: number;
  top_k?: number;
}

export const Settings: React.FC<SettingsProps> = ({ onClose }) => {
  const [config, setConfig] = useState<Config>({});
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Fetch current config on mount
  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/config`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch config: ${response.status}`);
      }
      
      const data = await response.json();
      setConfig(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load configuration');
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      const response = await fetch(`${API_BASE_URL}/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKey || undefined,
          model_name: config.model_name,
          temperature: config.temperature,
          max_output_tokens: config.max_output_tokens,
          top_p: config.top_p,
          top_k: config.top_k,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }
      
      setSuccess('Configuration saved successfully');
      fetchConfig(); // Refresh config
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings-page">
      <div className="settings-container">
        <div className="settings-header">
          <h2>Krya.ai Settings</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}
        
        {success && (
          <div className="success-message">
            {success}
            <button onClick={() => setSuccess(null)}>×</button>
          </div>
        )}
        
        <div className="settings-content">
          <div className="setting-group">
            <h3>API Configuration</h3>
            
            <div className="setting-item">
              <label htmlFor="api-key">Google Gemini API Key</label>
              <input
                id="api-key"
                type="password"
                placeholder={config.api_key_set ? '••••••••••••••••' : 'Enter API key'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
              <p className="setting-help">
                Get your API key from the <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a>
              </p>
            </div>
            
            <div className="setting-item">
              <label htmlFor="model-name">Model</label>
              <select
                id="model-name"
                value={config.model_name || 'gemini-2.5-flash'}
                onChange={(e) => setConfig({...config, model_name: e.target.value})}
              >
                <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
              </select>
            </div>
          </div>
          
          <div className="setting-group">
            <h3>Advanced Settings</h3>
            
            <div className="setting-item">
              <label htmlFor="temperature">Temperature</label>
              <input
                id="temperature"
                type="range"
                min="0"
                max="2"
                step="0.01"
                value={config.temperature || 1.55}
                onChange={(e) => setConfig({...config, temperature: parseFloat(e.target.value)})}
              />
              <span className="setting-value">{config.temperature?.toFixed(2) || 1.55}</span>
            </div>
            
            <div className="setting-item">
              <label htmlFor="max-tokens">Max Output Tokens</label>
              <input
                id="max-tokens"
                type="number"
                min="1"
                max="32768"
                value={config.max_output_tokens || 8192}
                onChange={(e) => setConfig({...config, max_output_tokens: parseInt(e.target.value)})}
              />
            </div>
          </div>
        </div>
        
        <div className="settings-footer">
          <button 
            className="cancel-button" 
            onClick={onClose}
          >
            Cancel
          </button>
          <button 
            className="save-button" 
            onClick={saveConfig}
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings; 