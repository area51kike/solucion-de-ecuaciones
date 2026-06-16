from backend.methods.base import MetodoBase, Resultado

class FalsaPosicion(MetodoBase):
    nombre = "Falsa Posición"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        a     = self._get_x0(params, 'a', -2.0)
        b     = self._get_x0(params, 'b',  2.0)
        tol   = self._get_param_validado(params, 'tol',     0.0001)
        max_i = self._get_param_validado(params, 'maxIter', 100, int)

        if a > b:
            a, b = b, a

        if a == b:
            raise ValueError(
                f"Los límites a y b son iguales ({a}). "
                f"El intervalo debe tener amplitud mayor que cero."
            )

        self._verificar_intervalo(f, a, b)

        iters, xr_old = [], a
        xr = a
        for i in range(max_i):
            fa, fb = f(a), f(b)
            if abs(fa - fb) < 1e-14:
                raise ValueError(
                    f"f(a) ≈ f(b) en la iteración {i+1}. División por cero inminente."
                )
            xr  = b - fb * (a - b) / (fa - fb)
            err = abs(xr - xr_old) if i > 0 else float('inf')
            self._agregar_iter(iters, i+1, xr, f(xr), err)

            if abs(f(xr)) < tol:
                return Resultado(roots=[xr], iterations=iters)
            if f(a) * f(xr) < 0:
                b = xr
            else:
                a = xr
            xr_old = xr

        hint = self._hint_raiz(f)
        return Resultado(
            roots=[xr],
            iterations=iters,
            warning=(
                f"Se alcanzó el máximo de iteraciones ({max_i}). "
                f"El resultado puede no ser suficientemente preciso.{hint}"
            )
        )