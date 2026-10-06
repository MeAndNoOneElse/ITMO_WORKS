package validation;

import jakarta.faces.component.UIComponent;
import jakarta.faces.context.FacesContext;
import jakarta.faces.validator.ValidatorException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;

class XValidatorTest {

    private XValidator validator;
    private FacesContext context;
    private UIComponent component;

    @BeforeEach
    void setUp() {
        validator = new XValidator();
        context = mock(FacesContext.class);
        component = mock(UIComponent.class);
    }

    @Test
    @DisplayName("X=null throws ValidatorException")
    void testNullValue() {
        ValidatorException ex = assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, null));
        assertTrue(ex.getMessage().contains("X"));
    }

    @ParameterizedTest
    @ValueSource(doubles = {-5.0, -2.5, 0.0, 2.5, 5.0})
    @DisplayName("Valid X values: -5 to 5")
    void testValidValues(double x) {
        assertDoesNotThrow(() -> validator.validate(context, component, x));
    }

    @ParameterizedTest
    @ValueSource(doubles = {-5.1, -10.0, 5.1, 100.0})
    @DisplayName("Invalid X values: outside -5..5")
    void testInvalidValues(double x) {
        ValidatorException ex = assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, x));
        assertTrue(ex.getMessage().contains("X"));
    }

    @Test
    @DisplayName("Invalid type (String) throws ValidatorException")
    void testInvalidType() {
        assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, "not a number"));
    }
}
