import React, { useState, useEffect } from 'react';
import { FiAlertCircle, FiX } from 'react-icons/fi';

interface ErrorBannerProps {
  message: string;
  onClose: () => void;
  autoHideDuration?: number;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ 
  message, 
  onClose, 
  autoHideDuration = 5000 
}) => {
  const [isVisible, setIsVisible] = useState(true);
  
  useEffect(() => {
    // Reset visibility when message changes
    setIsVisible(true);
    
    // Auto-hide after duration if specified
    if (autoHideDuration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(onClose, 300); // Allow animation to complete
      }, autoHideDuration);
      
      return () => clearTimeout(timer);
    }
  }, [message, autoHideDuration, onClose]);
  
  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300); // Allow animation to complete
  };
  
  return (
    <div className={`error-banner ${isVisible ? 'visible' : 'hidden'}`}>
      <div className="error-icon">
        <FiAlertCircle />
      </div>
      <div className="error-message">
        {message}
      </div>
      <button className="close-button" onClick={handleClose}>
        <FiX />
      </button>
    </div>
  );
};

export default ErrorBanner; 