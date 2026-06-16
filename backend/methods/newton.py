from backend.methods.base import MetodoBase, Resultado

class Newton(MetodoBase):
    nombre = "Newton-Raphson"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        df    = ec['f_prime']
        x     = self._get_x0(params, 'x0', 0.0)
        tol   = self._get_param_validado(params, 'tol',     0.0001)
        max_i = self._get_param_validado(params, 'maxIter', 100, int)

        self._verificar_dominio(f, x, 'x0')

        iters = []
        for i in range(max_i):
            fx, dfx = f(x), df(x)
            if abs(dfx) < 1e-14:
                raise ValueError(
                    f"Derivada cero en x={round(x,6)} (iteración {i+1}). "
                    f"El método no puede continuar. Intente con un x₀ diferente."
                )
            xn  = x - fx / dfx
            err = abs(xn - x)
            self._agregar_iter(iters, i+1, xn, f(xn), err)
            if err < tol:
                return Resultado(roots=[xn], iterations=iters)
            x = xn

        hint = self._hint_raiz(f)
        return Resultado(
            roots=[],
            iterations=iters,
            warning=(
                f"Se alcanzó el máximo de iteraciones ({max_i}). "
                f"Intente con un x₀ más cercano a la raíz.{hint}"
            )
        )