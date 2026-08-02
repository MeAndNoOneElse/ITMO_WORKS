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

class RValidatorTest {

    private RValidator validator;
    private FacesContext context;
    private UIComponent component;

    @BeforeEach
    void setUp() {
        validator = new RValidator();
        context = mock(FacesContext.class);
        component = mock(UIComponent.class);
    }

    @Test
    @DisplayName("R=null throws ValidatorException")
    void testNullValue() {
        ValidatorException ex = assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, null));
        assertTrue(ex.getMessage().contains("R"));
    }

    @ParameterizedTest
    @ValueSource(doubles = {2.0, 3.0, 3.5, 5.0})
    @DisplayName("Valid R values: 2 to 5")
    void testValidValues(double r) {
        assertDoesNotThrow(() -> validator.validate(context, component, r));
    }

    @ParameterizedTest
    @ValueSource(doubles = {1.9, 0.0, -1.0, 5.1, 10.0})
    @DisplayName("Invalid R values: outside 2..5")
    void testInvalidValues(double r) {
        ValidatorException ex = assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, r));
        assertTrue(ex.getMessage().contains("R"));
    }

    @Test
    @DisplayName("Invalid type (String) throws ValidatorException")
    void testInvalidType() {
        assertThrows(ValidatorException.class,
                () -> validator.validate(context, component, "not a number"));
    }
}
