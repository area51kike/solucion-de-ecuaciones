import math
from backend.methods.base import MetodoBase, Resultado

class Cuadratica(MetodoBase):
    nombre = "Cuadrática"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        import math
        coeffs = self._verificar_polinomio(ec['expr'], 2)
        a, b, c = float(coeffs[0]), float(coeffs[1]), float(coeffs[2])

        disc = b**2 - 4*a*c
        if disc > 0:
            r1 = (-b + math.sqrt(disc)) / (2*a)
            r2 = (-b - math.sqrt(disc)) / (2*a)
            return Resultado(roots=[r1, r2])
        elif abs(disc) < 1e-10:
            return Resultado(roots=[-b / (2*a)],
                             warning="Raíz doble (discriminante ≈ 0).")
        else:
            re =  -b / (2*a)
            im = math.sqrt(-disc) / (2*a)
            return Resultado(
                roots=[{"re": re, "im": im}, {"re": re, "im": -im}],
                warning="Raíces complejas (discriminante < 0)."
            )