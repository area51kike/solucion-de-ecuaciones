import math, cmath
from backend.methods.base import MetodoBase, Resultado

class Tartaglia(MetodoBase):
    nombre = "Tartaglia"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f = ec['f']
        # Detectar coeficientes de x^3 + px + q evaluando en 4 puntos
        # f(x) = ax^3 + bx^2 + cx + d
        f0  = f(0)
        f1  = f(1)
        fm1 = f(-1)
        f2  = f(2)

        a = (f2 - 2*f1 + 2*fm1 - f(- 2)) / 12 if False else None
        # Método directo con 4 puntos
        d = f0
        a = (f2 - 3*f1 + 3*f0 - fm1) / 6  # no exact but approx
        # Usar sympy para extraer coeficientes exactos
        expr = ec['expr']
        import sympy as sp
        x = sp.Symbol('x')
        poly = sp.Poly(expr, x)
        coeffs = poly.all_coeffs()

        if len(coeffs) != 4:
            raise ValueError("La ecuación debe ser de grado 3 exactamente.")

        A, B, C, D = [float(c) for c in coeffs]

        # Reducir a forma deprimida t^3 + pt + q
        p = (3*A*C - B**2) / (3*A**2)
        q = (2*B**3 - 9*A*B*C + 27*A**2*D) / (27*A**3)

        disc = -(4*p**3 + 27*q**2)

        delta = complex(-q/2 + cmath.sqrt(q**2/4 + p**3/27))
        gamma = complex(-q/2 - cmath.sqrt(q**2/4 + p**3/27))

        cbrt = lambda z: z**(1/3) if z.real >= 0 else -(-z)**(1/3)

        u = delta**(1/3)
        v = gamma**(1/3)

        w = complex(-1/2, math.sqrt(3)/2)  # raíz cúbica de la unidad

        raices = []
        for k in range(3):
            r = u * w**k + v * w**(2*k) - B/(3*A)
            if abs(r.imag) < 1e-8:
                raices.append(round(r.real, 10))
            else:
                raices.append({"re": round(r.real, 8), "im": round(r.imag, 8)})

        warn = None if disc >= 0 else "Raíces complejas presentes."
        return Resultado(roots=raices, warning=warn)