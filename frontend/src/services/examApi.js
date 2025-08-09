// API service for exam session management

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ExamApiService {
  // Helper method to get auth headers
  getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Handle API response
  async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    return response.json();
  }

  // Fetch all topics with question counts
  async getTopics() {
    try {
      const response = await fetch(`${API_BASE_URL}/topics/`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching topics:', error);
      throw error;
    }
  }

  // Fetch chat-generated questions with filtering
  async getQuestions(filters = {}) {
    try {
      const queryParams = new URLSearchParams({
        is_generated: 'true', // Only chat-generated questions
        ...filters
      });
      
      const response = await fetch(`${API_BASE_URL}/questions/?${queryParams}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching questions:', error);
      throw error;
    }
  }

  // Create a new exam session
  async createExamSession(examData) {
    try {
      const response = await fetch(`${API_BASE_URL}/exam-sessions/`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(examData),
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error creating exam session:', error);
      throw error;
    }
  }

  // Get exam session details
  async getExamSession(id) {
    try {
      const response = await fetch(`${API_BASE_URL}/exam-sessions/${id}/`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching exam session:', error);
      throw error;
    }
  }

  // List all exam sessions for the current teacher
  async getExamSessions() {
    try {
      const response = await fetch(`${API_BASE_URL}/exam-sessions/`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error fetching exam sessions:', error);
      throw error;
    }
  }

  // Update exam session
  async updateExamSession(id, examData) {
    try {
      const response = await fetch(`${API_BASE_URL}/exam-sessions/${id}/`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(examData),
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error('Error updating exam session:', error);
      throw error;
    }
  }

  // Delete exam session
  async deleteExamSession(id) {
    try {
      const response = await fetch(`${API_BASE_URL}/exam-sessions/${id}/`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete exam session');
      }
      return true;
    } catch (error) {
      console.error('Error deleting exam session:', error);
      throw error;
    }
  }
}

export const examApi = new ExamApiService();
export default examApi;
