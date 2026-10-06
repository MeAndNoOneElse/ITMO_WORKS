import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Point } from '../models/types';
import { Observable } from 'rxjs';

interface ClearResultsResponse {
  success: boolean;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class PointService {
  private http = inject(HttpClient);
  private baseUrl = '/api/results';

  addPoint(point: {x: number, y: number, r: number}): Observable<Point> {
    console.log('[PointService] Добавление точки:', point);
    return this.http.post<Point>(`${this.baseUrl}/check`, point);
  }

  getPoints(): Observable<Point[]> {
    console.log('[PointService] Запрос всех точек');
    return this.http.get<Point[]>(this.baseUrl);
  }

  clearPoints(): Observable<ClearResultsResponse> {
    console.log('[PointService] Очистка точек');
    return this.http.delete<ClearResultsResponse>(this.baseUrl);
  }
}


