// API base URL
export const API_BASE_URL = 'http://localhost:8000';

// WebSocket reconnect settings
export const WS_MAX_RECONNECT_ATTEMPTS = 10;
export const WS_INITIAL_RECONNECT_DELAY = 1000; // 1 second
export const WS_MAX_RECONNECT_DELAY = 30000; // 30 seconds

// UI settings
export const UI_SETTINGS = {
  maxLogsToShow: 100,
  debounceDelay: 300, // ms
};

// Default model settings
export const DEFAULT_MODEL_SETTINGS = {
  model_name: 'gemini-2.5-flash',
  temperature: 1.55,
  top_p: 0.95,
  top_k: 40,
  max_output_tokens: 8192,
}; 