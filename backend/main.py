from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any
import math

app = FastAPI(title="Ecuaciones Solver")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir el frontend desde la carpeta /frontend
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


# ── Modelos ──────────────────────────────────────────────
class SolveRequest(BaseModel):
    equation: str
    method: str
    params: dict = {}


class SolveResponse(BaseModel):
    roots: list
    iterations: list = []
    warning: str = ""
    error: bool = False
    message: str = ""


# ── Parser: convierte texto a función Python ─────────────
def parse_function(expr: str):
    safe = (expr
            .replace("^", "**")
            .replace("sin",  "math.sin")
            .replace("cos",  "math.cos")
            .replace("tan",  "math.tan")
            .replace("exp",  "math.exp")
            .replace("sqrt", "math.sqrt")
            .replace("log",  "math.log")
            .replace("abs",  "abs")
            )
    def f(x):
        return eval(safe, {"math": math, "x": x})
    return f


def derivative(f, h=1e-7):
    return lambda x: (f(x + h) - f(x - h)) / (2 * h)


# ── Endpoints ────────────────────────────────────────────
@app.get("/")
def root():
    return {"mensaje": "Servidor activo", "docs": "/docs", "app": "/app"}


@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    try:
        f = parse_function(req.equation)
        p = req.params
        tol     = float(p.get("tol",     0.0001))
        max_i   = int(p.get("maxIter",   100))
        x0      = float(p.get("x0",      0))
        x1      = float(p.get("x1",      1))
        a       = float(p.get("a",      -2))
        b       = float(p.get("b",       2))

        method = req.method

        # ── Bisección ────────────────────────────────────
        if method == "biseccion":
            if f(a) * f(b) > 0:
                return SolveResponse(roots=[], error=True,
                                     message="f(a) y f(b) tienen el mismo signo. No hay raíz garantizada en [a, b].")
            iters, lo, hi = [], a, b
            for i in range(max_i):
                mid = (lo + hi) / 2
                err = (hi - lo) / 2
                iters.append({"n": i+1, "x": mid, "fx": f(mid), "error": err})
                if abs(f(mid)) < tol or err < tol:
                    return SolveResponse(roots=[mid], iterations=iters)
                if f(lo) * f(mid) < 0:
                    hi = mid
                else:
                    lo = mid
            return SolveResponse(roots=[mid], iterations=iters,
                                 warning="Se alcanzó el máximo de iteraciones.")

        # ── Falsa posición ───────────────────────────────
        elif method == "falsa_posicion":
            if f(a) * f(b) > 0:
                return SolveResponse(roots=[], error=True,
                                     message="f(a) y f(b) tienen el mismo signo.")
            iters, lo, hi, xr_old = [], a, b, a
            for i in range(max_i):
                xr = hi - f(hi) * (lo - hi) / (f(lo) - f(hi))
                err = abs(xr - xr_old) if i > 0 else float('inf')
                iters.append({"n": i+1, "x": xr, "fx": f(xr), "error": err})
                if abs(f(xr)) < tol:
                    return SolveResponse(roots=[xr], iterations=iters)
                if f(lo) * f(xr) < 0:
                    hi = xr
                else:
                    lo = xr
                xr_old = xr
            return SolveResponse(roots=[xr], iterations=iters,
                                 warning="Se alcanzó el máximo de iteraciones.")

        # ── Newton-Raphson ───────────────────────────────
        elif method == "newton":
            df = derivative(f)
            x, iters = x0, []
            for i in range(max_i):
                fx, dfx = f(x), df(x)
                if abs(dfx) < 1e-14:
                    return SolveResponse(roots=[], error=True,
                                         message=f"Derivada cero en x={x:.6f}. El método no converge aquí.")
                xn = x - fx / dfx
                err = abs(xn - x)
                iters.append({"n": i+1, "x": xn, "fx": f(xn), "error": err})
                if err < tol:
                    return SolveResponse(roots=[xn], iterations=iters)
                x = xn
            return SolveResponse(roots=[x], iterations=iters,
                                 warning="Se alcanzó el máximo de iteraciones.")

        # ── Newton mejorado ──────────────────────────────
        elif method == "newton_mod":
            df  = derivative(f)
            d2f = derivative(df)
            x, iters = x0, []
            for i in range(max_i):
                fx, dfx, d2fx = f(x), df(x), d2f(x)
                denom = dfx**2 - fx * d2fx
                if abs(denom) < 1e-14:
                    return SolveResponse(roots=[], error=True,
                                         message="Denominador cero. El método no converge aquí.")
                xn = x - fx * dfx / denom
                err = abs(xn - x)
                iters.append({"n": i+1, "x": xn, "fx": f(xn), "error": err})
                if err < tol:
                    return SolveResponse(roots=[xn], iterations=iters)
                x = xn
            return SolveResponse(roots=[x], iterations=iters,
                                 warning="Se alcanzó el máximo de iteraciones.")

        # ── Secante ──────────────────────────────────────
        elif method == "secante":
            xa, xb, iters = x0, x1, []
            for i in range(max_i):
                fa, fb = f(xa), f(xb)
                if abs(fb - fa) < 1e-14:
                    return SolveResponse(roots=[], error=True,
                                         message="División por cero: f(x₀) ≈ f(x₁).")
                xc = xb - fb * (xb - xa) / (fb - fa)
                err = abs(xc - xb)
                iters.append({"n": i+1, "x": xc, "fx": f(xc), "error": err})
                if err < tol:
                    return SolveResponse(roots=[xc], iterations=iters)
                xa, xb = xb, xc
            return SolveResponse(roots=[xb], iterations=iters,
                                 warning="Se alcanzó el máximo de iteraciones.")

        # ── Cuadrática ───────────────────────────────────
        elif method in ("cuadratica", "cuad_mod"):
            fa, fb, fc = f(0), f(1), f(-1)
            ca = (fb + fc - 2*fa) / 2
            cb = (fb - fc) / 2
            cc = fa
            if abs(ca) < 1e-12:
                return SolveResponse(roots=[], error=True,
                                     message="No se detectó término cuadrático. ¿Es realmente grado 2?")
            disc = cb**2 - 4*ca*cc
            if method == "cuad_mod" and abs(disc) < 1e-8:
                r = -cb / (2*ca)
                return SolveResponse(roots=[r], warning="Raíz doble (discriminante ≈ 0).")
            if disc >= 0:
                r1 = (-cb + math.sqrt(disc)) / (2*ca)
                r2 = (-cb - math.sqrt(disc)) / (2*ca)
                return SolveResponse(roots=[r1, r2])
            else:
                re = -cb / (2*ca)
                im = math.sqrt(-disc) / (2*ca)
                return SolveResponse(
                    roots=[{"re": re, "im": im}, {"re": re, "im": -im}],
                    warning="Las raíces son complejas (discriminante < 0).")

        # ── Lineal ───────────────────────────────────────
        elif method == "lineal":
            fa, fb = f(0), f(1)
            slope = fb - fa
            if abs(slope) < 1e-12:
                return SolveResponse(roots=[], error=True,
                                     message="La ecuación no tiene pendiente. ¿Es realmente lineal?")
            root = -fa / slope
            return SolveResponse(roots=[root])

        # ── Método no implementado aún ───────────────────
        else:
            return SolveResponse(
                roots=[],
                warning=f"El método '{method}' aún no está implementado. Próximamente.",
                error=False
            )

    except Exception as e:
        return SolveResponse(roots=[], error=True, message=str(e))