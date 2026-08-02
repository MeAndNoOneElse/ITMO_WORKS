import api from './api';
import type { Point } from '../models/types';

interface ClearResponse {
  success: boolean;
  message: string;
}

export async function addPoint(x: number, y: number, r: number): Promise<Point> {
  const res = await api.post<Point>('/results/check', { x, y, r });
  return res.data;
}

export async function getPoints(): Promise<Point[]> {
  const res = await api.get<Point[]>('/results');
  return res.data;
}

export async function clearPoints(): Promise<ClearResponse> {
  const res = await api.delete<ClearResponse>('/results');
  return res.data;
}

