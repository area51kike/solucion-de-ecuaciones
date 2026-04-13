import sympy as sp
import numpy as np
import re

x = sp.Symbol('x')

ALIASES = {
    'sen': 'sin',
    'tg': 'tan',
    'arctg': 'atan',
    'arcsin': 'asin',
    'arccos': 'acos',
    'ln': 'log',
    'log10': 'log(x,10)',
    'π': 'pi',
    'e': 'E',
    '^': '**',
}


def normalizar(ecuacion: str) -> str:
    ec = ecuacion.strip().lower()

    for alias, real in ALIASES.items():
        ec = ec.replace(alias, real)

    ec = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', ec)
    ec = re.sub(r'(\))(\w)', r'\1*\2', ec)
    ec = re.sub(r'(\w)(\()', r'\1*\2', ec)

    funciones = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan',
                 'log', 'exp', 'sqrt', 'abs', 'sinh', 'cosh', 'tanh']
    for fn in funciones:
        ec = ec.replace(fn + '*(', fn + '(')

    return ec


def parsear(ecuacion: str):
    ec_normalizada = normalizar(ecuacion)

    try:
        expr = sp.sympify(ec_normalizada, locals={
            'x': x,
            'e': sp.E,
            'pi': sp.pi,
        })
    except Exception:
        raise ValueError(f"No se pudo interpretar la ecuación: '{ecuacion}'")

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
