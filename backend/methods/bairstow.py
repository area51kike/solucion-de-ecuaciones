import sympy as sp
import numpy as np
from backend.methods.base import MetodoBase, Resultado

class Bairstow(MetodoBase):
    nombre = "Bairstow"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        x    = sp.Symbol('x')
        expr = ec['expr']
        poly = sp.Poly(expr, x)
        coeffs = [float(c) for c in poly.all_coeffs()]
        n = len(coeffs) - 1

        if n < 2:
            raise ValueError("Bairstow requiere grado ≥ 2.")

        r   = self._get_param(params, 'r',   0.0)
        s   = self._get_param(params, 's',   0.0)
        tol = self._get_param(params, 'tol', 0.0001)

        raices = []
        a = coeffs[:]

        while len(a) - 1 >= 2:
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
                J   = c[n_-2]**2 - (c[n_-3]) * (c[n_-1] - b[n_])
                if abs(J) < 1e-14:
                    break
                dr  = (-b[n_-1]*c[n_-2] + b[n_]*c[n_-3]) / J
                ds  = (-b[n_]*c[n_-2]   + b[n_-1]*(c[n_-1] - b[n_])) / J  # fixed
                # simpler:
                dr = (b[n_]*c[n_-2] - b[n_-1]*c[n_-1]) / (c[n_-2]**2 - c[n_-3]*c[n_-1])
                ds = (b[n_-1]*c[n_-2] - b[n_]*c[n_-3]) / (c[n_-2]**2 - c[n_-3]*c[n_-1])
                r += dr
                s += ds
                if abs(dr) < tol and abs(ds) < tol:
                    break

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

        return Resultado(roots=raices)