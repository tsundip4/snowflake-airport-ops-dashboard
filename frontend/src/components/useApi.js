import { useMemo } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function fetchJson(path, options = {}, token = "", timeoutMs = 60000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {})
      }
    });
    const text = await res.text();
    const data = text ? JSON.parse(text) : null;
    if (!res.ok) {
      const detail = data?.detail || data?.message || text || res.statusText;
      throw new Error(detail);
    }
    return data;
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Request timed out");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

function useApi(token) {
  const authToken = useMemo(() => token, [token]);

  const apiRequest = async (path, options = {}) => {
    const timeoutMs = options.timeoutMs || 60000;
    return await fetchJson(path, options, authToken, timeoutMs);
  };

  return { apiRequest };
}

export default useApi;
