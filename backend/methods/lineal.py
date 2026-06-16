from backend.methods.base import MetodoBase, Resultado


class Lineal(MetodoBase):
    nombre = "Lineal"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        coeffs = self._verificar_polinomio(ec['expr'], 1)
        a, b = float(coeffs[0]), float(coeffs[1])
        if abs(a) < 1e-12:
            raise ValueError("El coeficiente principal (de x) es cero. La ecuación no es lineal.")
        root = -b / a
        return Resultado(roots=[root])