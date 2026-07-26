import type { Client, Dashboard, PPECompliance, PPEIssue, PPEItem, Product, ResponseEnvelope, User } from '../types/api';

const API_PREFIX = import.meta.env.VITE_API_URL ?? '/api/v1';
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
  const response = await fetch(`${API_PREFIX}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  const envelope = (await response.json()) as ResponseEnvelope<T>;

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
  products: (search = '', lowStockOnly = false) =>
    request<Product[]>(`/inventory/products?per_page=10&low_stock_only=${lowStockOnly}${search ? `&search=${encodeURIComponent(search)}` : ''}`),
  ppeCompliance: () => request<PPECompliance>('/ppe/compliance'),
  ppeItems: () => request<PPEItem[]>('/ppe/items'),
  ppeIssues: () => request<PPEIssue[]>('/ppe/issues'),
};
