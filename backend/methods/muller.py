import cmath
from backend.methods.base import MetodoBase, Resultado

class Muller(MetodoBase):
    nombre = "Müller"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f     = ec['f']
        x0    = self._get_x0(params, 'x0', 0.0)
        x1    = self._get_x0(params, 'x1', 1.0)
        x2    = self._get_x0(params, 'x2', 2.0)
        tol   = self._get_param_validado(params, 'tol',     0.0001)
        max_i = self._get_param_validado(params, 'maxIter', 100, int)

        if x0 == x1 or x1 == x2 or x0 == x2:
            raise ValueError(
                f"x₀, x₁ y x₂ deben ser tres puntos distintos "
                f"(recibidos: x₀={x0}, x₁={x1}, x₂={x2})."
            )

        self._verificar_dominio(f, x0, 'x0')
        self._verificar_dominio(f, x1, 'x1')
        self._verificar_dominio(f, x2, 'x2')

        iters = []
        for i in range(max_i):
            f0, f1, f2 = f(x0), f(x1), f(x2)

            h0, h1 = x1 - x0, x2 - x1
            if abs(h0) < 1e-14 or abs(h1) < 1e-14:
                raise ValueError(
                    f"Dos puntos consecutivos son iguales en iteración {i+1}. "
                    f"El método no puede continuar."
                )

            d0 = (f1 - f0) / h0
            d1 = (f2 - f1) / h1
            a  = (d1 - d0) / (h1 + h0)
            b  = a * h1 + d1
            c  = f2

            disc = b**2 - 4*a*c
            sq   = cmath.sqrt(complex(disc))
            den  = (b + sq) if abs(b + sq) > abs(b - sq) else (b - sq)

            if abs(den) < 1e-14:
                raise ValueError(
                    f"División por cero en iteración {i+1}. "
                    f"Intente con puntos iniciales diferentes."
                )

            dx = -2 * c / den
            x3 = x2 + dx
            err = abs(dx)

            # Registrar amba parte real o imaginaria de iteraciones 
            fx3_real = f(x3.real) if abs(x3.imag) < 1e-8 else float('nan')
            try:
                self._agregar_iter(iters, i + 1, x3.real, fx3_real, err)
            except ValueError:
                pass
            if err < tol:
                r = x3
                if abs(r.imag) < 1e-8:
                    return Resultado(roots=[round(r.real, 10)], iterations=iters)
                return Resultado(
                    roots=[{"re": round(r.real, 8), "im": round(r.imag, 8)}],
                    iterations=iters,
                    warning="La raíz encontrada es compleja."
                )
            x0, x1, x2 = x1, x2, x3

        hint = self._hint_raiz(f)
        return Resultado(
            roots=[],
            iterations=iters,
            warning=(
                f"Se alcanzó el máximo de iteraciones ({max_i}). "
                f"Intente con puntos iniciales más cercanos a la raíz.{hint}"
            )
        )
