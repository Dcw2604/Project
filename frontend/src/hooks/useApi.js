import { useState } from "react";
import apiService from "../services/api";

const useApi = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.request(endpoint, options);
      setData(result);
    } catch (err) {
      setError(err.message || "API error");
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, fetchData };
};

export default useApi;
