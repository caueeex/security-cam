import axios from 'axios';
import { Detection, DetectionStats } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class DetectionService {
  private baseURL = `${API_BASE_URL}/api/v1/detections`;

  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async getDetections(params?: any): Promise<Detection[]> {
    const response = await axios.get(this.baseURL, {
      params,
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async getDetection(id: number): Promise<Detection> {
    const response = await axios.get(`${this.baseURL}/${id}`, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async createDetection(detectionData: any): Promise<Detection> {
    const response = await axios.post(this.baseURL, detectionData, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async updateDetection(id: number, detectionData: any): Promise<Detection> {
    const response = await axios.put(`${this.baseURL}/${id}`, detectionData, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async deleteDetection(id: number): Promise<void> {
    await axios.delete(`${this.baseURL}/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  async getDetectionStats(params?: any): Promise<DetectionStats> {
    const response = await axios.get(`${this.baseURL}/stats/overview`, {
      params,
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async verifyDetection(id: number, is_false_positive: boolean, notes?: string): Promise<Detection> {
    const response = await axios.post(`${this.baseURL}/${id}/verify`, {}, {
      params: { is_false_positive, notes },
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async getDetectionImage(id: number): Promise<any> {
    const response = await axios.get(`${this.baseURL}/${id}/image`, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }
}

export const detectionService = new DetectionService();
