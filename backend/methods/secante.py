from backend.methods.base import MetodoBase, Resultado

class Secante(MetodoBase):
    nombre = "Secante"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        xa    = self._get_x0(params, 'x0', 0.0)
        xb    = self._get_x0(params, 'x1', 1.0)
        tol   = self._get_param_validado(params, 'tol',     0.0001)
        max_i = self._get_param_validado(params, 'maxIter', 100, int)

        if xa == xb:
            raise ValueError(
                f"x₀ y x₁ son iguales ({xa}). "
                f"Deben ser dos puntos iniciales distintos."
            )

        self._verificar_dominio(f, xa, 'x0')
        self._verificar_dominio(f, xb, 'x1')

        iters = []
        for i in range(max_i):
            fa, fb = f(xa), f(xb)
            if abs(fb - fa) < 1e-14:
                raise ValueError(
                    f"f(x₀) ≈ f(x₁) en iteración {i+1}. División por cero. "
                    f"Intente con puntos iniciales más separados o diferentes."
                )
            xc  = xb - fb * (xb - xa) / (fb - fa)
            err = abs(xc - xb)
            self._agregar_iter(iters, i+1, xc, f(xc), err)
            if err < tol:
                return Resultado(roots=[xc], iterations=iters)
            xa, xb = xb, xc

        hint = self._hint_raiz(f)
        return Resultado(
            roots=[],
            iterations=iters,
            warning=(
                f"Se alcanzó el máximo de iteraciones ({max_i}). "
                f"Intente con puntos iniciales más cercanos a la raíz.{hint}"
            )
        )