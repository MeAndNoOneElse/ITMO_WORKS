import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError, switchMap, from } from 'rxjs';
import { AuthService } from '../services/auth';

let isRefreshing = false;

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const authService = inject(AuthService);
  const token = localStorage.getItem('jwt_token');

  const publicEndpoints = [
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/refresh'
  ];

  const isPublicEndpoint = publicEndpoints.some(endpoint => req.url.includes(endpoint));

  let cloned = req;
  if (token && token.trim() !== '' && !isPublicEndpoint) {
    cloned = req.clone({
      setHeaders: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
  } else if (!isPublicEndpoint && !token) {
    console.warn('[AuthInterceptor] Нет токена для защищенного эндпоинта:', req.url);
  }

  return next(cloned).pipe(
    catchError((error: HttpErrorResponse) => {
      // Если получили 401 Unauthorized - пытаемся обновить токен
      if (error.status === 401 && !isPublicEndpoint && !isRefreshing) {
        console.warn('[AuthInterceptor] Получен 401 - попытка обновить токен');

        isRefreshing = true;

        return from(authService.refreshToken()).pipe(
          switchMap((refreshed: boolean) => {
            isRefreshing = false;

            if (refreshed) {
              console.log('[AuthInterceptor] Токен обновлен, повтор запроса');
              const newToken = localStorage.getItem('jwt_token');
              const retryReq = req.clone({
                setHeaders: {
                  'Authorization': `Bearer ${newToken}`,
                  'Content-Type': 'application/json'
                }
              });
              return next(retryReq);
            } else {
              console.warn('[AuthInterceptor] Не удалось обновить токен - выход');
              localStorage.removeItem('jwt_token');
              localStorage.removeItem('refresh_token');
              localStorage.removeItem('session_id');
              router.navigate(['/login'], {
                queryParams: { sessionExpired: 'true', reason: 'Сессия истекла' }
              });
              return throwError(() => error);
            }
          }),
          catchError((refreshError) => {
            isRefreshing = false;
            console.error('[AuthInterceptor] Ошибка обновления:', refreshError);
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('session_id');
            router.navigate(['/login'], {
              queryParams: { sessionExpired: 'true', reason: 'Сессия истекла' }
            });
            return throwError(() => error);
          })
        );
      }

      return throwError(() => error);
    })
  );
};




