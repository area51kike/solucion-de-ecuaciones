import sympy as sp
import numpy as np
import re

x = sp.Symbol('x')

# Alias de nombres en español/alternativos → nombres de SymPy.
# IMPORTANTE: 'e' suelto (constante de Euler) se maneja DESPUÉS de proteger
# las funciones, para evitar que 'exp' se convierta en 'Exp'.
_ALIAS_FUNCIONES = {
    'sen':    'sin',
    'tg':     'tan',
    'arctg':  'atan',
    'arcsin': 'asin',
    'arccos': 'acos',
    'ln':     'log',
}

# Todas las funciones reconocidas (para protegerlas de la regex de '*')
_FUNCIONES = [
    'sinh', 'cosh', 'tanh',   # primero las más largas para evitar solapamiento
    'asin', 'acos', 'atan',
    'sin', 'cos', 'tan',
    'exp', 'log', 'sqrt', 'cbrt','abs',
]


def normalizar(ecuacion: str) -> str:
    ec = ecuacion.strip().lower()

    # 1) Reemplazar ^ antes de todo
    ec = ec.replace('^', '**')

    # 2) Alias de funciones en español → nombre de SymPy.
    #    Se usa lookahead (?=\() para matchear solo cuando el alias va seguido
    #    de '(', y lookbehind (?<![a-zA-Z]) para no tocar substrings.
    #    Esto funciona tanto en '2sen(' como en 'sen(' sin necesitar word-boundary.
    for alias, real in _ALIAS_FUNCIONES.items():
        ec = re.sub(rf'(?<![a-zA-Z]){alias}(?=\()', real, ec)

    # 3) Otros alias simples
    ec = ec.replace('π', 'pi')

    # 4) Insertar '*' para multiplicación implícita
    #    a) dígito seguido de letra o '('   →  "2x", "2sin", "2("
    ec = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', ec)
    #    b) ')' seguido de letra o dígito   →  ")x", ")2"
    ec = re.sub(r'(\))([a-zA-Z0-9])', r'\1*\2', ec)
    #    c) letra/dígito seguido de '('     →  "x(", "cos("
    ec = re.sub(r'([a-zA-Z0-9])(\()', r'\1*\2', ec)

    # 5) Reparar el '*' que la regex insertó dentro de nombres de función
    #    Ej: "sin*(" → "sin(",  "log*(" → "log("
    for fn in _FUNCIONES:
        ec = ec.replace(fn + '*(', fn + '(')

    # 6) Reemplazar 'e' como constante de Euler SOLO cuando es un token aislado
    #    Look-behind/ahead alfanumérico para no tocar 'exp', 'sec', 'cse', etc.
    ec = re.sub(r'(?<![a-zA-Z0-9])e(?![a-zA-Z0-9])', 'E', ec)

    return ec


def parsear(ecuacion: str):
    ec_normalizada = normalizar(ecuacion)


    try:
        expr = sp.sympify(ec_normalizada, locals={
            'x': x,
            'e': sp.E,
            'pi': sp.pi,
            'cbrt': lambda a: a ** sp.Rational(1, 3),
        })
    except Exception:
        raise ValueError(f"No se pudo interpretar la ecuación: '{ecuacion}'")

    if expr.has(sp.zoo) or expr.has(sp.nan):
            raise ValueError("La ecuación contiene una división por cero o es indefinida.")

    if not expr.has(x):
        raise ValueError("La ecuación debe contener la variable 'x'")

    modulos = ['numpy', {'Abs': np.abs, 'sign': np.sign}]
    f = sp.lambdify(x, expr, modulos)
    f_prime = sp.lambdify(x, sp.diff(expr, x), modulos)
    f_double = sp.lambdify(x, sp.diff(expr, x, 2), modulos)

    return {
        'expr': expr,
        'f': f,
        'f_prime': f_prime,
        'f_double': f_double,
        'str': str(expr),
    }


def evaluar(ecuacion: str, valor: float) -> float:
    resultado = parsear(ecuacion)
    return float(resultado['f'](valor))