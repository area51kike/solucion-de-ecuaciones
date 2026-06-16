import sympy as sp
import numpy as np
from backend.methods.base import MetodoBase, Resultado

class Bairstow(MetodoBase):
    nombre = "Bairstow"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        x    = sp.Symbol('x')
        expr = ec['expr']
        coeffs_sym = self._verificar_polinomio_min(expr, 2)
        coeffs = [float(c) for c in coeffs_sym]
        n = len(coeffs) - 1

        r   = self._get_param(params, 'r',   0.0)
        s   = self._get_param(params, 's',   0.0)
        tol = self._get_param(params, 'tol', 0.0001)

        raices = []
        a = coeffs[:]
        convergio = True

        while len(a) - 1 >= 2:
            convergio_factor = False
            for _ in range(500):
                b = [0.0] * len(a)
                c = [0.0] * len(a)
                b[0] = a[0]
                b[1] = a[1] + r * b[0]
                for i in range(2, len(a)):
                    b[i] = a[i] + r * b[i-1] + s * b[i-2]
                c[0] = b[0]
                c[1] = b[1] + r * c[0]
                for i in range(2, len(a)):
                    c[i] = b[i] + r * c[i-1] + s * c[i-2]

                n_  = len(a) - 1
                denom = c[n_-2]**2 - c[n_-3]*c[n_-1]
                if abs(denom) < 1e-14:
                    break
                # Fórmulas correctas de Bairstow (Chapra, Métodos Numéricos)
                dr = (-b[n_-1]*c[n_-2] + b[n_]*c[n_-3]) / denom
                ds = (-b[n_]*c[n_-2]   + b[n_-1]*(c[n_-1] - b[n_])) / denom
                r += dr
                s += ds
                if abs(dr) < tol and abs(ds) < tol:
                    convergio_factor = True
                    break

            if not convergio_factor:
                convergio = False

            # Raíces del factor cuadrático x^2 - rx - s
            disc = r**2 + 4*s
            if disc >= 0:
                raices.append(round((r + disc**0.5) / 2, 10))
                raices.append(round((r - disc**0.5) / 2, 10))
            else:
                re = r / 2
                im = (-disc)**0.5 / 2
                raices.append({"re": round(re, 8), "im":  round(im, 8)})
                raices.append({"re": round(re, 8), "im": -round(im, 8)})

            a = b[:len(a)-2]

        if len(a) - 1 == 1:
            raices.append(round(-a[1]/a[0], 10))

        todas_complejas = all(isinstance(r, dict) for r in raices)
        if todas_complejas:
            warn = "Todas las raíces son complejas. La función no tiene raíces reales."
        elif not convergio:
            warn = (
        "El método no convergió con los valores iniciales r y s dados. "
        "Para ecuaciones cuadráticas sin raíces reales, intente con "
        "r = coeficiente de x con signo opuesto, s = término independiente con signo opuesto. "
        "Por ejemplo para x²-4x+7 use r=4, s=-7."
            )
        else:
            warn = None

        return Resultado(
            roots=raices if todas_complejas else ([] if not convergio else raices),
            converged=convergio,
            warning=warn
        )