import cmath
from backend.methods.base import MetodoBase, Resultado

class Muller(MetodoBase):
    nombre = "Müller"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        x0    = self._get_param(params, 'x0',      0.0)
        x1    = self._get_param(params, 'x1',      1.0)
        x2    = self._get_param(params, 'x2',      2.0)
        tol   = self._get_param(params, 'tol',     0.0001)
        max_i = self._get_param(params, 'maxIter', 100, int)

        iters = []
        for i in range(max_i):
            f0, f1, f2 = f(x0), f(x1), f(x2)

            h0, h1   = x1 - x0, x2 - x1
            d0, d1   = (f1 - f0) / h0, (f2 - f1) / h1
            a        = (d1 - d0) / (h1 + h0)
            b        = a * h1 + d1
            c        = f2

            disc = b**2 - 4*a*c
            sq   = cmath.sqrt(complex(disc))
            den  = (b + sq) if abs(b + sq) > abs(b - sq) else (b - sq)

            if abs(den) < 1e-14:
                raise ValueError("División por cero en Müller.")

            dx = -2 * c / den
            x3 = x2 + dx
            err = abs(dx)
            self._agregar_iter(iters, i+1, x3.real, f(x3.real), err)

            if err < tol:
                r = x3
                if abs(r.imag) < 1e-8:
                    return Resultado(roots=[round(r.real, 10)], iterations=iters)
                return Resultado(
                    roots=[{"re": round(r.real, 8), "im": round(r.imag, 8)}],
                    iterations=iters
                )
            x0, x1, x2 = x1, x2, x3

        return Resultado(roots=[x2.real], iterations=iters,
                         warning="Se alcanzó el máximo de iteraciones.")