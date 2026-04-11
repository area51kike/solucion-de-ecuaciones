from backend.methods.base import MetodoBase, Resultado

class FalsaPosicion(MetodoBase):
    nombre = "Falsa Posición"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        a     = self._get_param(params, 'a',      -2.0)
        b     = self._get_param(params, 'b',       2.0)
        tol   = self._get_param(params, 'tol',     0.0001)
        max_i = self._get_param(params, 'maxIter', 100, int)

        self._verificar_intervalo(f, a, b)

        iters, xr_old = [], a
        for i in range(max_i):
            xr  = b - f(b) * (a - b) / (f(a) - f(b))
            err = abs(xr - xr_old) if i > 0 else float('inf')
            self._agregar_iter(iters, i+1, xr, f(xr), err)

            if abs(f(xr)) < tol:
                return Resultado(roots=[xr], iterations=iters)
            if f(a) * f(xr) < 0:
                b = xr
            else:
                a = xr
            xr_old = xr

        return Resultado(roots=[xr], iterations=iters,
                         warning="Se alcanzó el máximo de iteraciones.")