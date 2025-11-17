// src/services/api.js - Complete API Service
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.sessionId = localStorage.getItem('movi_session_id') || null;
    
    // Create axios instance with default config
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ============================================
  // SESSION MANAGEMENT
  // ============================================

  setSessionId(sessionId) {
    this.sessionId = sessionId;
    localStorage.setItem('movi_session_id', sessionId);
  }

  clearSession() {
    this.sessionId = null;
    localStorage.removeItem('movi_session_id');
  }

  getSessionId() {
    return this.sessionId;
  }

  // ============================================
  // CHAT/AGENT ENDPOINTS
  // ============================================

  async sendMessage(message, currentPage = 'busDashboard') {
    try {
      const response = await this.axiosInstance.post('/api/agent/chat', {
        message,
        currentPage,
        sessionId: this.sessionId
      });

      // Update session ID if returned
      if (response.data.sessionId) {
        this.setSessionId(response.data.sessionId);
      }

      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async sendImage(file, message, currentPage = 'busDashboard') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('message', message);
      formData.append('currentPage', currentPage);
      
      if (this.sessionId) {
        formData.append('sessionId', this.sessionId);
      }

      const response = await this.axiosInstance.post('/api/agent/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Update session ID if returned
      if (response.data.sessionId) {
        this.setSessionId(response.data.sessionId);
      }

      return response.data;
    } catch (error) {
      console.error('Error sending image:', error);
      throw error;
    }
  }

  async clearChatSession() {
    try {
      if (!this.sessionId) return;
      
      await this.axiosInstance.post('/api/agent/clear', {
        sessionId: this.sessionId
      });
      
      this.clearSession();
    } catch (error) {
      console.error('Error clearing session:', error);
      // Clear locally even if API call fails
      this.clearSession();
    }
  }

  // ============================================
  // TRIPS ENDPOINTS
  // ============================================

  async getTrips(status = null) {
    try {
      const params = status ? { status } : {};
      const response = await this.axiosInstance.get('/api/trips/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching trips:', error);
      throw error;
    }
  }

  async getTrip(tripId) {
    try {
      const response = await this.axiosInstance.get(`/api/trips/${tripId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching trip:', error);
      throw error;
    }
  }

  // ============================================
  // ROUTES ENDPOINTS
  // ============================================

  async getRoutes(status = 'active') {
    try {
      const params = status ? { status } : {};
      const response = await this.axiosInstance.get('/api/routes/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching routes:', error);
      throw error;
    }
  }

  async getRoute(routeId) {
    try {
      const response = await this.axiosInstance.get(`/api/routes/${routeId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching route:', error);
      throw error;
    }
  }

  // ============================================
  // VEHICLES ENDPOINTS
  // ============================================

  async getVehicles() {
    try {
      const response = await this.axiosInstance.get('/api/vehicles/');
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      throw error;
    }
  }

  async getUnassignedVehicles() {
    try {
      const response = await this.axiosInstance.get('/api/vehicles/unassigned');
      return response.data;
    } catch (error) {
      console.error('Error fetching unassigned vehicles:', error);
      throw error;
    }
  }

  async getVehicle(vehicleId) {
    try {
      const response = await this.axiosInstance.get(`/api/vehicles/${vehicleId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle:', error);
      throw error;
    }
  }

  // ============================================
  // DRIVERS ENDPOINTS
  // ============================================

  async getDrivers() {
    try {
      const response = await this.axiosInstance.get('/api/drivers/');
      return response.data;
    } catch (error) {
      console.error('Error fetching drivers:', error);
      throw error;
    }
  }

  // ============================================
  // STOPS ENDPOINTS
  // ============================================

  async getStops() {
    try {
      const response = await this.axiosInstance.get('/api/stops/');
      return response.data;
    } catch (error) {
      console.error('Error fetching stops:', error);
      throw error;
    }
  }

  // ============================================
  // DASHBOARD STATS
  // ============================================

  async getDashboardStats() {
    try {
      const response = await this.axiosInstance.get('/api/dashboard/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  }

  // ============================================
  // UTILITY METHODS
  // ============================================

  async healthCheck() {
    try {
      const response = await this.axiosInstance.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      return { status: 'unhealthy' };
    }
  }
}

// Export singleton instance
const apiService = new ApiService();
export default apiService;