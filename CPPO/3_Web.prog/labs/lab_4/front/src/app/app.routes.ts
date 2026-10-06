import { Routes, Router } from '@angular/router';
import { LoginComponent } from './components/login/login';
import { RegisterComponent } from './components/register/register';
import { Main } from './components/main/main';
import { inject } from '@angular/core';
import { AuthService } from './services/auth';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  {
    path: 'main',
    component: Main,
    canActivate: [() => {
      const auth = inject(AuthService);
      const router = inject(Router);
      return auth.isLoggedIn() ? true : router.createUrlTree(['/login']);
    }]
  },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: '**', redirectTo: '/login' }
];
