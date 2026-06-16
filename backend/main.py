from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import math

from backend.parser import parsear
from backend.methods.biseccion import Biseccion
from backend.methods.falsa_posicion import FalsaPosicion
from backend.methods.newton import Newton
from backend.methods.newton_mod import NewtonMod
from backend.methods.secante import Secante
from backend.methods.punto_fijo import PuntoFijo
from backend.methods.muller import Muller
from backend.methods.lineal import Lineal
from backend.methods.cuadratica import Cuadratica
from backend.methods.cuad_mod import CuadMod
from backend.methods.tartaglia import Tartaglia
from backend.methods.ferrari import Ferrari
from backend.methods.horner import Horner
from backend.methods.bairstow import Bairstow
from backend.methods.bairstow2 import Bairstow2

app = FastAPI(title="Ecuaciones Solver")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

METODOS = {
    "biseccion":      Biseccion(),
    "falsa_posicion": FalsaPosicion(),
    "newton":         Newton(),
    "newton_mod":     NewtonMod(),
    "secante":        Secante(),
    "punto_fijo":     PuntoFijo(),
    "muller":         Muller(),
    "lineal":         Lineal(),
    "cuadratica":     Cuadratica(),
    "cuad_mod":       CuadMod(),
    "tartaglia":      Tartaglia(),
    "ferrari":        Ferrari(),
    "horner":         Horner(),
    "bairstow":       Bairstow(),
    "bairstow2":      Bairstow2(),
}


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


def limpiar(val):
    """Convierte nan/inf a None para que JSON no explote."""
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    if isinstance(val, dict):
        return {k: limpiar(v) for k, v in val.items()}
    return val


@app.get("/")
def root():
    return {"mensaje": "Servidor activo", "docs": "/docs", "app": "/app"}


@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    # 1. Validar que el método existe
    metodo = METODOS.get(req.method)
    if metodo is None:
        return SolveResponse(
            roots=[], error=True,
            message=f"Método '{req.method}' no reconocido. "
                    f"Métodos disponibles: {', '.join(METODOS.keys())}"
        )

    # 2. Parsear la ecuación con el parser corregido
    try:
        ec = parsear(req.equation)
    except Exception as e:
        return SolveResponse(roots=[], error=True,
                             message=f"Error al parsear la ecuación: {e}")

    # 3. Ejecutar el método
    resultado = metodo.resolver(ec, req.params)

    # 4. Limpiar nan/inf antes de responder
    roots_limpias = [limpiar(r) for r in resultado.get("roots", [])]
    iters_limpias = [
        {k: limpiar(v) for k, v in it.items()}
        for it in (resultado.get("iterations") or [])
    ]

    return SolveResponse(
        roots=roots_limpias,
        iterations=iters_limpias,
        warning=resultado.get("warning") or "",
        error=resultado.get("error", False),
        message=resultado.get("message") or "",
    )