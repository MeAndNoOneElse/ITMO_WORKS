package org.example;

import java.math.BigDecimal;
import java.math.MathContext;
import java.util.HashMap;
import java.util.Map;

public class JsonParser implements RequestParser {
    private static final MathContext MC = new MathContext(100);
    private String originalYString = null;

    public static class ValidatedValues {
        private final BigDecimal x;
        private final BigDecimal y;
        private final BigDecimal r;
        private final String originalY;

        public ValidatedValues(BigDecimal x, BigDecimal y, BigDecimal r, String originalY) {
            this.x = x;
            this.y = y;
            this.r = r;
            this.originalY = originalY;
        }

        public BigDecimal getX() {
            return x;
        }

        public BigDecimal getY() {
            return y;
        }

        public BigDecimal getR() {
            return r;
        }


        @Override
        public String toString() {
            return "ValidatedValues{" +
                    "x=" + x +
                    ", y=" + y +
                    ", r=" + r +
                    ", originalY='" + originalY + '\'' +
                    '}';
        }
    }

    @Override
    public BigDecimal[] getBigDecimals(String requestString) throws IllegalArgumentException {
        ValidatedValues validatedValues = validateAndParse(requestString);
        return new BigDecimal[] { validatedValues.getX(), validatedValues.getY(), validatedValues.getR() };
    }
    public ValidatedValues validateAndParse(String requestString) throws IllegalArgumentException {
        try {
            requestString = requestString.replaceAll("[{}\"]", "");
            String[] parts = requestString.split(",");

            if (parts.length < 3) {
                throw new IllegalArgumentException("JSON must contain exactly 3 parameters: x, y, r");
            }

            Map<String, String> params = new HashMap<>();

            for (String part : parts) {
                String[] keyValue = part.split(":");
                if (keyValue.length == 2) {
                    String key = keyValue[0].trim().toLowerCase();
                    String value = keyValue[1].trim().replace(",", ".");
                    params.put(key, value);
                }
            }

            if (!params.containsKey("x") || !params.containsKey("y") || !params.containsKey("r")) {
                throw new IllegalArgumentException("JSON must contain all three parameters: x, y, r");
            }

            String xStr = params.get("x");
            String yStr = params.get("y");
            String rStr = params.get("r");

            this.originalYString = yStr;

            // Валидация Y
            if (!yStr.matches("^-?\\d*\\.?\\d+$")) {
                throw new IllegalArgumentException("Y must be a valid decimal number");
            }
            if (yStr.length() > 100) {
                throw new IllegalArgumentException("The Y value is too long (maximum 100 characters)");
            }

            validateValue(xStr, "X");
            validateValue(yStr, "Y");
            validateValue(rStr, "R");

            BigDecimal x = new BigDecimal(xStr, MC);
            BigDecimal y = new BigDecimal(yStr, MC);
            BigDecimal r = new BigDecimal(rStr, MC);

            return new ValidatedValues(x, y, r, yStr);

        } catch (Exception e) {
            throw new IllegalArgumentException("Invalid JSON format: " + e.getMessage());
        }
    }

    private void validateValue(String valueStr, String paramName) throws IllegalArgumentException {
        if (valueStr == null || valueStr.trim().isEmpty()) {
            throw new IllegalArgumentException(paramName + " cannot be null or empty");
        }

        try {
            new BigDecimal(valueStr, MC);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(paramName + " must be a valid decimal number: " + valueStr);
        }

        if (valueStr.length() > 100) {
            throw new IllegalArgumentException(paramName + " value is too long (maximum 100 characters)");
        }
    }

    @Override
    public String getOriginalYString() {
        return originalYString;
    }
}
