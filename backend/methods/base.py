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
        import math, numbers
        if isinstance(x, complex) or isinstance(fx, complex):
            raise ValueError(
                f"El método produjo un valor complejo en la iteración {n}. "
                f"La función evaluada fuera de su dominio real (p.ej. ln de negativo, √ de negativo). "
                f"Verifique el intervalo o punto inicial."
            )
        try:
            x = float(x); fx = float(fx); error = float(error)
        except Exception:
            raise ValueError(f"Valor no numérico en iteración {n}.")

        if math.isnan(x) or math.isinf(x):
            raise ValueError(
                f"El método divergió en la iteración {n}: x={x}. "
                f"Intente con un punto inicial diferente o verifique el dominio de la función."
            )
        if math.isnan(fx):
            raise ValueError(
                f"f(x) = indefinido en la iteración {n} (x={round(x,6)}). "
                f"El método salió del dominio de la función. "
                f"Intente con un punto inicial diferente."
            )
        lista.append(Iteracion(n=n, x=round(x,10), fx=round(fx,10), error=round(error,10)))

    def _verificar_dominio(self, f, x: float, nombre: str = "x"):
        """Lanza ValueError si f(x) produce nan, inf o complejo (punto fuera del dominio real)."""
        import math
        try:
            val = f(x)
        except Exception:
            raise ValueError(
                f"{nombre}={x} produce un error de evaluación. "
                f"Verifique que el punto esté en el dominio de la función."
            )
        if isinstance(val, complex):
            raise ValueError(
                f"f({nombre}={x}) = valor complejo. "
                f"El punto está fuera del dominio real de la función "
                f"(p.ej. √x con x<0, ln(x) con x≤0)."
            )
        try:
            val = float(val)
        except Exception:
            raise ValueError(
                f"f({nombre}={x}) no es un número real válido."
            )
        if math.isnan(val):
            raise ValueError(
                f"f({nombre}={x}) = indefinido. "
                f"El punto está fuera del dominio de la función "
                f"(p.ej. √x con x<0, ln(x) con x≤0, asin(x) con |x|>1)."
            )
        if math.isinf(val):
            raise ValueError(
                f"f({nombre}={x}) = ±∞. "
                f"La función tiene una singularidad en ese punto (p.ej. ln(0), 1/0)."
            )
        return val

    def _verificar_polinomio(self, expr, grado_esperado: int):
        """
        Verifica que expr sea un polinomio del grado exacto requerido.
        Lanza ValueError con mensaje claro si no lo es.
        """
        import sympy as sp
        x = sp.Symbol('x')
        try:
            poly = sp.Poly(expr, x)
        except sp.PolynomialError:
            raise ValueError(
                f"{self.nombre} solo funciona con ecuaciones polinomiales "
                f"(sin funciones como sin, cos, ln, exp, etc.). "
                f"Para ecuaciones trascendentales use Bisección, Newton u otro método iterativo."
            )
        grado = poly.degree()
        if grado != grado_esperado:
            raise ValueError(
                f"{self.nombre} requiere una ecuación polinomial de grado exactamente {grado_esperado}. "
                f"La ecuación ingresada es de grado {grado}."
            )
        return poly.all_coeffs()

    def _verificar_polinomio_min(self, expr, grado_minimo: int):
        """Igual que _verificar_polinomio pero acepta grado >= grado_minimo."""
        import sympy as sp
        x = sp.Symbol('x')
        try:
            poly = sp.Poly(expr, x)
        except sp.PolynomialError:
            raise ValueError(
                f"{self.nombre} solo funciona con ecuaciones polinomiales "
                f"(sin funciones como sin, cos, ln, exp, etc.)."
            )
        grado = poly.degree()
        if grado < grado_minimo:
            raise ValueError(
                f"{self.nombre} requiere una ecuación polinomial de grado ≥ {grado_minimo}. "
                f"La ecuación ingresada es de grado {grado}."
            )
        return poly.all_coeffs()

    def _buscar_intervalo_sugerido(self, f) -> tuple | None:
        """
        Escanea [-200, 200] en 200 pasos buscando un cambio de signo.
        Devuelve (a, b) con el primer cambio encontrado, o None si la
        función no tiene raíces reales detectables en ese rango.
        """
        import math
        lo, hi, pasos = -200.0, 200.0, 200
        dx = (hi - lo) / pasos
        xprev, fprev = lo, None
        try:
            fprev = float(f(lo))
            if math.isnan(fprev) or math.isinf(fprev):
                fprev = None
        except Exception:
            pass

        for i in range(1, pasos + 1):
            xnow = lo + i * dx
            try:
                fnow = float(f(xnow))
                if math.isnan(fnow) or math.isinf(fnow):
                    xprev, fprev = xnow, None
                    continue
            except Exception:
                xprev, fprev = xnow, None
                continue

            if fprev is not None and fprev * fnow < 0:
                return (round(xprev, 2), round(xnow, 2))

            xprev, fprev = xnow, fnow

        return None

    def _hint_raiz(self, f) -> str:
        """
        Devuelve una cadena de sugerencia lista para agregar a un warning.
        Usa _buscar_intervalo_sugerido internamente.
        """
        sug = self._buscar_intervalo_sugerido(f)
        if sug:
            xmid = round((sug[0] + sug[1]) / 2, 2)
            return (f" Hay un cambio de signo entre x={sug[0]} y x={sug[1]}: "
                    f"intente con un punto inicial cercano a x={xmid}.")
        return (" No se detectó ningún cambio de signo en [-200, 200]: "
                "es probable que la función no tenga raíces reales.")

    def _verificar_intervalo(self, f, a: float, b: float):
        """Verifica que f(a)*f(b) < 0. Si no, sugiere dónde buscar o avisa que no hay raíz."""
        fa = self._verificar_dominio(f, a, "a")
        fb = self._verificar_dominio(f, b, "b")
        if fa * fb >= 0:
            sug = self._buscar_intervalo_sugerido(f)
            if sug:
                raise ValueError(
                    f"f(a) y f(b) deben tener signos opuestos. "
                    f"f({a})={round(fa,6)}, f({b})={round(fb,6)}. "
                    f"Pruebe con a={sug[0]}, b={sug[1]}."
                )
            else:
                raise ValueError(
                    f"f(a) y f(b) deben tener signos opuestos. "
                    f"f({a})={round(fa,6)}, f({b})={round(fb,6)}. "
                    f"No se detectó ningún cambio de signo en [-200, 200]: "
                    f"es probable que la función no tenga raíces reales."
                )

    def _get_param_validado(self, params: dict, key: str, default, tipo=float):
        """Igual que _get_param pero valida rangos y da mensajes claros."""
        try:
            val = tipo(params.get(key, default))
        except (ValueError, TypeError):
            raw = params.get(key, default)
            raise ValueError(
                f"El parámetro '{key}' debe ser un número (recibido: '{raw}'). "
                f"Ingrese un valor numérico válido."
            )
        if tipo == int and val <= 0:
            raise ValueError(
                f"'{key}' debe ser un entero positivo (recibido: {val})."
            )
        if key == 'tol' and val <= 0:
            raise ValueError(
                f"La tolerancia debe ser un número positivo (recibido: {val}). "
                f"Valor típico: 0.0001"
            )
        return val

    def _get_x0(self, params: dict, key: str = 'x0', default: float = 0.0) -> float:
        """Obtiene punto inicial con error claro si no es numérico."""
        raw = params.get(key, default)
        try:
            val = float(raw)
        except (ValueError, TypeError):
            raise ValueError(
                f"'{key}' debe ser un número (recibido: '{raw}'). "
                f"Ingrese un valor numérico como punto inicial."
            )
        import math
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"'{key}' no es un número válido (recibido: '{raw}').")
        return val