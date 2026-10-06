import { Component, inject, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';
import { CommonModule } from '@angular/common';
import { AuthResponse, SessionInfo } from '../../models/types';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class LoginComponent implements OnInit {
  private authService = inject(AuthService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  credentials = {
    username: '',
    password: ''
  };

  sessionExpiredMessage: string | null = null;
  showSessionModal: boolean = false;
  activeSessions: SessionInfo[] = [];
  currentSessionId: number | null = null;
  isProcessing: boolean = false;

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      if (params['sessionExpired'] === 'true') {
        const reason = params['reason'] || 'Ваша сессия истекла';
        this.sessionExpiredMessage = reason;
        setTimeout(() => {
          this.sessionExpiredMessage = null;
        }, 10000);
      }
    });
  }

  onLogin() {
    if (!this.validate()) return;

    if (this.isProcessing) {
      console.warn('[LoginComponent] ️ Уже обрабатывается вход, игнорируем повторный клик');
      return;
    }

    this.isProcessing = true;
    console.log('[LoginComponent] Вход начат...');

    this.authService.login(this.credentials, (response: AuthResponse) => {
      console.log('[LoginComponent] Получен ответ:', response);

      this.currentSessionId = response.sessionId || null;

      if (response.activeSessions && response.activeSessions.length > 0) {
        console.log('[LoginComponent] Найдены другие активные сессии:', response.activeSessions.length);
        this.activeSessions = response.activeSessions;
        this.showSessionModal = true;
        this.isProcessing = false;
        setTimeout(() => {
          this.cdr.detectChanges();
          console.log('[LoginComponent] Модалка показана');
        }, 0);
      } else {
        console.log('[LoginComponent] Нет других сессий, переход на /main');
        this.router.navigate(['/main']).then(() => {
          setTimeout(() => this.isProcessing = false, 1000);
        });
      }
    });
  }

  // Закрыть одну конкретную сессию
  onCloseSession(sessionId: number) {
    if (this.isProcessing) {
      console.warn('[LoginComponent]  Уже обрабатывается запрос, игнорируем повторный клик');
      return;
    }

    this.isProcessing = true;
    console.log('[LoginComponent] Закрытие сессии:', sessionId);

    this.authService.closeSession(sessionId).subscribe({
      next: () => {
        console.log('[LoginComponent] Сессия закрыта:', sessionId);
        // Удаляем из списка
        this.activeSessions = this.activeSessions.filter(s => s.id !== sessionId);

        // Если список пуст - можно войти
        if (this.activeSessions.length === 0) {
          console.log('[LoginComponent] Все другие сессии закрыты, переход на /main');
          this.showSessionModal = false;
          this.router.navigate(['/main']).then(() => {
            setTimeout(() => this.isProcessing = false, 1000);
          });
        } else {
          this.isProcessing = false;
        }

        this.cdr.detectChanges();
      },
      error: (err: any) => {
        this.isProcessing = false;
        alert('Ошибка закрытия сессии: ' + (err.error?.message || 'Неизвестная ошибка'));
      }
    });
  }

  // Закрыть все другие сессии и войти
  onCloseAllAndLogin() {
    if (this.isProcessing) {
      console.warn('[LoginComponent]  Уже обрабатывается запрос, игнорируем повторный клик');
      return;
    }

    this.isProcessing = true;
    console.log('[LoginComponent] Закрытие всех других сессий');

    this.authService.closeOtherSessions().subscribe({
      next: () => {
        console.log('[LoginComponent] Все другие сессии закрыты, переход на /main');
        this.activeSessions = [];
        this.showSessionModal = false;
        this.router.navigate(['/main']).then(() => {
          setTimeout(() => this.isProcessing = false, 1000);
        });
      },
      error: (err: any) => {
        this.isProcessing = false;
        alert('Ошибка закрытия сессий: ' + (err.error?.message || 'Неизвестная ошибка'));
      }
    });
  }

  // Создать новую / Войти в созданную сессию
  onContinueWithNew() {
    if (this.isProcessing) {
      console.warn('[LoginComponent]  Уже обрабатывается запрос, игнорируем повторный клик');
      return;
    }

    this.isProcessing = true;
    console.log('[LoginComponent] Вход в уже созданную сессию');
    console.log('[LoginComponent] Текущий sessionId:', this.currentSessionId);
    console.log('[LoginComponent] Токены в localStorage:', {
      jwt_token: !!localStorage.getItem('jwt_token'),
      refresh_token: !!localStorage.getItem('refresh_token'),
      session_id: localStorage.getItem('session_id')
    });

    this.showSessionModal = false;

    console.log('[LoginComponent] Переход на /main');
    this.router.navigate(['/main']).then(() => {
      console.log('[LoginComponent]  Переход на /main завершен');
      // Сбрасываем флаг через небольшую задержку
      setTimeout(() => {
        this.isProcessing = false;
      }, 1000);
    });
  }

  // Назад - закрыть модалку и закрыть созданную сессию
  onCancel() {
    console.log('[LoginComponent] Отмена входа, закрытие созданной сессии:', this.currentSessionId);

    if (this.currentSessionId) {
      this.authService.closeSession(this.currentSessionId).subscribe({
        next: () => {
          console.log('[LoginComponent] Созданная сессия закрыта');
          this.authService.clearTokens();
          this.showSessionModal = false;
          this.currentSessionId = null;
          this.activeSessions = [];
        },
        error: (err: any) => {
          console.error('[LoginComponent] Ошибка закрытия сессии:', err);
          // Все равно закрываем модалку и чистим токены
          this.authService.clearTokens();
          this.showSessionModal = false;
          this.currentSessionId = null;
          this.activeSessions = [];
        }
      });
    } else {
      this.showSessionModal = false;
    }
  }

  validate(): boolean {
    if (!this.credentials.username || !this.credentials.password) {
      alert('Пожалуйста, введите имя пользователя и пароль');
      return false;
    }
    return true;
  }

  formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleString();
  }
}


