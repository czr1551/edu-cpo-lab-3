import pytest
from math_expression_by_string import evaluate, ExpressionError

# --- Simple arithmetic tests ---
def test_addition_and_subtraction():
    assert evaluate("1+2") == 3.0
    assert evaluate("5-3") == 2.0

def test_multiplication_and_division():
    assert evaluate("4*2") == 8.0
    assert evaluate("9/3") == 3.0

def test_integer_division_and_modulo():
    assert evaluate("10//3") == 3.0
    assert evaluate("10%3") == 1.0

def test_unary_minus():
    # Unary minus handling
    assert evaluate("-3+5") == 2.0
    assert evaluate("4*-2") == -8.0

# --- Parentheses and precedence ---
def test_parentheses_precedence():
    assert evaluate("(1+2)*3") == 9.0
    # Complex precedence
    expr = "3+4*2/(1-5)**2"
    # Compute expected: (1-5)=-4, 2**3=8 -> (-4)**2=16; 4*2=8; 8/16=0.5; +3
    assert evaluate(expr) == pytest.approx(3.5)

# --- Decimal and whitespace handling ---
def test_decimal_and_whitespace():
    assert evaluate("12.5*2") == 25.0
    assert evaluate(" -0.5 + 1.5 ") == 1.0

def test_nested_parentheses_and_whitespace():
    expr = " ((2 + 3) * max(1, 2, 3)) ** 2 / 5 % 2 "
    # (2+3)=5; max(...)=3 -> 5*3=15; 15**2=225; 225/5=45.0; 45.0%2=1.0
    assert evaluate(expr) == 1.0

# --- Built-in functions tests ---
def test_math_functions():
    assert evaluate("sin(0)") == pytest.approx(0.0)
    assert evaluate("cos(0)") == pytest.approx(1.0)

def test_multi_arg_functions():
    assert evaluate("max(1,2,3)") == 3.0
    assert evaluate("min(5,3,1)") == 1.0
    assert evaluate("pow(2,3)") == 8.0

# --- User-defined functions ---
def test_user_defined_function_single_arg():
    funcs = {"foo": lambda x: x*42}
    assert evaluate("foo(2)", functions=funcs) == 84.0

def test_user_defined_function_multi_arg():
    funcs = {"bar": lambda x, y: x + y}
    assert evaluate("bar(2,3)", functions=funcs) == 5.0

# --- Variables mapping tests ---
def test_variables_substitution():
    vals = {"a": 1.0, "b": 2.0}
    assert evaluate("a+b", variables=vals) == 3.0

# --- Error and boundary tests ---
def test_missing_expression_argument():
    with pytest.raises(ExpressionError):
        evaluate()

def test_non_string_expression():
    with pytest.raises(ExpressionError):
        evaluate(123)

def test_invalid_variables_type():
    with pytest.raises(ExpressionError):
        evaluate("1+1", variables=123)

def test_invalid_functions_type():
    with pytest.raises(ExpressionError):
        evaluate("1+1", functions=123)

def test_non_string_variable_name():
    with pytest.raises(ExpressionError):
        evaluate("1", variables={123: 4})

def test_non_numeric_variable_value():
    with pytest.raises(ExpressionError):
        evaluate("1", variables={"a": "x"})

def test_non_string_function_name():
    with pytest.raises(ExpressionError):
        evaluate("1", functions={123: lambda x: x})

def test_non_callable_function_value():
    with pytest.raises(ExpressionError):
        evaluate("foo(1)", functions={"foo": 123})

def test_unknown_variable():
    with pytest.raises(ExpressionError):
        evaluate("a+b", variables={"a":1})

def test_unknown_function():
    with pytest.raises(ExpressionError):
        evaluate("bar(1)")

def test_division_by_zero():
    with pytest.raises(ExpressionError):
        evaluate("1/0")

def test_int_division_by_zero():
    with pytest.raises(ExpressionError):
        evaluate("1//0")

def test_modulo_by_zero():
    with pytest.raises(ExpressionError):
        evaluate("1%0")

def test_empty_expression():
    with pytest.raises(ExpressionError):
        evaluate("")
