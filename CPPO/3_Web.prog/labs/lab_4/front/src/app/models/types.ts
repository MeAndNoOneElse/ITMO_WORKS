export interface User {
  username: string;
  password?: string;
  id?: number;
  email?: string;
  createdAt?: number;
}

export interface Point {
  id: number;
  x: number;
  y: number;
  r: number;
  hit: boolean;
  createdAt: string;
  executionTime: number;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user?: User;
  token?: string;
  refreshToken?: string;
  sessionId?: number;
  hasActiveSessions?: boolean;
  closedSessions?: SessionInfo[];
  activeSessions?: SessionInfo[];
  isCurrentSession?: boolean;
}

export interface SessionInfo {
  id: number;
  deviceName: string;
  ipAddress: string;
  createdAt: string;
  refreshExpiresAt: string;
}


export interface LoginRequest {
  username: string;
  password: string;
  deviceName?: string;
  expirationMinutes?: number;
  sessionIdsToClose?: number[];
  useExistingSessionId?: number;
  createNewSession?: boolean;
}

export interface RegisterRequest {
  username: string;
  email?: string;
  password: string;
  deviceName?: string;
  expirationMinutes?: number;
}

