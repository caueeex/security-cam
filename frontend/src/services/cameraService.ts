import axios from 'axios';
import { Camera, CameraStats } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class CameraService {
  private baseURL = `${API_BASE_URL}/api/v1/cameras`;

  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async getCameras(params?: any): Promise<Camera[]> {
    const response = await axios.get(this.baseURL, {
      params,
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async getCamera(id: number): Promise<Camera> {
    const response = await axios.get(`${this.baseURL}/${id}`, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async createCamera(cameraData: any): Promise<Camera> {
    const response = await axios.post(this.baseURL, cameraData, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async updateCamera(id: number, cameraData: any): Promise<Camera> {
    const response = await axios.put(`${this.baseURL}/${id}`, cameraData, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async deleteCamera(id: number): Promise<void> {
    await axios.delete(`${this.baseURL}/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  async getCameraStatus(id: number): Promise<any> {
    const response = await axios.get(`${this.baseURL}/${id}/status`, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async getCameraStats(id: number): Promise<CameraStats> {
    const response = await axios.get(`${this.baseURL}/${id}/stats`, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async testCameraConnection(id: number): Promise<any> {
    const response = await axios.post(`${this.baseURL}/${id}/test-connection`, {}, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }
}

export const cameraService = new CameraService();
