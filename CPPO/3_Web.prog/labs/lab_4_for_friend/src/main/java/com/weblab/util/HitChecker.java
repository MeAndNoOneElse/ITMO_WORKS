package com.weblab.util;

/**
 * Логика попадания точки в область по варианту 48585.
 *
 * Области:
 *  - I  квадрант: пусто (не попадает)
 *  - II квадрант (x<=0, y>=0): y <= r/2  И  x >= -r
 *  - III квадрант (x<=0, y<=0): y >= -x - r/2
 *  - IV квадрант (x>=0, y<=0): x² + y² <= r²
 */
public class HitChecker {

    public static boolean isHit(double x, double y, double r) {
        if (r <= 0) return false;

        // I квадрант — пусто
        if (x >= 0 && y >= 0) {
            return false;
        }

        // II квадрант: x<=0, y>=0 — прямоугольник: y <= r/2 && x >= -r
        if (x <= 0 && y >= 0) {
            return y <= r / 2.0 && x >= -r;
        }

        // III квадрант: x<=0, y<=0 — треугольник: y >= -x - r/2
        if (x <= 0 && y <= 0) {
            return y >= -x - r / 2.0;
        }

        // IV квадрант: x>=0, y<=0 — четверть круга: x² + y² <= r²
        return x * x + y * y <= r * r;
    }
}
