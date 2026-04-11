import sympy as sp
import numpy as np
from backend.methods.base import MetodoBase, Resultado

class Horner(MetodoBase):
    nombre = "Horner"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        x    = sp.Symbol('x')
        expr = ec['expr']
        poly = sp.Poly(expr, x)
        coeffs = [float(c) for c in poly.all_coeffs()]

        raices_np = np.roots(coeffs)
        raices = []
        for r in raices_np:
            if abs(r.imag) < 1e-8:
                raices.append(round(r.real, 10))
            else:
                raices.append({"re": round(r.real, 8), "im": round(r.imag, 8)})

        return Resultado(roots=raices)