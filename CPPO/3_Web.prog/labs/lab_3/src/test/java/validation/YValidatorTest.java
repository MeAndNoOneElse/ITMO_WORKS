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

class YValidatorTest {

    private YValidator validator;
    private FacesContext context;
    private UIComponent component;

    @BeforeEach
    void setUp() {
        validator = new YValidator();
        context = mock(FacesContext.class);
        component = mock(UIComponent.class);
    }

    @Test
    @DisplayName("Y=null throws ValidatorException")
    void testNullValue() {
        ValidatorException ex = assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, null));
        assertTrue(ex.getMessage().contains("Y"));
    }

    @Test
    @DisplayName("Y=empty string throws ValidatorException")
    void testEmptyValue() {
        assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, ""));
    }

    @ParameterizedTest
    @ValueSource(doubles = {-3.0, -1.5, 0.0, 1.5, 3.0})
    @DisplayName("Valid Y values: -3 to 3")
    void testValidValues(double y) {
        assertDoesNotThrow(() -> validator.validate(context, component, y));
    }

    @ParameterizedTest
    @ValueSource(doubles = {-3.1, -10.0, 3.1, 100.0})
    @DisplayName("Invalid Y values: outside -3..3")
    void testInvalidValues(double y) {
        ValidatorException ex = assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, y));
        assertTrue(ex.getMessage().contains("Y"));
    }

    @Test
    @DisplayName("Y=NaN throws ValidatorException")
    void testNaN() {
        assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, Double.NaN));
    }

    @Test
    @DisplayName("Y=Infinity throws ValidatorException")
    void testInfinity() {
        assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, Double.POSITIVE_INFINITY));
    }

    @Test
    @DisplayName("Y string too long (>7 chars)")
    void testTooLongString() {
        assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, "12345678"));
    }

    @Test
    @DisplayName("Y not a number (string)")
    void testNotANumber() {
        assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, "abc"));
    }
}
