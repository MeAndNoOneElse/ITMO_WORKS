import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { interval, Subscription } from 'rxjs';
import { AuthService } from './auth';

@Injectable({
  providedIn: 'root',
})
export class SessionMonitorService {
  private router = inject(Router);
  private authService = inject(AuthService);

  private checkInterval = 60000; // 1 минута
  private checkSubscription?: Subscription;

  startMonitoring() {
    this.stopMonitoring();

    console.log('[SessionMonitor] Запуск мониторинга (проверка каждую минуту)');
    console.log('[SessionMonitor] Первая проверка будет через 60 секунд');
    this.checkSubscription = interval(this.checkInterval).subscribe(() => {
      this.checkToken();
    });
  }

  stopMonitoring() {
    if (this.checkSubscription) {
      this.checkSubscription.unsubscribe();
      this.checkSubscription = undefined;
      console.log('[SessionMonitor] Мониторинг остановлен');
    }
  }

  private async checkToken() {
    const accessToken = localStorage.getItem('jwt_token');
    const refreshToken = localStorage.getItem('refresh_token');

    if (!accessToken || !refreshToken) {
      return;
    }

    try {
      const tokenData = this.decodeJwt(accessToken);
      if (!tokenData?.exp) {
        console.error('[SessionMonitor] Неверный формат токена');
        return;
      }

      const now = Math.floor(Date.now() / 1000);
      const timeUntilExpiry = tokenData.exp - now;

      console.log(`[SessionMonitor] Токен истекает через ${timeUntilExpiry} сек`);


      const sessionValid = await this.checkSessionStatus();

      if (!sessionValid) {
        console.warn('[SessionMonitor] Сессия закрыта на сервере');
        this.handleSessionExpired('Сессия была закрыта на другом устройстве');
        return;
      }

      if (timeUntilExpiry <= 15) {
        console.log('[SessionMonitor] Токен скоро истечет, обновляем...');
        this.refreshToken();
      }
    } catch (error) {
      console.error('[SessionMonitor] Ошибка проверки токена:', error);
    }
  }

  private async checkSessionStatus(): Promise<boolean> {
    try {
      const token = localStorage.getItem('jwt_token');
      const response = await fetch('/api/auth/check-session', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.status === 401) {
        console.warn('[SessionMonitor] Сервер вернул 401 - сессия недействительна');
        return false;
      }

      return true;
    } catch (error) {
      console.error('[SessionMonitor] Ошибка проверки статуса сессии:', error);
      return true;
    }
  }

  private async refreshToken() {
    try {
      const success = await this.authService.refreshToken();

      if (success) {
        console.log('[SessionMonitor]  Токен обновлен');
        this.showNotification('Сессия продлена', 'success');
      } else {
        console.error('[SessionMonitor]  Не удалось обновить токен');
        this.handleSessionExpired('Сессия истекла');
      }
    } catch (error) {
      console.error('[SessionMonitor] Ошибка обновления токена:', error);
      this.handleSessionExpired('Сессия была закрыта на другом устройстве');
    }
  }

  private handleSessionExpired(reason: string) {
    console.log('[SessionMonitor] Сессия истекла:', reason);

    localStorage.removeItem('jwt_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('session_id');

    this.stopMonitoring();

    this.showNotification(reason, 'error');

    setTimeout(() => {
      this.router.navigate(['/login'], {
        queryParams: { sessionExpired: 'true', reason: reason }
      });
    }, 2000);
  }

  private showNotification(message: string, type: 'success' | 'error') {
    const notification = document.createElement('div');
    const bgColor = type === 'success' ? '#4CAF50' : '#f44336';

    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${bgColor};
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      z-index: 99999;
      font-family: Arial, sans-serif;
      font-size: 14px;
      animation: slideIn 0.3s ease-out;
    `;
    notification.innerHTML = `
      <strong>${type === 'success' ? '✓' : '⚠'} ${message}</strong>
    `;

    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    `;
    document.head.appendChild(style);

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideIn 0.3s ease-out reverse';
      setTimeout(() => {
        notification.remove();
        style.remove();
      }, 300);
    }, 3000);
  }

  private decodeJwt(token: string): any {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;

      const payload = parts[1];
      const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
      return JSON.parse(decoded);
    } catch (error) {
      return null;
    }
  }
}


