export interface User {
  id?: number;
  username: string;
  email?: string;
}

export interface Point {
  id: number;
  x: number;
  y: number;
  r: number;
  hit: boolean;
  /** UNIX epoch millis (UTC) — используй new Date(createdAt) для отображения */
  createdAt: number;
  executionTime: number;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user?: User;
  token?: string;
  refreshToken?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
  deviceName?: string;
}

export interface RegisterRequest {
  username: string;
  email?: string;
  password: string;
  deviceName?: string;
}

