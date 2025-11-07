import math
import pytest
from src.functions.calculator import calculator

@pytest.mark.parametrize(
    "a,b,op,expected",
    [
        (2, 3, "+", 5.0),
        (2, 3, "-", -1.0),
        (2, 3, "*", 6.0),
        (6, 3, "/", 2.0),
        (2.5, 0.5, "+", 3.0),
        (2.5, 0.5, "-", 2.0),
        (2.5, 0.5, "*", 1.25),
        (2.5, 0.5, "/", 5.0),
    ],
)
def test_basic_ops(a, b, op, expected):
    assert calculator(a, b, op) == pytest.approx(expected)

def test_division_by_zero_returns_inf():
    result = calculator(5, 0, "/")
    assert math.isinf(result) and result > 0

@pytest.mark.parametrize("a,b", [(0, 9999), (9999, 0), (-5, -7)])
def test_handles_ints_and_zero(a, b):
    out = calculator(a, b, "+")
    assert isinstance(out, float)

def test_float_accuracy_reasonable():
    assert calculator(0.1, 0.2, "+") == pytest.approx(0.3, abs=1e-9)

def test_unsupported_operator_raises():
    with pytest.raises(ValueError):
        calculator(1, 2, "%")
