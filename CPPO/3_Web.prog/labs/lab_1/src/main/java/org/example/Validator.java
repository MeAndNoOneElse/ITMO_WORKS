package org.example;

import java.math.BigDecimal;

public class Validator implements PointValidator {
  @Override
  public void validate(BigDecimal x, BigDecimal y, BigDecimal r) {
    if (x == null || y == null || r == null) {
      throw new IllegalArgumentException("X, Y, R can`t null");
    }



    if (x.compareTo(Config.X_MIN) < 0 || x.compareTo(Config.X_MAX) > 0) {
      throw new IllegalArgumentException("X must be in the range of [-4; 4]");
    }

    if (y.compareTo(Config.Y_MIN) <= 0) {
      throw new IllegalArgumentException("Y must be in the range of (-3; 5)");
    }

    if (y.compareTo(Config.Y_MAX) >= 0) {
      throw new IllegalArgumentException("Y must be in the range of (-3; 5)");
    }

    if (r.compareTo(Config.R_MIN) < 0 || r.compareTo(Config.R_MAX) > 0) {
      throw new IllegalArgumentException("R must be in the range of [1; 3]");
    }
  }

  @Override
  public boolean isHit(BigDecimal x, BigDecimal y, BigDecimal r) {
    throw new UnsupportedOperationException("Hit checking not supported by Validator");
  }
}