import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class RegisterComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  credentials = {
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  };

  errors = {
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  };

  onRegister() {
    this.clearErrors();

    if (!this.validate()) {
      return;
    }

    this.authService.register({
      username: this.credentials.username,
      email: this.credentials.email,
      password: this.credentials.password
    });
  }

  validate(): boolean {
    let isValid = true;

    if (!this.credentials.username || this.credentials.username.trim().length < 3) {
      this.errors.username = 'Имя пользователя должно быть не менее 3 символов';
      isValid = false;
    }

    if (!this.credentials.email || !this.isValidEmail(this.credentials.email)) {
      this.errors.email = 'Неверный адрес электронной почты';
      isValid = false;
    }

    if (!this.credentials.password || this.credentials.password.length < 6) {
      this.errors.password = 'Пароль должен быть не менее 6 символов';
      isValid = false;
    }

    if (this.credentials.password !== this.credentials.confirmPassword) {
      this.errors.confirmPassword = 'Пароли не совпадают';
      isValid = false;
    }

    return isValid;
  }

  isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  clearErrors() {
    this.errors = {
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    };
  }

  goToLogin() {
    this.router.navigate(['/login']);
  }
}

