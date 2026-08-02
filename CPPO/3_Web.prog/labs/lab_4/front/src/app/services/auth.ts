import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { AuthResponse, LoginRequest, RegisterRequest, SessionInfo } from '../models/types';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  login(credentials: LoginRequest, onActiveSessionsCallback?: (response: AuthResponse) => void) {
    console.log('[Auth] 🔐 login() вызван с credentials:', credentials.username);
    console.trace('[Auth] Stack trace для login()');

    const loginData: LoginRequest = {
      ...credentials,
      deviceName: credentials.deviceName || this.getDeviceName()
    };

    console.log('[Auth] Отправляем POST /api/auth/login');
    const observable = this.http.post<AuthResponse>('/api/auth/login', loginData);

    observable.subscribe({
      next: (res) => {
        console.log('[Auth] Получен ответ от POST /api/auth/login:', {
          success: res.success,
          sessionId: res.sessionId,
          hasActiveSessions: res.hasActiveSessions,
          activeSessions: res.activeSessions?.length || 0
        });

        if (res.success) {
          if (res.token && res.refreshToken) {
            this.saveTokens(res.token, res.refreshToken, res.sessionId);
            console.log('[Auth] Токены сохранены');
          }

          if (onActiveSessionsCallback) {
            console.log('[Auth] Вызываем callback с ответом');
            onActiveSessionsCallback(res);
          } else {
            console.log('[Auth] Нет callback, переходим на /main');
            this.router.navigate(['/main']);
          }
        } else {
          alert('Ошибка входа: ' + res.message);
        }
      },
      error: (err) => {
        console.error('[Auth] Ошибка при POST /api/auth/login:', err);
        const errorMessage = err.error?.message || 'Неверные учетные данные';
        alert('Ошибка входа: ' + errorMessage);
      },
    });

    return observable;
  }


  register(credentials: RegisterRequest) {
    const registerData: RegisterRequest = {
      username: credentials.username,
      email: credentials.email || credentials.username,
      password: credentials.password,
      deviceName: credentials.deviceName || this.getDeviceName()
    };

    this.http.post<AuthResponse>('/api/auth/register', registerData).subscribe({
      next: (res) => {
        if (res.success && res.token && res.refreshToken) {
          this.saveTokens(res.token, res.refreshToken, res.sessionId);
          this.router.navigate(['/main']);
        } else {
          alert('Ошибка регистрации: ' + res.message);
        }
      },
      error: (err) => {
        const errorMessage = err.error?.message || 'Имя пользователя уже занято';
        alert('Ошибка регистрации: ' + errorMessage);
      },
    });
  }

  logout() {
    const token = localStorage.getItem('jwt_token');
    console.log('[Auth] Выход, токен существует:', !!token);

    if (token) {
      fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        keepalive: true
      }).then(() => {
        console.log('[Auth] Сессия закрыта на сервере');
      }).catch((err) => {
        console.warn('[Auth] Ошибка запроса выхода:', err);
      }).finally(() => {
        this.clearTokens();
      });
    } else {
      this.clearTokens();
    }
  }

  refreshToken(): Promise<boolean> {
    return new Promise((resolve) => {
      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        console.warn('[Auth] Нет refresh токена');
        resolve(false);
        return;
      }

      this.http.post<AuthResponse>('/api/auth/refresh', { refreshToken }).subscribe({
        next: (res) => {
          if (res.success && res.token) {
            console.log('🔄 [Auth] Access токен обновлен');
            localStorage.setItem('jwt_token', res.token);
            this.showRefreshNotification();
            resolve(true);
          } else {
            console.error('[Auth] Не удалось обновить токен');
            resolve(false);
          }
        },
        error: (err) => {
          console.error('[Auth] Refresh токен истек:', err);
          this.logout();
          resolve(false);
        }
      });
    });
  }


  closeSession(sessionId: number): Observable<AuthResponse> {
    return this.http.delete<AuthResponse>(`/api/auth/sessions/${sessionId}`).pipe(
      switchMap((response) => {
        if (response.isCurrentSession) {
          console.warn('[Auth] Текущая сессия закрыта');
          this.clearTokens();
          alert(response.message || 'Ваша сессия была закрыта');
          setTimeout(() => this.router.navigate(['/login']), 100);
        }
        return of(response);
      })
    );
  }

  closeOtherSessions(): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/sessions/close-others', {});
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('jwt_token');
  }


  private saveTokens(accessToken: string, refreshToken: string, sessionId?: number) {
    localStorage.setItem('jwt_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    if (sessionId) {
      localStorage.setItem('session_id', sessionId.toString());
    }
    console.log('[Auth] Токены сохранены');
  }

  clearTokens() {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('session_id');
    console.log('[Auth] Токены очищены');
    this.router.navigate(['/login']);
  }

  private showRefreshNotification() {
    const notification = document.createElement('div');
    notification.innerHTML = `
      <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
      ">
        <div style="display: flex; align-items: center; gap: 12px;">
          <div>
            <div style="font-weight: 600; margin-bottom: 4px;">Токен обновлен</div>
            <div style="font-size: 13px; opacity: 0.9;">Ваша сессия продолжается</div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-in';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  private getDeviceName(): string {
    const ua = navigator.userAgent;

    if (ua.includes('Windows NT 10.0')) return 'Windows 10 PC';
    if (ua.includes('Windows NT')) return 'Windows PC';
    if (ua.includes('Mac OS X')) {
      if (ua.includes('iPhone')) return 'iPhone';
      if (ua.includes('iPad')) return 'iPad';
      return 'Mac';
    }
    if (ua.includes('Android')) return 'Android Device';
    if (ua.includes('Linux')) return 'Linux PC';

    if (ua.includes('Chrome')) return 'Chrome Browser';
    if (ua.includes('Firefox')) return 'Firefox Browser';
    if (ua.includes('Safari')) return 'Safari Browser';
    if (ua.includes('Edge')) return 'Edge Browser';

    return 'Web Browser';
  }
}

