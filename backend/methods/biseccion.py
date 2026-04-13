from backend.methods.base import MetodoBase, Resultado

class Biseccion(MetodoBase):
    nombre = "Bisección"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        a     = self._get_param(params, 'a',       -2.0)
        b     = self._get_param(params, 'b',        2.0)
        tol   = self._get_param(params, 'tol',      0.0001)
        max_i = self._get_param(params, 'maxIter',  100, int)

        self._verificar_intervalo(f, a, b)

        iters = []
        for i in range(max_i):
            mid = (a + b) / 2
            err = (b - a) / 2
            self._agregar_iter(iters, i+1, mid, f(mid), err)

            if abs(f(mid)) < tol or err < tol:
                return Resultado(roots=[mid], iterations=iters)

            if f(a) * f(mid) < 0:
                b = mid
            else:
                a = mid

        return Resultado(
            roots=[mid],
            iterations=iters,
            warning="Se alcanzó el máximo de iteraciones."
        )