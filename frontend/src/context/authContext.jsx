import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // TODO: Load user from localStorage or API
    const storedUser = localStorage.getItem("educonnect_user");
    if (storedUser) setUser(JSON.parse(storedUser));
  }, []);

  const login = async (credentials) => {
    setLoading(true);
    setError(null);
    // TODO: Call API for login
    try {
      // Simulate API call
      const fakeUser = { id: 1, type: "student", ...credentials };
      setUser(fakeUser);
      localStorage.setItem("educonnect_user", JSON.stringify(fakeUser));
    } catch (err) {
      setError("Login failed");
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("educonnect_user");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
