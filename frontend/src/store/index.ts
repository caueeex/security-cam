import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import cameraSlice from './slices/cameraSlice';
import detectionSlice from './slices/detectionSlice';
import alertSlice from './slices/alertSlice';
import uiSlice from './slices/uiSlice';
import websocketSlice from './slices/websocketSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    cameras: cameraSlice,
    detections: detectionSlice,
    alerts: alertSlice,
    ui: uiSlice,
    websocket: websocketSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['websocket/messageReceived'],
        ignoredPaths: ['websocket.messages'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
