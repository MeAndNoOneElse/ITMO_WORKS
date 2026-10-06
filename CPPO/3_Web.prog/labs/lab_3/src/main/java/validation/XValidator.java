package validation;
import jakarta.faces.application.FacesMessage;
import jakarta.faces.component.UIComponent;
import jakarta.faces.context.FacesContext;
import jakarta.faces.validator.FacesValidator;
import jakarta.faces.validator.Validator;
import jakarta.faces.validator.ValidatorException;

import java.math.BigDecimal;

@FacesValidator("XValidator")
public class XValidator implements Validator {
    @Override
    public void validate(FacesContext context, UIComponent component, Object value) throws ValidatorException {
        if (value == null) {
            throw new ValidatorException(new FacesMessage("Ошибка: X обязательно для ввода!"));
        }
        try {
            Double doubleValue = (Double) value;
            BigDecimal x = BigDecimal.valueOf(doubleValue);

            BigDecimal min = BigDecimal.valueOf(-5);
            BigDecimal max = BigDecimal.valueOf(5);

            if (x.compareTo(min) < 0 || x.compareTo(max) > 0) {
                throw new ValidatorException(new FacesMessage("Ошибка: X должно быть от -5 до 5!"));
            }
        } catch (ClassCastException e) {
            throw new ValidatorException(new FacesMessage("Ошибка: Некорректный тип данных для X!"));
        }
    }
}

