import React, { useEffect, useRef } from 'react';
import { FiX, FiInfo, FiAlertTriangle, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import { useAppStore } from '../store';
import './ConsolePanel.css';

interface ConsolePanelProps {
  onClose: () => void;
  isConnected: boolean;
}

export const ConsolePanel: React.FC<ConsolePanelProps> = ({ onClose, isConnected }) => {
  const { logs, activeJobId } = useAppStore();
  const consoleEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when logs update
  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Get icon based on log level
  const getLogIcon = (level: string) => {
    switch (level) {
      case 'INFO':
        return <FiInfo className="log-icon info" />;
      case 'WARNING':
        return <FiAlertTriangle className="log-icon warning" />;
      case 'SUCCESS':
        return <FiCheckCircle className="log-icon success" />;
      case 'ERROR':
        return <FiAlertCircle className="log-icon error" />;
      default:
        return <FiInfo className="log-icon info" />;
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (e) {
      return timestamp;
    }
  };

  return (
    <div className="console-panel">
      <div className="console-header">
        <h3>Console Output {activeJobId ? `(Job: ${activeJobId.substring(0, 8)}...)` : ''}</h3>
        <div className="console-actions">
          <button onClick={onClose} className="icon-button close-button">
            <FiX />
          </button>
        </div>
      </div>

      <div className="console-content">
        {logs.length === 0 ? (
          <div className="empty-logs">
            {isConnected ? (
              "No logs yet. Waiting for activity..."
            ) : (
              "Not connected to server. Please check if the server is running."
            )}
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className={`log-entry ${log.level.toLowerCase()}`}>
              {getLogIcon(log.level)}
              <div className="log-content">
                <div className="log-timestamp">{formatTimestamp(log.timestamp)}</div>
                <div className="log-message">{log.message}</div>
              </div>
            </div>
          ))
        )}
        <div ref={consoleEndRef} />
      </div>

      <div className="connection-status">
        <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></div>
        {isConnected ? 'Connected to server' : 'Disconnected from server'}
        {activeJobId && <span> - Job running: {activeJobId.substring(0, 8)}...</span>}
      </div>
    </div>
  );
};

export default ConsolePanel; 