import api from './api';
import type { AuthResponse, LoginRequest, RegisterRequest } from '../models/types';

const TOKEN_KEY = 'jwt_token';
const REFRESH_KEY = 'refresh_token';

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

export function saveTokens(token: string, refreshToken: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(REFRESH_KEY, refreshToken);
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function isLoggedIn(): boolean {
  return !!getAccessToken();
}

export function getDeviceName(): string {
  const ua = navigator.userAgent;
  if (/mobile/i.test(ua)) return 'Mobile Browser';
  if (/tablet/i.test(ua)) return 'Tablet Browser';
  return 'Desktop Browser';
}

export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  const res = await api.post<AuthResponse>('/auth/login', {
    ...credentials,
    deviceName: credentials.deviceName || getDeviceName()
  });
  const data = res.data;
  if (data.success && data.token && data.refreshToken) {
    saveTokens(data.token, data.refreshToken);
  }
  return data;
}

export async function register(credentials: RegisterRequest): Promise<AuthResponse> {
  const res = await api.post<AuthResponse>('/auth/register', {
    ...credentials,
    deviceName: credentials.deviceName || getDeviceName()
  });
  const data = res.data;
  if (data.success && data.token && data.refreshToken) {
    saveTokens(data.token, data.refreshToken);
  }
  return data;
}

export async function logout(): Promise<void> {
  const token = getAccessToken();
  if (token) {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        keepalive: true
      });
    } catch {
      // ignore
    }
  }
  clearTokens();
}

