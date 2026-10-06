package service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.*;

class AreaCheckServiceTest {

    private AreaCheckService service;

    @BeforeEach
    void setUp() {
        service = new AreaCheckService();
    }

    private boolean invokeCheckHit(double x, String y, double r) throws Exception {
        Method method = AreaCheckService.class.getDeclaredMethod("checkHit", double.class, String.class, double.class);
        method.setAccessible(true);
        return (boolean) method.invoke(service, x, y, r);
    }

    @Test
    @DisplayName("Q1: inside rectangle")
    void testQ1Inside() throws Exception {
        assertTrue(invokeCheckHit(1.0, "1.0", 4.0));
    }

    @Test
    @DisplayName("Q1: outside by Y")
    void testQ1OutsideY() throws Exception {
        assertFalse(invokeCheckHit(1.0, "3.0", 4.0));
    }

    @Test
    @DisplayName("Q1: outside by X")
    void testQ1OutsideX() throws Exception {
        assertFalse(invokeCheckHit(5.0, "1.0", 4.0));
    }

    @Test
    @DisplayName("Q1: boundary")
    void testQ1Boundary() throws Exception {
        assertTrue(invokeCheckHit(4.0, "2.0", 4.0));
    }

    @Test
    @DisplayName("Q2: inside triangle")
    void testQ2Inside() throws Exception {
        assertTrue(invokeCheckHit(-1.0, "1.0", 4.0));
    }

    @Test
    @DisplayName("Q2: outside triangle")
    void testQ2Outside() throws Exception {
        assertFalse(invokeCheckHit(-1.0, "3.0", 4.0));
    }

    @Test
    @DisplayName("Q2: boundary")
    void testQ2Boundary() throws Exception {
        assertTrue(invokeCheckHit(-2.0, "0.0", 4.0));
    }

    @Test
    @DisplayName("Q4: inside circle quarter")
    void testQ4Inside() throws Exception {
        assertTrue(invokeCheckHit(1.0, "-1.0", 4.0));
    }

    @Test
    @DisplayName("Q4: outside circle quarter")
    void testQ4Outside() throws Exception {
        assertFalse(invokeCheckHit(4.0, "-4.0", 4.0));
    }

    @Test
    @DisplayName("Q4: boundary")
    void testQ4Boundary() throws Exception {
        assertTrue(invokeCheckHit(0.0, "-4.0", 4.0));
    }

    @Test
    @DisplayName("Q3: always miss")
    void testQ3AlwaysMiss() throws Exception {
        assertFalse(invokeCheckHit(-1.0, "-1.0", 4.0));
        assertFalse(invokeCheckHit(-0.1, "-0.1", 5.0));
    }

    @Test
    @DisplayName("Origin")
    void testOrigin() throws Exception {
        assertTrue(invokeCheckHit(0.0, "0.0", 4.0));
    }

    @Test
    @DisplayName("Invalid Y returns false")
    void testInvalidY() throws Exception {
        assertFalse(invokeCheckHit(1.0, "abc", 4.0));
    }

    @ParameterizedTest(name = "x={0}, y={1}, r={2} -> hit={3}")
    @CsvSource({
        "1.0, 1.0, 4.0, true",
        "0.5, 0.5, 3.0, true",
        "3.0, 2.0, 4.0, true",
        "-1.0, 0.5, 4.0, true",
        "-3.0, 3.0, 4.0, false",
        "1.0, -1.0, 4.0, true",
        "3.0, -3.0, 4.0, false",
        "-1.0, -1.0, 4.0, false"
    })
    void testParameterized(double x, String y, double r, boolean expected) throws Exception {
        assertEquals(expected, invokeCheckHit(x, y, r));
    }
}
