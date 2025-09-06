import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Camera, CameraStats } from '../../types';
import { cameraService } from '../../services/cameraService';

interface CameraState {
  cameras: Camera[];
  selectedCamera: Camera | null;
  stats: CameraStats[];
  isLoading: boolean;
  error: string | null;
}

const initialState: CameraState = {
  cameras: [],
  selectedCamera: null,
  stats: [],
  isLoading: false,
  error: null,
};

export const fetchCameras = createAsyncThunk('cameras/fetchCameras', async () => {
  return await cameraService.getCameras();
});

export const fetchCameraStats = createAsyncThunk('cameras/fetchStats', async () => {
  return await cameraService.getCameraStats();
});

export const createCamera = createAsyncThunk('cameras/create', async (cameraData: any) => {
  return await cameraService.createCamera(cameraData);
});

export const updateCamera = createAsyncThunk('cameras/update', async ({ id, data }: { id: number; data: any }) => {
  return await cameraService.updateCamera(id, data);
});

export const deleteCamera = createAsyncThunk('cameras/delete', async (id: number) => {
  await cameraService.deleteCamera(id);
  return id;
});

const cameraSlice = createSlice({
  name: 'cameras',
  initialState,
  reducers: {
    setSelectedCamera: (state, action: PayloadAction<Camera | null>) => {
      state.selectedCamera = action.payload;
    },
    updateCameraStatus: (state, action: PayloadAction<{ id: number; is_online: boolean }>) => {
      const camera = state.cameras.find(c => c.id === action.payload.id);
      if (camera) {
        camera.is_online = action.payload.is_online;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCameras.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCameras.fulfilled, (state, action) => {
        state.isLoading = false;
        state.cameras = action.payload;
      })
      .addCase(fetchCameras.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao carregar câmeras';
      })
      .addCase(createCamera.fulfilled, (state, action) => {
        state.cameras.push(action.payload);
      })
      .addCase(updateCamera.fulfilled, (state, action) => {
        const index = state.cameras.findIndex(c => c.id === action.payload.id);
        if (index !== -1) {
          state.cameras[index] = action.payload;
        }
      })
      .addCase(deleteCamera.fulfilled, (state, action) => {
        state.cameras = state.cameras.filter(c => c.id !== action.payload);
      });
  },
});

export const { setSelectedCamera, updateCameraStatus, clearError } = cameraSlice.actions;
export default cameraSlice.reducer;
