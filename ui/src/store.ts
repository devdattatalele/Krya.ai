import { create } from 'zustand';
import { API_BASE_URL } from './config';

interface Log {
  timestamp: string;
  level: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  message: string;
  job_id: string;
}

interface AppState {
  // WebSocket connection
  isConnected: boolean;
  socket: WebSocket | null;
  reconnectAttempts: number;
  reconnectInterval: number;
  reconnectTimeout: number | null;
  
  // Logs
  logs: Log[];
  addLog: (log: Log) => void;
  clearLogs: () => void;
  
  // Active job
  activeJobId: string | null;
  setActiveJobId: (jobId: string | null) => void;
  
  // Connection management
  connect: () => void;
  disconnect: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // WebSocket connection
  isConnected: false,
  socket: null,
  reconnectAttempts: 0,
  reconnectInterval: 1000, // Start with 1 second, will increase exponentially
  reconnectTimeout: null,
  
  // Logs
  logs: [],
  addLog: (log: Log) => set(state => ({ logs: [...state.logs, log] })),
  clearLogs: () => set({ logs: [] }),
  
  // Active job
  activeJobId: null,
  setActiveJobId: (jobId: string | null) => {
    // When setting job to null (job completed), clear logs too
    if (jobId === null && get().activeJobId !== null) {
      set({ activeJobId: null, logs: [] });
    } else {
      set({ activeJobId: jobId });
    }
  },
  
  // Connection management
  connect: () => {
    // Close existing socket if any
    const currentSocket = get().socket;
    if (currentSocket) {
      currentSocket.close();
    }
    
    // Clear any existing reconnect timeout
    const reconnectTimeout = get().reconnectTimeout;
    if (reconnectTimeout !== null) {
      clearTimeout(reconnectTimeout);
      set({ reconnectTimeout: null });
    }
    
    try {
      // Create new WebSocket connection - Fix: Use the correct WebSocket URL format
      // Extract host and port from API_BASE_URL
      const apiUrl = new URL(API_BASE_URL.startsWith('http') ? API_BASE_URL : `http://${API_BASE_URL}`);
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${apiUrl.host}/logs`;
      
      console.log('Connecting to WebSocket at:', wsUrl);
      const socket = new WebSocket(wsUrl);
      
      // Setup event handlers
      socket.onopen = () => {
        set({ 
          isConnected: true, 
          socket,
          reconnectAttempts: 0,
          reconnectInterval: 1000
        });
        console.log('WebSocket connected');
      };
      
      socket.onmessage = (event) => {
        try {
          const log = JSON.parse(event.data);
          get().addLog(log);
          
          // If we receive a log with SUCCESS or ERROR level and it matches our active job,
          // consider the job completed
          if (log.job_id === get().activeJobId && 
              (log.level === 'SUCCESS' || log.level === 'ERROR')) {
            // Wait a bit to ensure all logs are received
            setTimeout(() => {
              // Only reset if this is still the active job
              if (log.job_id === get().activeJobId) {
                get().setActiveJobId(null);
              }
            }, 1000);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      socket.onclose = () => {
        // Only try to reconnect if we were previously connected
        // or if we're still on our first few attempts
        const wasConnected = get().isConnected;
        const reconnectAttempts = get().reconnectAttempts;
        
        set(state => ({ 
          isConnected: false,
          socket: null
        }));
        console.log('WebSocket disconnected');
        
        // Only attempt to reconnect if we were previously connected or on initial connection
        if (wasConnected || reconnectAttempts < 3) {
          // Attempt to reconnect with exponential backoff
          const reconnectInterval = get().reconnectInterval;
          
          const timeout = setTimeout(() => {
            if (reconnectAttempts < 5) { // Max 5 reconnect attempts
              set(state => ({
                reconnectAttempts: state.reconnectAttempts + 1,
                reconnectInterval: Math.min(30000, state.reconnectInterval * 1.5), // Max 30 seconds
                reconnectTimeout: null
              }));
              get().connect();
            }
          }, reconnectInterval);
          
          set({ reconnectTimeout: timeout });
        }
      };
      
      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      set({ socket });
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  },
  
  disconnect: () => {
    const socket = get().socket;
    if (socket) {
      socket.close();
    }
    
    // Clear any existing reconnect timeout
    const reconnectTimeout = get().reconnectTimeout;
    if (reconnectTimeout !== null) {
      clearTimeout(reconnectTimeout);
    }
    
    set({ 
      socket: null, 
      isConnected: false,
      reconnectTimeout: null,
      reconnectAttempts: 0
    });
  }
})); 