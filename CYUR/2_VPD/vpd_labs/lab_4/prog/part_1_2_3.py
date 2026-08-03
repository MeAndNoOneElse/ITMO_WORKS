#!/usr/bin/env python3

import math
import time
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B


class Integral:

    def __init__(self, dt, x0=0.0):
        self.dt = dt
        self.integral = x0
        self.prev_val = None

    def update(self, val):
        if self.prev_val is not None:
            self.integral += (self.prev_val + val) / 2.0 * self.dt
        self.prev_val = val
        return self.integral

    def reset(self, x0=0.0):
        self.integral = x0
        self.prev_val = None


class Odometry:

    def __init__(self, r, B, dt, x0=0.0, y0=0.0, theta0=0.0):
        self.r = r
        self.B = B
        self.dt = dt
        self.int_x = Integral(dt, x0)
        self.int_y = Integral(dt, y0)
        self.int_theta = Integral(dt, theta0)

    def update(self, omega_r, omega_l):
        v = (omega_r + omega_l) * self.r / 2.0
        omega = (omega_r - omega_l) * self.r / self.B
        x_dot = v * math.cos(self.int_theta.integral)
        y_dot = v * math.sin(self.int_theta.integral)
        x = self.int_x.update(x_dot)
        y = self.int_y.update(y_dot)
        theta = self.int_theta.update(omega)
        theta = math.atan2(math.sin(theta), math.cos(theta))
        return [x, y, theta]

    def reset(self, x0=0.0, y0=0.0, theta0=0.0):
        self.int_x.reset(x0)
        self.int_y.reset(y0)
        self.int_theta.reset(theta0)


class Upravlenie:

    @staticmethod
    def control_robot(x, y, theta, x_g, y_g, Kl, Kr):
        e_x = x_g - x
        e_y = y_g - y
        rho = math.sqrt(e_x ** 2 + e_y ** 2)
        psi = math.atan2(e_y, e_x)
        alpha = psi - theta

        while alpha > math.pi:
            alpha -= 2 * math.pi
        while alpha <= -math.pi:
            alpha += 2 * math.pi

        u_right = Kl * rho + Kr * alpha
        u_left = Kl * rho - Kr * alpha

        return [u_right, u_left, rho, alpha]


POINTS = [
    (1, 0),
    (1, 1),
    (-1, 1),
    (0, 0)
]

# Инициализация моторов
left_motor = LargeMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_B)

# Сброс энкодеров
left_motor.reset()
right_motor.reset()

# Включение режима прямого управления (один раз!)
left_motor.run_direct()
right_motor.run_direct()

# Начальные позиции энкодеров
prev_left = left_motor.position
prev_right = right_motor.position

# Параметры робота
r = 0.029
B = 0.120
dt = 0.01
T = 0.03

# Коэффициенты регулятора
Kl = 150
Kr = 400

# Одометрия
odom = Odometry(r, B, dt)

with open("data_fifth.txt", "w") as f:
    for point in POINTS:

        gx = point[0]
        gy = point[1]

        print("Going to point: ({}, {})".format(gx, gy))

        while True:
            t1 = time.time()

            # Чтение энкодеров
            current_left = left_motor.position
            current_right = right_motor.position

            dpsi_l = math.radians(current_left - prev_left)
            dpsi_r = math.radians(current_right - prev_right)

            prev_left = current_left
            prev_right = current_right

            omega_l = dpsi_l / T if T > 0 else 0
            omega_r = dpsi_r / T if T > 0 else 0

            x, y, theta = odom.update(omega_r, omega_l)

            control = Upravlenie.control_robot(x, y, theta, gx, gy, Kl, Kr)

            u_right = control[0]
            u_left = control[1]
            rho = control[2]

            print("x={:.3f}, y={:.3f}, rho={:.3f}, u_l={:.1f}, u_r={:.1f}".format(x, y, rho, u_left, u_right))

            # Достигли цели?
            if rho < 0.01:
                left_motor.stop()
                right_motor.stop()
                print("Point reached! Stop motors.\n")
                time.sleep(5)
                # Перезапускаем режим direct для следующей точки
                left_motor.run_direct()
                right_motor.run_direct()
                break

            # Ограничение мощности (проценты -100..100)
            u_left = max(-100, min(100, u_left))
            u_right = max(-100, min(100, u_right))

            # Меняем мощность моторов (без повторного вызова run_direct)
            left_motor.duty_cycle_sp = int(u_left)
            right_motor.duty_cycle_sp = int(u_right)

            # Запись в файл
            t2 = time.time()
            f.write("{} {} {} {}\n".format(t2, theta, x, y))

            sleep_time = T - (t2 - t1)
            if sleep_time > 0:
                time.sleep(sleep_time)

# Остановка моторов в конце
left_motor.stop()
right_motor.stop()
print("Program finished")