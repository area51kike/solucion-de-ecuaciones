import math
from backend.methods.base import MetodoBase, Resultado

class CuadMod(MetodoBase):
    nombre = "Cuadrática Modificada"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        import math
        coeffs = self._verificar_polinomio(ec['expr'], 2)
        a, b, c = float(coeffs[0]), float(coeffs[1]), float(coeffs[2])

        disc = b**2 - 4*a*c

        if abs(disc) < 1e-10:
            return Resultado(roots=[-b / (2*a)],
                             warning="Raíz doble (discriminante ≈ 0).")
        if disc > 0:
            sign_b = 1 if b >= 0 else -1
            q = -(b + sign_b * math.sqrt(disc)) / 2
            r1 = q / a
            r2 = c / q if abs(q) > 1e-14 else -b/(2*a)
            return Resultado(roots=[r1, r2])
        else:
            re = -b / (2*a)
            im = math.sqrt(-disc) / (2*a)
            return Resultado(
                roots=[{"re": re, "im": im}, {"re": re, "im": -im}],
                warning="Raíces complejas (discriminante < 0)."
            )