from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Iteracion:
    n:     int
    x:     float
    fx:    float
    error: float

@dataclass
class Resultado:
    roots:      list          = field(default_factory=list)
    iterations: list          = field(default_factory=list)
    converged:  bool          = True
    warning:    str | None    = None
    error:      bool          = False
    message:    str           = ""

    def to_dict(self) -> dict:
        return {
            "roots":      self.roots,
            "iterations": [vars(it) for it in self.iterations],
            "converged":  self.converged,
            "warning":    self.warning,
            "error":      self.error,
            "message":    self.message,
        }


class MetodoBase(ABC):

    nombre: str = "Método base"

    def resolver(self, ecuacion_dict: dict, params: dict) -> dict:
        try:
            resultado = self._calcular(ecuacion_dict, params)
        except ValueError as e:
            resultado = Resultado(error=True, message=str(e))
        except Exception as e:
            resultado = Resultado(error=True, message=f"Error interno: {str(e)}")

        return resultado.to_dict()

    @abstractmethod
    def _calcular(self, ecuacion_dict: dict, params: dict) -> Resultado:
        pass

    def _get_param(self, params: dict, key: str, default, tipo=float):
        try:
            return tipo(params.get(key, default))
        except (ValueError, TypeError):
            return tipo(default)

    def _agregar_iter(self, lista: list, n: int, x: float, fx: float, error: float):
        lista.append(Iteracion(n=n, x=round(x,10), fx=round(fx,10), error=round(error,10)))

    def _verificar_intervalo(self, f, a: float, b: float):
        if f(a) * f(b) >= 0:
            raise ValueError(
                f"f(a) y f(b) deben tener signos opuestos. "
                f"f({a})={round(f(a),6)}, f({b})={round(f(b),6)}"
            )