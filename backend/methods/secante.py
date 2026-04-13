from backend.methods.base import MetodoBase, Resultado


class Secante(MetodoBase):
    nombre = "Secante"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f = ec['f']
        xa = self._get_param(params, 'x0', 0.0)
        xb = self._get_param(params, 'x1', 1.0)
        tol = self._get_param(params, 'tol', 0.0001)
        max_i = self._get_param(params, 'maxIter', 100, int)

        iters = []
        for i in range(max_i):
            fa, fb = f(xa), f(xb)
            if abs(fb - fa) < 1e-14:
                raise ValueError("División por cero: f(x0) ≈ f(x1).")
            xc = xb - fb * (xb - xa) / (fb - fa)
            err = abs(xc - xb)
            self._agregar_iter(iters, i + 1, xc, f(xc), err)
            if err < tol:
                return Resultado(roots=[xc], iterations=iters)
            xa, xb = xb, xc

        return Resultado(roots=[xb], iterations=iters,
                         warning="Se alcanzó el máximo de iteraciones.")
