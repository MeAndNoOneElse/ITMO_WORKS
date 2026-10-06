package validation;



import jakarta.faces.application.FacesMessage;
import jakarta.faces.component.UIComponent;
import jakarta.faces.context.FacesContext;
import jakarta.faces.validator.FacesValidator;
import jakarta.faces.validator.Validator;
import jakarta.faces.validator.ValidatorException;

import java.math.BigDecimal;
@FacesValidator("RValidator")
public class RValidator implements Validator {
    @Override
    public void validate(FacesContext context, UIComponent component, Object value) throws ValidatorException {
        if (value == null) {
            throw new ValidatorException(new FacesMessage("Ошибка: R обязательно для ввода!"));
        }
        try {
            Double doubleValue = (Double) value;
            BigDecimal x = BigDecimal.valueOf(doubleValue);

            BigDecimal min = BigDecimal.valueOf(2);
            BigDecimal max = BigDecimal.valueOf(5);

            if (x.compareTo(min) < 0 || x.compareTo(max) > 0) {
                throw new ValidatorException(new FacesMessage("Ошибка: R должно быть от 2 до 5!"));
            }
        } catch (ClassCastException e) {
            throw new ValidatorException(new FacesMessage("Ошибка: Некорректный тип данных для R!"));
        }
    }
}


