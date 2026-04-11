from backend.methods.base import MetodoBase, Resultado

class NewtonMod(MetodoBase):
    nombre = "Newton Mejorado"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f      = ec['f']
        df     = ec['f_prime']
        d2f    = ec['f_double']
        x      = self._get_param(params, 'x0',      0.0)
        tol    = self._get_param(params, 'tol',      0.0001)
        max_i  = self._get_param(params, 'maxIter',  100, int)

        iters = []
        for i in range(max_i):
            fx, dfx, d2fx = f(x), df(x), d2f(x)
            denom = dfx**2 - fx * d2fx
            if abs(denom) < 1e-14:
                raise ValueError("Denominador cero. El método no converge.")
            xn  = x - fx * dfx / denom
            err = abs(xn - x)
            self._agregar_iter(iters, i+1, xn, f(xn), err)
            if err < tol:
                return Resultado(roots=[xn], iterations=iters)
            x = xn

        return Resultado(roots=[x], iterations=iters,
                         warning="Se alcanzó el máximo de iteraciones.")