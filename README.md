# GROUP-NO DAY OFF - lab 3 - variant "Mathematical
Expression by String Substitution"

This project implements a simple interpreter for mathematical expressions
using iterative string substitution. It supports variables,
built-in and user-defined functions, correct operator precedence,
and detailed error reporting with logging.

## Project structure

- `math_expression_by_string.py`
- Contains the evaluate() function and ExpressionError exception.
- Validates inputs (expression, variables, functions)
- Strips and tokenizes the expression
- Recursively handles function calls and grouping parentheses
- Performs flat numeric evaluation with correct operator precedence
- Uses Python’s math module and user-supplied callables
- Logs each substitution and computation step with logging

- `test_math_expression_by_string.py`
- Simple examples: basic arithmetic, unary minus
- Complex precedence: nested parentheses, exponent chains
- Decimal & whitespace: handling floats and arbitrary spaces
- Built-in & multi-arg functions: sin, cos, max, min, pow
- User-defined functions
- Variable substitution
- Error & boundary conditions: type checks,
  unknown identifiers, division by zero, empty expressions

## Features

- **Core functionality:**

- Basic arithmetic: +, -, *, /, //, %, **
- Correct precedence & associativity
- Parentheses: arbitrary nesting
- Built-in functions: all from Python’s math plus max, min, pow
- User functions: pass a functions dict of name→callable
- Variables: pass a variables dict of name→number
- Detailed errors: clear messages for missing args, type mismatches,
  unknown identifiers, runtime errors

## Contribution

- `<czr61551@gmail.com>` -- Implementation of `math_expression_by_string`,  
  documentation.

- `<quinn_wang0416@163.com>` -- Implementation of test cases.

## Changelog

- **2025-04-23 – 1.2**
- Fixed right-associative exponentiation edge cases
- Improved flat evaluator regex for mixed operators
- Enhanced error messages for empty expressions

- **12.02.2025 - 2**
- Refactored `_probe()` to correctly handle empty slots.

- **2025-04-21 – 1.1**
- Added support for // and % operators
- Integrated user-defined multi-argument functions

- **2025-04-19 – 1.0**
- Initial implementation of string-substitution evaluator
- Basic support: +, -, *, /, **, variables, built-in functions, logging

## Design notes

- Parsing approach: no AST or Python eval()—uses regex to locate
  innermost constructs and replace them with numeric results
- Function & grouping recursion:
  First handle function calls (to correctly parse f(1+2))
  Then strip a single layer of parentheses ((…​))
  Finally perform flat numeric reductions
- Logging: uses Python’s logging.DEBUG to trace each match, replacement
  and computed value
- Error safety:Decorated to enforce string-type expressions
  Checks for empty inputs, invalid variable/function mappings
  Catches runtime errors (like division by zero) and rethrows as
  ExpressionError with context
