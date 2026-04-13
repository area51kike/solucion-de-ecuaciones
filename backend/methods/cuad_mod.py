import math
from backend.methods.base import MetodoBase, Resultado

class CuadMod(MetodoBase):
    nombre = "Cuadrática Modificada"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f = ec['f']
        f0, f1, fm1 = f(0), f(1), f(-1)
        a = (f1 + fm1 - 2*f0) / 2
        b = (f1 - fm1) / 2
        c = f0

        if abs(a) < 1e-12:
            raise ValueError("No se detectó término cuadrático.")

        disc = b**2 - 4*a*c

        if abs(disc) < 1e-8:
            return Resultado(roots=[-b / (2*a)],
                             warning="Raíz doble (discriminante ≈ 0).")

        if disc >= 0:
            sign_b = 1 if b >= 0 else -1
            q = -(b + sign_b * math.sqrt(disc)) / 2
            r1 = q / a
            r2 = c / q
            return Resultado(roots=[r1, r2])
        else:
            re = -b / (2*a)
            im = math.sqrt(-disc) / (2*a)
            return Resultado(
                roots=[{"re": re, "im": im}, {"re": re, "im": -im}],
                warning="Raíces complejas."
            )