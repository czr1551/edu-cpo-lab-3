import re
import math
import logging
from functools import wraps

# Configure logging for transparent interpreter tracing
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ExpressionError(Exception):
    """Custom exception for expression evaluation errors."""
    pass


def arg_type(pos, expected_type):
    """
    Decorator: ensure argument at position `pos` is instance of `expected_type`.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if pos >= len(args):
                raise ExpressionError(f"Missing argument at "
                                      f"position {pos} for {func.__name__}")
            if not isinstance(args[pos], expected_type):
                raise ExpressionError(
                    f"Argument {pos} of {func.__name__} must be "
                    f"{expected_type.__name__}, got {type(args[pos]).__name__}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


@arg_type(0, str)
def evaluate(expression, variables=None, functions=None):
    """
    Evaluate a mathematical expression via string
    substitution with correct precedence,
    supporting:
      - Parentheses grouping
      - Exponentiation (**), right-associative
      - *, /, //, % (left-associative)
      - +, - (binary, left-associative)
      - Unary minus
      - Multi-argument and user-defined functions
    """
    # --- Setup and validation ---
    variables = {} if variables is None else variables
    functions = {} if functions is None else functions
    if not isinstance(variables, dict):
        raise ExpressionError(f"`variables` must be a dict,"
                              f" got {type(variables).__name__}")
    if not isinstance(functions, dict):
        raise ExpressionError(f"`functions` must be a dict, "
                              f"got {type(functions).__name__}")
    for n, v in variables.items():
        if not isinstance(n, str):
            raise ExpressionError(f"Variable name {n!r} is not a string")
        if not isinstance(v, (int, float)):
            raise ExpressionError(
                f"Variable {n!r} has non-numeric value {v!r}")
    for n, f in functions.items():
        if not isinstance(n, str):
            raise ExpressionError(f"Function name {n!r} is not a string")
        if not callable(f):
            raise ExpressionError(f"Function {n!r} is not callable")

    # Combine math module + built-ins + user funcs
    math_funcs = {
        name: getattr(math, name)
        for name in dir(math)
        if callable(getattr(math, name)) and not name.startswith('_')
    }
    math_funcs.update({'max': max, 'min': min, 'pow': pow})
    all_functions = {**math_funcs, **functions}

    # Strip whitespace
    expr = re.sub(r'\s+', '', expression)
    if expr == '':
        raise ExpressionError("Empty expression")
    logger.debug(f"Start expr: {expr}")

    # Replace variables (leave function names intact)
    def _var(m):
        tok = m.group(0)
        if tok in variables:
            return str(variables[tok])
        if tok in all_functions:
            return tok
        raise ExpressionError(f"Unknown identifier '{tok}' in expression")
    expr = re.sub(r'\b[a-zA-Z_]\w*\b', _var, expr)
    logger.debug(f"After var repl: {expr}")

    # Flat evaluator: only numbers and ops
    def eval_flat(s):
        # 1) Exponentiation **, right-associative
        ep = re.compile(r'(-?\d+(?:\.\d+)?)(\*\*)(-?\d+(?:\.\d+)?)')
        while True:
            matches = list(ep.finditer(s))
            if not matches:
                break
            m = matches[-1]  # rightmost for right-assoc
            a, b = float(m.group(1)), float(m.group(3))
            try:
                r = a ** b
            except Exception as e:
                raise ExpressionError(f"Error computing {a}**{b}: {e}")
            s = s[:m.start()] + str(r) + s[m.end():]
            logger.debug(f"**: {a}**{b} -> {r}, now {s}")

        # 2) *, /, //, % left-assoc
        pat_mul = re.compile(
            r'(-?\d+(?:\.\d+)?)(?P<op>//|%|\*|/)(-?\d+(?:\.\d+)?)')
        while True:
            m = pat_mul.search(s)
            if not m:
                break
            a = float(m.group(1))
            op_sym = m.group('op')
            b = float(m.group(3))
            try:
                if op_sym == '*':
                    r = a * b
                elif op_sym == '/':
                    r = a / b
                elif op_sym == '//':
                    r = a // b
                elif op_sym == '%':
                    r = a % b
            except Exception as e:
                raise ExpressionError(f"Error computing {a}{op_sym}{b}: {e}")
            s = s[:m.start()] + str(r) + s[m.end():]
            logger.debug(f"{op_sym}: {a}{op_sym}{b} -> {r}, now {s}")

        # 3) +, - left-assoc
        pat_add = re.compile(
            r'(?<![\d)])(-?\d+(?:\.\d+)?)(?P<op>[+\-])(-?\d+(?:\.\d+)?)')
        while True:
            m = pat_add.search(s)
            if not m:
                break
            a = float(m.group(1))
            op_sym = m.group('op')
            b = float(m.group(3))
            if op_sym == '+':
                r = a + b
            else:
                r = a - b
            s = s[:m.start()] + str(r) + s[m.end():]
            logger.debug(f"{op_sym}: {a}{op_sym}{b} -> {r}, now {s}")

        return s

    # Recursive evaluator: functions & grouping
    def eval_expr(s):
        # Function calls
        func_pat = re.compile(r'([a-zA-Z_]\w*)\(([^()]*)\)')
        while True:
            m = func_pat.search(s)
            if not m:
                break
            fn, args_str = m.group(1), m.group(2)
            if fn not in all_functions:
                raise ExpressionError(f"Unknown function '{fn}' in expression")
            parts = [p for p in args_str.split(',') if p]
            vals = [eval_expr(p) for p in parts]
            try:
                r = all_functions[fn](*vals)
            except Exception as e:
                raise ExpressionError(f"Error in function '{fn}': {e}")
            s = s[:m.start()] + str(r) + s[m.end():]
            logger.debug(f"fn {fn}({args_str}) -> {r}, now {s}")

        # Grouping parentheses
        grp_pat = re.compile(r'\(([^()]*)\)')
        while True:
            m = grp_pat.search(s)
            if not m:
                break
            inner = m.group(1)
            r = eval_expr(inner)
            s = s[:m.start()] + str(r) + s[m.end():]
            logger.debug(f"grp ({inner}) -> {r}, now {s}")

        # Flat numeric evaluation
        res = eval_flat(s)
        try:
            return float(res)
        except ValueError:
            raise ExpressionError(
                f"Could not fully evaluate expression, got '{res}'")

    return eval_expr(expr)
