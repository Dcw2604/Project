import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [authToken, setAuthToken] = useState(null);
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for stored auth token
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    
    if (token && userData) {
      setAuthToken(token);
      setUser(JSON.parse(userData));
      setIsAuthenticated(true);
    }
  }, []);

  const login = (token, userData) => {
    console.log('Setting auth state:', { token, userData });
    localStorage.setItem('authToken', token);
    localStorage.setItem('userData', JSON.stringify(userData));
    setAuthToken(token);
    setUser(userData);
    setIsAuthenticated(true);
    console.log('Auth state set');
  };

  const loginWithCredentials = async (username, password) => {
    try {
<<<<<<< HEAD
      const response = await fetch('http://127.0.0.1:8000/api/token/', {
=======
      const response = await fetch('http://127.0.0.1:8000/api/login/', {
>>>>>>> daniel
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
<<<<<<< HEAD
        const token = data.access;
        const userData = { username }; // You can expand this with more user data if needed
        login(token, userData);
        return { success: true };
      } else {
        return { success: false, error: 'Invalid credentials' };
=======
        const token = data.token;  // Use 'token' instead of 'access'
        const userData = data.user;  // Get user data from response
        login(token, userData);
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Invalid credentials' };
>>>>>>> daniel
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    setAuthToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

<<<<<<< HEAD
=======
  const clearCache = () => {
    console.log('Clearing auth cache...');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    setAuthToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

>>>>>>> daniel
  return {
    authToken,
    user,
    isAuthenticated,
    login,
    loginWithCredentials,
<<<<<<< HEAD
    logout
=======
    logout,
    clearCache
>>>>>>> daniel
  };
};