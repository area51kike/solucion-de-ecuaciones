from backend.methods.base import MetodoBase, Resultado

class PuntoFijo(MetodoBase):
    nombre = "Punto Fijo"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        x     = self._get_param(params, 'x0',      0.0)
        tol   = self._get_param(params, 'tol',     0.0001)
        max_i = self._get_param(params, 'maxIter', 100, int)

        # g(x) = x - f(x)  como función de iteración
        iters = []
        for i in range(max_i):
            xn  = x - f(x)
            err = abs(xn - x)
            self._agregar_iter(iters, i+1, xn, f(xn), err)
            if err < tol:
                return Resultado(roots=[xn], iterations=iters)
            x = xn

        return Resultado(roots=[x], iterations=iters,
                         warning="Se alcanzó el máximo de iteraciones.")