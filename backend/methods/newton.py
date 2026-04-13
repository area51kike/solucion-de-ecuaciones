from backend.methods.base import MetodoBase, Resultado


class Newton(MetodoBase):
    nombre = "Newton-Raphson"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f = ec['f']
        df = ec['f_prime']
        x = self._get_param(params, 'x0', 0.0)
        tol = self._get_param(params, 'tol', 0.0001)
        max_i = self._get_param(params, 'maxIter', 100, int)

        iters = []
        for i in range(max_i):
            fx, dfx = f(x), df(x)
            if abs(dfx) < 1e-14:
                raise ValueError(f"Derivada cero en x={x:.6f}. El método no converge.")
            xn = x - fx / dfx
            err = abs(xn - x)
            self._agregar_iter(iters, i + 1, xn, f(xn), err)
            if err < tol:
                return Resultado(roots=[xn], iterations=iters)
            x = xn

        return Resultado(roots=[x], iterations=iters,
                         warning="Se alcanzó el máximo de iteraciones.")
