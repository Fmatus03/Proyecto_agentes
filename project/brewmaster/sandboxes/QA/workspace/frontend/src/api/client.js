const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const TOKEN_KEY = 'brewmaster.auth.token';
const USER_KEY = 'brewmaster.auth.user';

function readJson(text) {
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

function normalizeError(payload, fallbackMessage) {
  if (payload?.error) return payload.error;
  if (payload?.message) return payload;
  return { code: 'request_error', message: fallbackMessage || 'request_error', details: [] };
}

export function getToken() {
  return window.localStorage.getItem(TOKEN_KEY) || '';
}

export function getStoredUser() {
  const raw = window.localStorage.getItem(USER_KEY);
  return raw ? readJson(raw) : null;
}

export function setSession(session) {
  if (session?.access_token) window.localStorage.setItem(TOKEN_KEY, session.access_token);
  if (session?.user) window.localStorage.setItem(USER_KEY, JSON.stringify(session.user));
}

export function clearSession() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

export async function api(path, options = {}) {
  const { body, skipAuth = false, headers = {}, ...fetchOptions } = options;
  const requestHeaders = { Accept: 'application/json', ...headers };
  if (body !== undefined && !(body instanceof FormData)) requestHeaders['Content-Type'] = 'application/json';
  const token = getToken();
  if (token && !skipAuth) requestHeaders.Authorization = `Bearer ${token}`;
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...fetchOptions,
      body: body === undefined || body instanceof FormData ? body : JSON.stringify(body),
      headers: requestHeaders,
    });
  } catch (error) {
    throw { code: 'network_error', message: error.message || 'network_error', details: [{ path }] };
  }
  const payload = readJson(await response.text());
  if (!response.ok) {
    throw normalizeError(payload, response.statusText || 'api_error');
  }
  return payload.data ?? payload;
}

export async function login(credentials) {
  const session = await api('/auth/login', { method: 'POST', body: credentials, skipAuth: true });
  setSession(session);
  return session;
}

export async function logout() {
  try {
    await api('/auth/logout', { method: 'POST' });
  } finally {
    clearSession();
  }
}
