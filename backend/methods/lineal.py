from backend.methods.base import MetodoBase, Resultado

class Lineal(MetodoBase):
    nombre = "Lineal"

    def _calcular(self, ec: dict, params: dict) -> Resultado:
        f = ec['f']
        # f(x) = ax + b → a = f(1) - f(0), b = f(0)
        fa = f(0)
        slope = f(1) - fa
        if abs(slope) < 1e-12:
            raise ValueError("La ecuación no tiene pendiente. ¿Es realmente lineal?")
        root = -fa / slope
        return Resultado(roots=[root])