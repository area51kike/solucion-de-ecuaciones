import math, cmath
import sympy as sp
from backend.methods.base import MetodoBase, Resultado


class Tartaglia(MetodoBase):
    nombre = "Tartaglia"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        expr = ec['expr']
        x = sp.Symbol('x')
        poly = sp.Poly(expr, x)
        coeffs = poly.all_coeffs()

        if len(coeffs) != 4:
            raise ValueError("La ecuación debe ser de grado 3 exactamente.")

        A, B, C, D = [float(c) for c in coeffs]

        p = (3 * A * C - B ** 2) / (3 * A ** 2)
        q = (2 * B ** 3 - 9 * A * B * C + 27 * A ** 2 * D) / (27 * A ** 3)

        disc = -(4 * p ** 3 + 27 * q ** 2)

        delta = complex(-q / 2 + cmath.sqrt(q ** 2 / 4 + p ** 3 / 27))
        gamma = complex(-q / 2 - cmath.sqrt(q ** 2 / 4 + p ** 3 / 27))

        u = delta ** (1 / 3)
        v = gamma ** (1 / 3)

        w = complex(-1 / 2, math.sqrt(3) / 2)

        raices = []
        for k in range(3):
            r = u * w ** k + v * w ** (2 * k) - B / (3 * A)
            if abs(r.imag) < 1e-8:
                raices.append(round(r.real, 10))
            else:
                raices.append({"re": round(r.real, 8), "im": round(r.imag, 8)})

        warn = None if disc >= 0 else "Raíces complejas presentes."
        return Resultado(roots=raices, warning=warn)
