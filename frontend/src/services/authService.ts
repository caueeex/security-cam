import axios from 'axios';
import { User } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class AuthService {
  private baseURL = `${API_BASE_URL}/api/v1/auth`;

  async login(credentials: { username: string; password: string }) {
    const response = await axios.post(`${this.baseURL}/login`, credentials);
    return response.data;
  }

  async logout() {
    const token = localStorage.getItem('token');
    if (token) {
      await axios.post(`${this.baseURL}/logout`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    }
  }

  async getCurrentUser(): Promise<User> {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Token não encontrado');
    }

    const response = await axios.get(`${this.baseURL}/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  }

  async refreshToken() {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Token não encontrado');
    }

    const response = await axios.post(`${this.baseURL}/refresh`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  }

  async changePassword(currentPassword: string, newPassword: string) {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Token não encontrado');
    }

    const response = await axios.post(`${this.baseURL}/change-password`, {
      current_password: currentPassword,
      new_password: newPassword
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    return response.data;
  }
}

export const authService = new AuthService();
