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
      const response = await fetch('http://127.0.0.1:8000/api/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const token = data.access;
        const userData = { username }; // You can expand this with more user data if needed
        login(token, userData);
        return { success: true };
      } else {
        return { success: false, error: 'Invalid credentials' };
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

  return {
    authToken,
    user,
    isAuthenticated,
    login,
    loginWithCredentials,
    logout
  };
};