import { useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { setConnectionStatus, messageReceived, setError } from '../store/slices/websocketSlice';

export const useWebSocket = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { isConnected, connectionStatus } = useSelector((state: RootState) => state.websocket);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = () => {
    try {
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        dispatch(setConnectionStatus('connected'));
        console.log('WebSocket conectado');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          dispatch(messageReceived(message));
        } catch (error) {
          console.error('Erro ao processar mensagem WebSocket:', error);
        }
      };

      wsRef.current.onclose = () => {
        dispatch(setConnectionStatus('disconnected'));
        console.log('WebSocket desconectado');
        
        // Tentar reconectar após 5 segundos
        reconnectTimeoutRef.current = setTimeout(() => {
          if (wsRef.current?.readyState === WebSocket.CLOSED) {
            connect();
          }
        }, 5000);
      };

      wsRef.current.onerror = (error) => {
        dispatch(setConnectionStatus('error'));
        dispatch(setError('Erro na conexão WebSocket'));
        console.error('Erro WebSocket:', error);
      };

    } catch (error) {
      dispatch(setConnectionStatus('error'));
      dispatch(setError('Erro ao conectar WebSocket'));
      console.error('Erro ao conectar WebSocket:', error);
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const sendMessage = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, []);

  return {
    isConnected,
    connectionStatus,
    sendMessage,
    connect,
    disconnect,
  };
};
