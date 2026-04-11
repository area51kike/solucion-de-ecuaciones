import sympy as sp
import numpy as np
import re

x = sp.Symbol('x')

# Alias para que el usuario pueda escribir de forma natural
ALIASES = {
    # Trigonométricas
    'sen':    'sin',
    'tg':     'tan',
    'arctg':  'atan',
    'arcsin': 'asin',
    'arccos': 'acos',
    # Logaritmos
    'ln':     'log',      # ln(x) → log(x) base e
    'log10':  'log(x,10)',# se maneja abajo
    # Constantes
    'π':      'pi',
    'e':      'E',
    '^':      '**',       # para que el usuario pueda escribir x^2
}

def normalizar(ecuacion: str) -> str:
    """
    Convierte la ecuación del usuario a formato sympy.
    Ejemplos:
        'x^2 + sen(x)'  →  'x**2 + sin(x)'
        '2x'            →  '2*x'
        'Ln(x)'         →  'log(x)'
    """
    ec = ecuacion.strip().lower()

    # Reemplazar alias
    for alias, real in ALIASES.items():
        ec = ec.replace(alias, real)

    # Multiplicación implícita: 2x → 2*x, x(... → x*(
    ec = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', ec)   # 2x → 2*x
    ec = re.sub(r'(\))(\w)',         r'\1*\2', ec)   # )x → )*x
    ec = re.sub(r'(\w)(\()',         r'\1*\2', ec)   # x( → x*(  (cuidado con funciones)

    # Restaurar funciones que no deben tener * (sin*, cos*, etc.)
    funciones = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan',
                 'log', 'exp', 'sqrt', 'abs', 'sinh', 'cosh', 'tanh']
    for fn in funciones:
        ec = ec.replace(fn + '*(', fn + '(')

    return ec


def parsear(ecuacion: str):
    """
    Recibe string del usuario y devuelve:
    - expr_sympy: expresión simbólica (para derivadas, etc.)
    - f_numpy:    función numérica evaluable con numpy
    - f_prime:    derivada numérica (útil para Newton)
    - f_double:   segunda derivada (útil para Newton mejorado)

    Lanza ValueError si la ecuación es inválida.
    """
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

    # Crear funciones numéricas con numpy
    modulos = ['numpy', {'Abs': np.abs, 'sign': np.sign}]
    f       = sp.lambdify(x, expr,                  modulos)
    f_prime = sp.lambdify(x, sp.diff(expr, x),      modulos)
    f_double= sp.lambdify(x, sp.diff(expr, x, 2),   modulos)

    return {
        'expr':    expr,
        'f':       f,
        'f_prime': f_prime,
        'f_double':f_double,
        'str':     str(expr),
    }


def evaluar(ecuacion: str, valor: float) -> float:
    """Evalúa f(valor) directamente desde un string."""
    resultado = parsear(ecuacion)
    return float(resultado['f'](valor))