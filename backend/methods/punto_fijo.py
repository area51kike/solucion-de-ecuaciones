from backend.methods.base import MetodoBase, Resultado

class PuntoFijo(MetodoBase):
    nombre = "Punto Fijo"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        x     = self._get_x0(params, 'x0', 0.0)
        tol   = self._get_param_validado(params, 'tol',     0.0001)
        max_i = self._get_param_validado(params, 'maxIter', 100, int)

        self._verificar_dominio(f, x, 'x0')

        # ── Selección automática de g(x) ──────────────────────────────────
        # Se intenta encontrar un factor de relajación α tal que g(x) = x - α·f(x)
        # sea contractiva cerca de x₀, es decir |1 - α·f'(x₀)| < 1.
        # Estimamos f'(x₀) por diferencias finitas y elegimos α = 1/f'(x₀).
        # Esto es equivalente a un paso de Newton pero usado como g(x) fija.
        # Si f'(x₀) ≈ 0 usamos α = 1 (g(x) = x - f(x) funciona en ese caso).
        h = 1e-7
        try:
            fpx0 = (f(x + h) - f(x - h)) / (2 * h)
        except Exception:
            fpx0 = 0.0

        if abs(fpx0) > 1e-10:
            alpha = 1.0 / fpx0   # garantiza |g'(x₀)| ≈ 0 → contracción óptima
        else:
            alpha = 1.0

        def g(t):
            return t - alpha * f(t)

        iters     = []
        historial = []

        for i in range(max_i):
            try:
                xn = g(x)
            except Exception as exc:
                raise ValueError(f"Error evaluando g(x) en x={x:.6g}: {exc}")

            # Divergencia
            if abs(xn) > 1e12 or xn != xn:  # xn != xn detecta NaN
                hint = self._hint_raiz(f)
                raise ValueError(
                    f"El método de Punto Fijo diverge (x={xn:.2e} en iteración {i+1}). "
                    f"Intenta con un x₀ más cercano a la raíz.{hint}"
                )

            err = abs(xn - x)

            # Oscilación entre dos valores
            if len(historial) >= 4 and abs(xn - historial[-2]) < 1e-10:
                hint = self._hint_raiz(f)
                raise ValueError(
                    f"El método oscila entre {round(historial[-1], 6)} y {round(xn, 6)} "
                    f"sin converger. Intenta con un x₀ diferente.{hint}"
                )

            self._agregar_iter(iters, i + 1, xn, f(xn), err)
            historial.append(xn)

            if err < tol:
                return Resultado(roots=[xn], iterations=iters)

            x = xn

        hint = self._hint_raiz(f)
        return Resultado(
            roots=[x],
            iterations=iters,
            warning=(
                f"Se alcanzó el máximo de iteraciones ({max_i}). "
                f"Convergencia lenta — intenta con un x₀ más cercano a la raíz.{hint}"
            )
        )