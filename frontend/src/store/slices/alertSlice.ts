import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Alert, AlertStats } from '../../types';
import { alertService } from '../../services/alertService';

interface AlertState {
  alerts: Alert[];
  stats: AlertStats | null;
  isLoading: boolean;
  error: string | null;
  filters: any;
}

const initialState: AlertState = {
  alerts: [],
  stats: null,
  isLoading: false,
  error: null,
  filters: {},
};

export const fetchAlerts = createAsyncThunk('alerts/fetchAlerts', async (filters: any = {}) => {
  return await alertService.getAlerts(filters);
});

export const fetchAlertStats = createAsyncThunk('alerts/fetchStats', async () => {
  return await alertService.getAlertStats();
});

export const acknowledgeAlert = createAsyncThunk('alerts/acknowledge', async (id: number) => {
  return await alertService.acknowledgeAlert(id);
});

export const resolveAlert = createAsyncThunk('alerts/resolve', async ({ id, notes }: { id: number; notes?: string }) => {
  return await alertService.resolveAlert(id, notes);
});

const alertSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<any>) => {
      state.filters = action.payload;
    },
    addAlert: (state, action: PayloadAction<Alert>) => {
      state.alerts.unshift(action.payload);
    },
    updateAlert: (state, action: PayloadAction<Alert>) => {
      const index = state.alerts.findIndex(a => a.id === action.payload.id);
      if (index !== -1) {
        state.alerts[index] = action.payload;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAlerts.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.isLoading = false;
        state.alerts = action.payload;
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao carregar alertas';
      })
      .addCase(fetchAlertStats.fulfilled, (state, action) => {
        state.stats = action.payload;
      })
      .addCase(acknowledgeAlert.fulfilled, (state, action) => {
        const index = state.alerts.findIndex(a => a.id === action.payload.id);
        if (index !== -1) {
          state.alerts[index] = action.payload;
        }
      })
      .addCase(resolveAlert.fulfilled, (state, action) => {
        const index = state.alerts.findIndex(a => a.id === action.payload.id);
        if (index !== -1) {
          state.alerts[index] = action.payload;
        }
      });
  },
});

export const { setFilters, addAlert, updateAlert, clearError } = alertSlice.actions;
export default alertSlice.reducer;
