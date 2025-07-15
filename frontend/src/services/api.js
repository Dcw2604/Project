class ApiService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api";
    this.timeout = 10000;
  }

  async request(endpoint, options = {}) {
    const token = localStorage.getItem("authToken");
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Example endpoints
  async getStudentClasses(studentId) {
    return this.request(`/students/${studentId}/classes`);
  }
  async bookClass(classId, studentId) {
    return this.request(`/classes/${classId}/book`, {
      method: "POST",
      body: JSON.stringify({ studentId }),
    });
  }
  async getTeacherRequests(teacherId) {
    return this.request(`/teachers/${teacherId}/requests`);
  }
  async approveClassRequest(requestId) {
    return this.request(`/requests/${requestId}/approve`, {
      method: "PUT",
    });
  }
}

export default new ApiService();
