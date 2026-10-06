package org.example;

import java.math.BigDecimal;

public class HitChecker implements PointValidator {
    @Override
    public void validate(BigDecimal x, BigDecimal y, BigDecimal r) {
    // Пустая реализация, так как валидация выполняется в Validator
    throw new UnsupportedOperationException("Verification is not supported by HitChecker");
    }

    @Override
    public boolean isHit(BigDecimal x, BigDecimal y, BigDecimal r) {
    return (checkTriangle1(x, y, r) || checkCircle(x, y, r) || checkRectangle4(x, y, r));
    }

    private boolean checkTriangle1(BigDecimal x, BigDecimal y, BigDecimal r) {
        if (x.compareTo(BigDecimal.ZERO) < 0 || y.compareTo(BigDecimal.ZERO) < 0) {
            return false;
        }

        BigDecimal halfR = r.divide(new BigDecimal("2"));
        BigDecimal lineY = r.subtract(x).divide(new BigDecimal("2"));

        return (x.compareTo(r) <= 0 &&
                y.compareTo(halfR) <= 0 &&
                y.compareTo(lineY) <= 0);
    }
    private boolean checkCircle(BigDecimal x, BigDecimal y, BigDecimal r) {
        if (x.compareTo(BigDecimal.ZERO) > 0 || y.compareTo(BigDecimal.ZERO) > 0) {
            return false;
        }
        BigDecimal halfR = r.divide(new BigDecimal("2"));
        BigDecimal radiusSquared = halfR.multiply(halfR);
        BigDecimal distanceSquared = x.multiply(x).add(y.multiply(y));

        return distanceSquared.compareTo(radiusSquared) <= 0;
    }
    private boolean checkRectangle4(BigDecimal x, BigDecimal y, BigDecimal r) {
        BigDecimal halfR = r.divide(new BigDecimal("2"));
        return (x.compareTo(BigDecimal.ZERO) >= 0 &&
                x.compareTo(halfR) <= 0 &&
                y.compareTo(r.negate()) >= 0 &&
                y.compareTo(BigDecimal.ZERO) <= 0);
    }
}