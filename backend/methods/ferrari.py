import sympy as sp
from backend.methods.base import MetodoBase, Resultado

class Ferrari(MetodoBase):
    nombre = "Ferrari"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        x    = sp.Symbol('x')
        expr = ec['expr']
        self._verificar_polinomio(expr, 4)

        raices_sym = sp.solve(expr, x)
        raices = []
        for r in raices_sym:
            r_c = complex(r)
            if abs(r_c.imag) < 1e-8:
                raices.append(round(r_c.real, 10))
            else:
                raices.append({"re": round(r_c.real, 8), "im": round(r_c.imag, 8)})

        return Resultado(roots=raices)