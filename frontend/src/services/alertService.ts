import axios from 'axios';
import { Alert, AlertStats } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class AlertService {
  private baseURL = `${API_BASE_URL}/api/v1/alerts`;

  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async getAlerts(params?: any): Promise<Alert[]> {
    const response = await axios.get(this.baseURL, {
      params,
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async getAlert(id: number): Promise<Alert> {
    const response = await axios.get(`${this.baseURL}/${id}`, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async createAlert(alertData: any): Promise<Alert> {
    const response = await axios.post(this.baseURL, alertData, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async updateAlert(id: number, alertData: any): Promise<Alert> {
    const response = await axios.put(`${this.baseURL}/${id}`, alertData, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async deleteAlert(id: number): Promise<void> {
    await axios.delete(`${this.baseURL}/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  async getAlertStats(params?: any): Promise<AlertStats> {
    const response = await axios.get(`${this.baseURL}/stats/overview`, {
      params,
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async acknowledgeAlert(id: number): Promise<Alert> {
    const response = await axios.post(`${this.baseURL}/${id}/acknowledge`, {}, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async resolveAlert(id: number, resolution_notes?: string, resolved_by?: string): Promise<Alert> {
    const response = await axios.post(`${this.baseURL}/${id}/resolve`, {}, {
      params: { resolution_notes, resolved_by },
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async getAlertNotifications(id: number): Promise<any[]> {
    const response = await axios.get(`${this.baseURL}/${id}/notifications`, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }
}

export const alertService = new AlertService();
