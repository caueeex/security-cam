import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Detection, DetectionStats } from '../../types';
import { detectionService } from '../../services/detectionService';

interface DetectionState {
  detections: Detection[];
  stats: DetectionStats | null;
  isLoading: boolean;
  error: string | null;
  filters: any;
}

const initialState: DetectionState = {
  detections: [],
  stats: null,
  isLoading: false,
  error: null,
  filters: {},
};

export const fetchDetections = createAsyncThunk('detections/fetchDetections', async (filters: any = {}) => {
  return await detectionService.getDetections(filters);
});

export const fetchDetectionStats = createAsyncThunk('detections/fetchStats', async () => {
  return await detectionService.getDetectionStats();
});

export const verifyDetection = createAsyncThunk('detections/verify', async ({ id, is_false_positive, notes }: { id: number; is_false_positive: boolean; notes?: string }) => {
  return await detectionService.verifyDetection(id, is_false_positive, notes);
});

const detectionSlice = createSlice({
  name: 'detections',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<any>) => {
      state.filters = action.payload;
    },
    addDetection: (state, action: PayloadAction<Detection>) => {
      state.detections.unshift(action.payload);
    },
    updateDetection: (state, action: PayloadAction<Detection>) => {
      const index = state.detections.findIndex(d => d.id === action.payload.id);
      if (index !== -1) {
        state.detections[index] = action.payload;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDetections.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchDetections.fulfilled, (state, action) => {
        state.isLoading = false;
        state.detections = action.payload;
      })
      .addCase(fetchDetections.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao carregar detecções';
      })
      .addCase(fetchDetectionStats.fulfilled, (state, action) => {
        state.stats = action.payload;
      })
      .addCase(verifyDetection.fulfilled, (state, action) => {
        const index = state.detections.findIndex(d => d.id === action.payload.id);
        if (index !== -1) {
          state.detections[index] = action.payload;
        }
      });
  },
});

export const { setFilters, addDetection, updateDetection, clearError } = detectionSlice.actions;
export default detectionSlice.reducer;
