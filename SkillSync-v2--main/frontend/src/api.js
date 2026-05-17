export const apiBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const ACCESS_TOKEN_KEY = "skillsync_access";
const REFRESH_TOKEN_KEY = "skillsync_refresh";

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens({ access, refresh }) {
  if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export async function apiFetch(path, options = {}, auth = true) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (auth) {
    const token = getAccessToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers,
  });

  let data = null;
  try {
    data = await response.json();
  } catch (err) {
    data = null;
  }

  if (!response.ok) {
    let detail = data?.detail || data?.error;
    if (!detail && data && typeof data === "object") {
      const firstKey = Object.keys(data)[0];
      if (firstKey) {
        const value = data[firstKey];
        if (Array.isArray(value)) {
          detail = value.join(" ");
        } else if (typeof value === "string") {
          detail = value;
        } else {
          detail = "Request failed";
        }
      }
    }
    detail = detail || "Request failed";
    throw new Error(detail);
  }

  return data;
}

export async function login(identifier, password) {
  const data = await apiFetch(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ identifier, password }),
    },
    false
  );
  setTokens(data);
  return data;
}

export async function register(payload) {
  return apiFetch(
    "/auth/register",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    false
  );
}

export async function getMe() {
  return apiFetch("/auth/me");
}

export async function updateMe(payload) {
  return apiFetch("/auth/me", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}
