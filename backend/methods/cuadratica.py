import math
from backend.methods.base import MetodoBase, Resultado

class Cuadratica(MetodoBase):
    nombre = "Cuadrática"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f = ec['f']
        f0, f1, fm1 = f(0), f(1), f(-1)
        a = (f1 + fm1 - 2*f0) / 2
        b = (f1 - fm1) / 2
        c = f0

        if abs(a) < 1e-12:
            raise ValueError("No se detectó término cuadrático. ¿Es realmente grado 2?")

        disc = b**2 - 4*a*c
        if disc >= 0:
            r1 = (-b + math.sqrt(disc)) / (2*a)
            r2 = (-b - math.sqrt(disc)) / (2*a)
            return Resultado(roots=[r1, r2])
        else:
            re =  -b / (2*a)
            im = math.sqrt(-disc) / (2*a)
            return Resultado(
                roots=[{"re": re, "im": im}, {"re": re, "im": -im}],
                warning="Raíces complejas (discriminante < 0)."
            )