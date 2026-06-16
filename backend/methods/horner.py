import sympy as sp
import numpy as np
from backend.methods.base import MetodoBase, Resultado


class Horner(MetodoBase):
    nombre = "Horner"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        x = sp.Symbol('x')
        expr = ec['expr']
        coeffs_sym = self._verificar_polinomio_min(expr, 2)
        coeffs = [float(c) for c in coeffs_sym]

        raices_np = np.roots(coeffs)
        raices = []
        for r in raices_np:
            if abs(r.imag) < 1e-8:
                raices.append(round(r.real, 10))
            else:
                raices.append({"re": round(r.real, 8), "im": round(r.imag, 8)})

        todas_complejas = all(isinstance(r, dict) for r in raices)
        return Resultado(
            roots=raices,
            warning="Todas las raíces son complejas. La función no tiene raíces reales." if todas_complejas else None
        )