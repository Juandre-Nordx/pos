import type { Client, CompanySettings, Dashboard, PPECompliance, PPEItem, Product, ResponseEnvelope, StockAddition, User } from '../types/api';

const RAILWAY_FRONTEND_HOST = 'pos-frontend-production.up.railway.app';
const RAILWAY_BACKEND_URL = 'https://pos-production-62cf5.up.railway.app/api/v1';

function getApiPrefix() {
  const configuredUrl = import.meta.env.VITE_API_URL?.trim();
  if (configuredUrl) {
    return configuredUrl.replace(/\/$/, '');
  }

  // The production frontend and backend are separate Railway services, so a
  // relative URL would send POST requests to Caddy on the frontend service.
  if (window.location.hostname === RAILWAY_FRONTEND_HOST) {
    return RAILWAY_BACKEND_URL;
  }

  return '/api/v1';
}

const API_PREFIX = getApiPrefix();
const TOKEN_KEY = 'nordxpos.access_token';
const REFRESH_KEY = 'nordxpos.refresh_token';

export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_KEY);
}

export function storeTokens(accessToken: string, refreshToken: string) {
  window.localStorage.setItem(TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_KEY, refreshToken);
}

export function clearTokens() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken();
  const method = options.method ?? 'GET';
  const startedAt = performance.now();
  console.info('[API] Request started', { method, path });

  let response: Response;
  try {
    response = await fetch(`${API_PREFIX}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch (error) {
    console.error('[API] Request could not reach the backend', { method, path, error });
    throw new Error('Unable to reach the server. Please try again.');
  }

  const requestLog = {
    method,
    path,
    status: response.status,
    duration_ms: Math.round(performance.now() - startedAt),
  };
  if (response.ok) {
    console.info('[API] Request completed', requestLog);
  } else {
    console.error('[API] Request failed', requestLog);
  }

  const responseBody = await response.text();
  if (response.status === 405 && path === '/auth/login') {
    throw new Error(
      'Login reached the frontend service instead of the API. Set VITE_API_URL to the backend URL and redeploy the frontend.',
    );
  }
  if (!responseBody.trim()) {
    throw new Error(
      response.ok
        ? 'The server returned an empty response'
        : `Request failed with ${response.status}${response.statusText ? ` ${response.statusText}` : ''}`,
    );
  }

  let envelope: ResponseEnvelope<T>;
  try {
    envelope = JSON.parse(responseBody) as ResponseEnvelope<T>;
  } catch {
    throw new Error(
      response.ok
        ? 'The server returned an invalid response'
        : `Request failed with ${response.status}${response.statusText ? ` ${response.statusText}` : ''}`,
    );
  }

  if (!response.ok || envelope.errors?.length) {
    throw new Error(envelope.errors?.join(', ') || `Request failed with ${response.status}`);
  }

  return envelope.data;
}

export async function login(email: string, password: string) {
  return request<{ access_token: string; refresh_token: string; token_type: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export const api = {
  me: () => request<User>('/auth/me'),
  dashboard: () => request<Dashboard>('/dashboard'),
  clients: (search = '') => request<Client[]>(`/clients?per_page=8${search ? `&search=${encodeURIComponent(search)}` : ''}`),
  products: (search = '', lowStockOnly = false, perPage = 10) =>
    request<Product[]>(`/inventory/products?per_page=${perPage}&low_stock_only=${lowStockOnly}${search ? `&search=${encodeURIComponent(search)}` : ''}`),
  ppeCompliance: () => request<PPECompliance>('/ppe/compliance'),
  ppeItems: () => request<PPEItem[]>('/ppe/items'),
  addStock: (productUuid: string, quantity: number, reason: string, reference?: string) =>
    request<StockAddition>(`/inventory/products/${productUuid}/stock`, {
      method: 'POST',
      body: JSON.stringify({ quantity, reason, reference: reference || null }),
    }),
  companySettings: () => request<CompanySettings | null>('/settings/company'),
  updateCompanySettings: (settings: CompanySettings) => request<CompanySettings>('/settings/company', {
    method: 'PUT',
    body: JSON.stringify(settings),
  }),
};
