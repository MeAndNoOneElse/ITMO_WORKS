package validation;

import jakarta.faces.application.FacesMessage;
import jakarta.faces.component.UIComponent;
import jakarta.faces.context.FacesContext;
import jakarta.faces.validator.FacesValidator;
import jakarta.faces.validator.Validator;
import jakarta.faces.validator.ValidatorException;

import java.math.BigDecimal;

@FacesValidator("YValidator")
public class YValidator implements Validator {
    @Override
    public void validate(FacesContext context, UIComponent component, Object value) throws ValidatorException {
        if (value == null || String.valueOf(value).isEmpty()) {
            throw new ValidatorException(new FacesMessage("Ошибка: Y обязательно для ввода!"));
        }
        String stringValue = String.valueOf(value);
        if (stringValue.length() > 7) {
            throw new ValidatorException(new FacesMessage("Ошибка: Длина значения Y не должна превышать 7 символов!"));
        }


        if (value instanceof Double && (((Double) value).isNaN() || ((Double) value).isInfinite())) {
            throw new ValidatorException(new FacesMessage("Ошибка: Y не должно быть NaN или бесконечностью!"));
        }

        BigDecimal yValue;
        try {
            if (value instanceof String) {
                yValue = new BigDecimal((String) value);
            } else if (value instanceof Double) {
                yValue = BigDecimal.valueOf((Double) value);
            } else if (value instanceof BigDecimal) {
                yValue = (BigDecimal) value;
            } else {
                throw new ValidatorException(new FacesMessage("Ошибка: недопустимый тип для Y!"));
            }
        } catch (NumberFormatException | NullPointerException e) {
            throw new ValidatorException(new FacesMessage("Ошибка: Y должно быть числом!"));
        }

        BigDecimal min = BigDecimal.valueOf(-3);
        BigDecimal max = BigDecimal.valueOf(3);

        if (yValue.compareTo(min) < 0 || yValue.compareTo(max) > 0) {
            throw new ValidatorException(new FacesMessage("Ошибка: Y должно быть от -3 до 3 (включительно)!"));
        }
    }
}
