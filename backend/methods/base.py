from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

# ─────────────────────────────────────────────
# Estructura estándar de una iteración
# ─────────────────────────────────────────────
@dataclass
class Iteracion:
    n:     int
    x:     float
    fx:    float
    error: float


# ─────────────────────────────────────────────
# Estructura estándar del resultado
# Esto es lo que SIEMPRE devuelve el backend al frontend
# ─────────────────────────────────────────────
@dataclass
class Resultado:
    roots:      list          = field(default_factory=list)
    iterations: list          = field(default_factory=list)
    converged:  bool          = True
    warning:    str | None    = None
    error:      bool          = False
    message:    str           = ""

    def to_dict(self) -> dict:
        """Convierte a dict para enviarlo como JSON al frontend."""
        return {
            "roots":      self.roots,
            "iterations": [vars(it) for it in self.iterations],
            "converged":  self.converged,
            "warning":    self.warning,
            "error":      self.error,
            "message":    self.message,
        }


# ─────────────────────────────────────────────
# Clase base que todos los métodos heredan
# ─────────────────────────────────────────────
class MetodoBase(ABC):

    nombre: str = "Método base"

    def resolver(self, ecuacion_dict: dict, params: dict) -> dict:
        """
        Punto de entrada único para todos los métodos.
        Llama a _calcular() y atrapa cualquier error inesperado.
        """
        try:
            resultado = self._calcular(ecuacion_dict, params)
        except ValueError as e:
            resultado = Resultado(error=True, message=str(e))
        except Exception as e:
            resultado = Resultado(error=True, message=f"Error interno: {str(e)}")

        return resultado.to_dict()

    @abstractmethod
    def _calcular(self, ecuacion_dict: dict, params: dict) -> Resultado:
        """
        Cada método implementa su lógica aquí.
        Recibe:
          ecuacion_dict → salida de parsear() con f, f_prime, expr, etc.
          params        → parámetros del usuario (a, b, x0, tol, maxIter, etc.)
        Devuelve un objeto Resultado.
        """
        pass

    # ── Helpers comunes disponibles para todos los métodos ──

    def _get_param(self, params: dict, key: str, default, tipo=float):
        """Obtiene un parámetro con valor por defecto y conversión de tipo."""
        try:
            return tipo(params.get(key, default))
        except (ValueError, TypeError):
            return tipo(default)

    def _agregar_iter(self, lista: list, n: int, x: float, fx: float, error: float):
        """Agrega una iteración a la lista."""
        lista.append(Iteracion(n=n, x=round(x,10), fx=round(fx,10), error=round(error,10)))

    def _verificar_intervalo(self, f, a: float, b: float):
        """Verifica que f(a) y f(b) tengan signos opuestos (para métodos cerrados)."""
        if f(a) * f(b) >= 0:
            raise ValueError(
                f"f(a) y f(b) deben tener signos opuestos. "
                f"f({a})={round(f(a),6)}, f({b})={round(f(b),6)}"
            )