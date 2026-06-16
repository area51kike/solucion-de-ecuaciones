from backend.methods.base import MetodoBase, Resultado

class NewtonMod(MetodoBase):
    nombre = "Newton Mejorado"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        df    = ec['f_prime']
        d2f   = ec['f_double']
        x     = self._get_x0(params, 'x0', 0.0)
        tol   = self._get_param_validado(params, 'tol',     0.0001)
        max_i = self._get_param_validado(params, 'maxIter', 100, int)

        self._verificar_dominio(f, x, 'x0')

        try:
            _df0  = df(x)
            _d2f0 = d2f(x)
        except Exception:
            raise ValueError(
                f"La derivada de la función no está definida en x₀={x}. "
                f"Verifique que x₀ esté dentro del dominio de la función y sus derivadas."
            )
        import math as _math
        if _math.isnan(_df0) or _math.isinf(_df0) or _math.isnan(_d2f0) or _math.isinf(_d2f0):
            raise ValueError(
                f"La derivada es indefinida o infinita en x₀={x}. "
                f"Elija un x₀ diferente, más alejado de singularidades."
            )

        iters = []
        for i in range(max_i):
            fx, dfx, d2fx = f(x), df(x), d2f(x)
            denom = dfx**2 - fx * d2fx
            if abs(denom) < 1e-14:
                raise ValueError(
                    f"Denominador cero en x={round(x,6)} (iteración {i+1}). "
                    f"El método no puede continuar. Intente con un x₀ diferente."
                )
            xn  = x - fx * dfx / denom
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