import { Component, OnInit, inject, ChangeDetectorRef, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { PointService } from '../../services/point';
import { AuthService } from '../../services/auth';
import { SessionMonitorService } from '../../services/session-monitor';
import { Point } from '../../models/types';

@Component({
  selector: 'app-main',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './main.html',
  styleUrl: './main.css'
})
export class Main implements OnInit, OnDestroy {
  private pointService = inject(PointService);
  private authService = inject(AuthService);
  private sessionMonitor = inject(SessionMonitorService);
  private cdr = inject(ChangeDetectorRef);
  private router = inject(Router);

  x: number | null = null;
  y: string = '';
  r: number | null = null;

  xOptions: number[] = [-3, -2, -1, 0, 1, 2, 3, 4, 5];
  rOptions: number[] = [-3, -2, -1, 0, 1, 2, 3, 4, 5];

  allPoints: Point[] = [];
  scale: number = 25;

  viewMode: 'auto' | 'desktop' | 'tablet' | 'mobile' = 'auto';
  currentMode: 'desktop' | 'tablet' | 'mobile' = 'desktop';

  theme: 'light' | 'dark' = 'light';

  graphSize: number = 300;

  get numR(): number {
    return this.r ?? 0;
  }

  get points(): Point[] {
    return this.allPoints;
  }

  ngOnInit() {
    const token = localStorage.getItem('jwt_token');
    console.log('[MainComponent] Токен при загрузке:', token ? `${token.substring(0, 20)}...` : 'ОТСУТСТВУЕТ');

    if (!token) {
      console.error('[MainComponent] ОШИБКА: Токен отсутствует! Перенаправление на login.');
      this.router.navigate(['/login']);
      return;
    }

    console.log('[MainComponent] Запуск мониторинга сессии...');
    this.sessionMonitor.startMonitoring();

    this.loadSavedRadius(token);

    this.loadPoints();
    this.updateViewMode();
    this.updateGraphSize();

    if (typeof window !== 'undefined') {
      window.addEventListener('resize', () => {
        this.updateViewMode();
        this.updateGraphSize();
        this.cdr.detectChanges();
      });

      const savedTheme = localStorage.getItem('theme') as 'light' | 'dark';
      if (savedTheme) {
        this.theme = savedTheme;
        this.applyTheme();
      }
    }
  }

  loadPoints() {
    console.log('[MainComponent] Загрузка точек...');
    const token = localStorage.getItem('jwt_token');
    console.log('[MainComponent] Токен перед загрузкой:', token ? `${token.substring(0, 20)}...` : 'ОТСУТСТВУЕТ');

    this.pointService.getPoints().subscribe({
      next: (data) => {
        console.log('[MainComponent] Точки загружены:', data.length);
        this.allPoints = [...data];
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('[MainComponent] Ошибка загрузки точек:', err);

        // Если 401 - показываем уведомление
        if (err.status === 401) {
          console.error('[MainComponent] 401 при загрузке точек - токен недействителен!');
        }
      }
    });
  }

  isHitClient(x: number, y: number, r: number): boolean {
    if (r <= 0) return false;

    if (x >= 0 && y >= 0) {
      return x <= r / 2 && y <= r;
    }

    if (x <= 0 && y >= 0) {
      return (x * x + y * y) <= (r * r);
    }

    if (x <= 0 && y <= 0) {
      return false;
    }

    if (x >= 0 && y <= 0) {
      return y >= 2 * x - r;
    }

    return false;
  }

  onYInput(event: Event) {
    const input = event.target as HTMLInputElement;
    let value = input.value;

    value = value.replace(/[^0-9.\-]/g, '');

    if (value.indexOf('-') > 0) {
      value = value.replace(/-/g, '');
    }
    const minusCount = (value.match(/-/g) || []).length;
    if (minusCount > 1) {
      value = '-' + value.replace(/-/g, '');
    }

    const dotCount = (value.match(/\./g) || []).length;
    if (dotCount > 1) {
      const firstDotIndex = value.indexOf('.');
      value = value.substring(0, firstDotIndex + 1) + value.substring(firstDotIndex + 1).replace(/\./g, '');
    }

    this.y = value;
    input.value = value;
  }

  onSend() {
    if (this.x === null) {
      alert('Выберите координату X!');
      return;
    }

    const yNum = parseFloat(this.y);
    if (isNaN(yNum) || yNum < -3 || yNum > 3) {
      alert('Координата Y должна быть числом в диапазоне от -3 до 3!');
      return;
    }

    if (this.r === null) {
      alert('Выберите радиус R!');
      return;
    }

    if (this.r <= 0) {
      alert('Радиус R должен быть больше 0!');
      return;
    }

    this.sendPoint(this.x, yNum, this.r);
  }

  sendPoint(x: number, y: number, r: number) {
    this.pointService.addPoint({ x, y, r }).subscribe({
      next: () => {
        this.loadPoints();
        this.cdr.detectChanges();
      },
      error: (err) => console.error(err)
    });
  }

  onSvgClick(event: MouseEvent) {
    if (this.r === null) {
      alert('Выберите радиус R!');
      return;
    }

    if (this.r <= 0) {
      alert('Радиус R должен быть больше 0!');
      return;
    }

    const svg = event.currentTarget as SVGSVGElement;
    const rect = svg.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;
    const mathX = (mouseX - this.graphCenter) / this.scale;
    const mathY = (this.graphCenter - mouseY) / this.scale;

    if (mathX < -3 || mathX > 5 || mathY < -3 || mathY > 3) {
      alert('Клик вне допустимого диапазона!\nX: [-3, 5], Y: [-3, 3]');
      return;
    }

    this.sendPoint(Number(mathX.toFixed(3)), Number(mathY.toFixed(3)), this.r);
  }

  abs(val: number): number {
    return Math.abs(val);
  }

  clearResults() {
    if (confirm('Вы уверены, что хотите удалить все результаты?')) {
      this.allPoints = [];
      this.cdr.detectChanges();

      this.pointService.clearPoints().subscribe({
        next: () => {
          this.loadPoints();
        },
        error: (err) => {
          console.error('Ошибка при очистке:', err);
          this.loadPoints();
        }
      });
    }
  }

  logout() {
    console.log('[MainComponent] Logout button clicked');
    this.authService.logout();
  }

  toggleTheme() {
    this.theme = this.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', this.theme);
    this.applyTheme();
  }

  applyTheme() {
    if (typeof document !== 'undefined') {
      document.body.className = this.theme === 'dark' ? 'dark-theme' : 'light-theme';
    }
  }

  toggleViewMode() {
    if (this.viewMode === 'auto') {
      this.viewMode = this.currentMode;
    } else if (this.viewMode === 'desktop') {
      this.viewMode = 'tablet';
      this.currentMode = 'tablet';
      this.updateGraphSize();
    } else if (this.viewMode === 'tablet') {
      this.viewMode = 'mobile';
      this.currentMode = 'mobile';
      this.updateGraphSize();
    } else {
      this.viewMode = 'auto';
      this.updateViewMode();
      this.updateGraphSize();
    }
    this.cdr.detectChanges();
  }

  updateViewMode() {
    if (this.viewMode === 'auto' && typeof window !== 'undefined') {
      const width = window.innerWidth;
      if (width >= 1164) {
        this.currentMode = 'desktop';
      } else if (width >= 710) {
        this.currentMode = 'tablet';
      } else {
        this.currentMode = 'mobile';
      }
    }
  }

  updateGraphSize() {
    if (typeof window !== 'undefined') {
      const width = window.innerWidth;
      let maxSize = 300; // по умолчанию

      if (this.currentMode === 'desktop') {
        // Для десктопа: график занимает правую половину, минус отступы
        const desktopSize = Math.floor((width / 2) - 80);
        maxSize = Math.min(desktopSize, 600); // максимум 600px
      } else if (this.currentMode === 'tablet') {
        // Для планшета: график занимает 2/3, минус отступы
        const tabletSize = Math.floor((width * 2 / 3) - 60);
        maxSize = Math.min(tabletSize, 500); // максимум 500px
      } else {
        // Для мобильного: график занимает почти всю ширину
        const mobileSize = Math.floor(width - 50);
        maxSize = Math.min(mobileSize, 400); // максимум 400px
      }

      // Устанавливаем размер (минимум 250px)
      this.graphSize = Math.max(maxSize, 250);

      // Обновляем масштаб для точек
      this.scale = this.graphSize / 12;
    }
  }

  get graphCenter(): number {
    return this.graphSize / 2;
  }

  get viewModeLabel(): string {
    if (this.viewMode === 'auto') return 'Авто';
    return this.viewMode === 'desktop' ? 'ПК' : this.viewMode === 'tablet' ? 'Планшет' : 'Мобильный';
  }

  private loadSavedRadius(token: string) {
    const storageKey = `session_radius_${token}`;
    const savedRadius = localStorage.getItem(storageKey);

    if (savedRadius !== null) {
      const radiusValue = parseFloat(savedRadius);

      // Проверяем, что значение валидно и есть в списке опций
      if (!isNaN(radiusValue) && this.rOptions.includes(radiusValue)) {
        this.r = radiusValue;
        console.log(`Загружен сохраненный радиус для сессии: R = ${radiusValue}`);
      } else {
        console.warn(` Сохраненный радиус (${savedRadius}) невалиден, устанавливаем по умолчанию R = 3`);
        this.r = 3;
        this.saveCurrentRadius(); // Сохраняем значение по умолчанию
      }
    } else {
      console.log(' Сохраненный радиус для этой сессии не найден, устанавливаем по умолчанию R = 3');
      this.r = 3;
      this.saveCurrentRadius(); // Сохраняем значение по умолчанию
    }
  }


  private saveCurrentRadius() {
    const token = localStorage.getItem('jwt_token');

    if (token && this.r !== null) {
      const storageKey = `session_radius_${token}`;
      localStorage.setItem(storageKey, this.r.toString());
      console.log(` Сохранен радиус для сессии: R = ${this.r}`);
    }
  }

  onRadiusChange() {
    this.saveCurrentRadius();
  }

  ngOnDestroy() {
    // Останавливаем мониторинг сессии
    console.log('[MainComponent] Остановка мониторинга сессии...');
    this.sessionMonitor.stopMonitoring();

    // Компонент уничтожается
    console.log('[MainComponent] Component destroyed');
  }
}
