import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { WebSocketMessage } from '../../types';

interface WebSocketState {
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  messages: WebSocketMessage[];
  lastMessage: WebSocketMessage | null;
  error: string | null;
}

const initialState: WebSocketState = {
  isConnected: false,
  connectionStatus: 'disconnected',
  messages: [],
  lastMessage: null,
  error: null,
};

const websocketSlice = createSlice({
  name: 'websocket',
  initialState,
  reducers: {
    setConnectionStatus: (state, action: PayloadAction<WebSocketState['connectionStatus']>) => {
      state.connectionStatus = action.payload;
      state.isConnected = action.payload === 'connected';
    },
    messageReceived: (state, action: PayloadAction<WebSocketMessage>) => {
      state.messages.push(action.payload);
      state.lastMessage = action.payload;
      
      // Manter apenas as últimas 100 mensagens
      if (state.messages.length > 100) {
        state.messages = state.messages.slice(-100);
      }
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearMessages: (state) => {
      state.messages = [];
      state.lastMessage = null;
    },
  },
});

export const { setConnectionStatus, messageReceived, setError, clearMessages } = websocketSlice.actions;
export default websocketSlice.reducer;
