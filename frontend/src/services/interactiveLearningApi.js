// API service for interactive learning with Ollama

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class InteractiveLearningApiService {
  // Helper method to get auth headers
  getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Token ${token}` })
    };
  }

  // Handle API response
  async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.error || 'API request failed');
    }
    return response.json();
  }

  // Start an interactive learning session (uses Ollama)
  async startSession(topic = 'Linear Equations') {
    try {
      console.log(`🎓 Starting interactive learning session for topic: ${topic}`);
      const response = await fetch(`${API_BASE_URL}/interactive/start/`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ topic }),
      });
      const result = await this.handleResponse(response);
      console.log('✅ Session started:', result);
      return result;
    } catch (error) {
      console.error('❌ Error starting interactive learning:', error);
      throw error;
    }
  }

  // Submit answer to interactive learning session (uses Ollama for checking)
  async submitAnswer(sessionId, message) {
    try {
      console.log(`📝 Submitting answer for session ${sessionId}: "${message}"`);
      const response = await fetch(`${API_BASE_URL}/interactive/chat/${sessionId}/`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ message }),
      });
      const result = await this.handleResponse(response);
      console.log('✅ Answer processed:', result);
      return result;
    } catch (error) {
      console.error('❌ Error submitting answer:', error);
      throw error;
    }
  }

  // Get interactive learning progress
  async getProgress(sessionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/interactive/progress/${sessionId}/`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });
      const result = await this.handleResponse(response);
      return result;
    } catch (error) {
      console.error('❌ Error fetching progress:', error);
      throw error;
    }
  }

  // End interactive learning session
  async endSession(sessionId) {
    try {
      console.log(`🏁 Ending session ${sessionId}`);
      const response = await fetch(`${API_BASE_URL}/interactive/end/${sessionId}/`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });
      const result = await this.handleResponse(response);
      console.log('✅ Session ended:', result);
      return result;
    } catch (error) {
      console.error('❌ Error ending session:', error);
      throw error;
    }
  }

  // Alternative: Submit answer to structured learning
  async submitStructuredAnswer(sessionId, answer) {
    try {
      console.log(`📚 Submitting structured answer for session ${sessionId}: "${answer}"`);
      const response = await fetch(`${API_BASE_URL}/learning/answer/`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ session_id: sessionId, answer }),
      });
      const result = await this.handleResponse(response);
      console.log('✅ Structured answer processed:', result);
      return result;
    } catch (error) {
      console.error('❌ Error submitting structured answer:', error);
      throw error;
    }
  }

  // Get available learning topics
  async getAvailableTopics() {
    try {
      const response = await fetch(`${API_BASE_URL}/learning/topics/`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });
      return this.handleResponse(response);
    } catch (error) {
      console.error('❌ Error fetching topics:', error);
      throw error;
    }
  }
}

export const interactiveLearningApi = new InteractiveLearningApiService();
export default interactiveLearningApi;
