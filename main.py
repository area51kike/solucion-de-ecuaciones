from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.parser import parsear
from backend.methods.biseccion      import Biseccion
from backend.methods.falsa_posicion import FalsaPosicion
from backend.methods.newton         import Newton
from backend.methods.newton_mod     import NewtonMod
from backend.methods.secante        import Secante
from backend.methods.punto_fijo     import PuntoFijo
from backend.methods.lineal         import Lineal
from backend.methods.cuadratica     import Cuadratica
from backend.methods.cuad_mod       import CuadMod
from backend.methods.tartaglia      import Tartaglia
from backend.methods.ferrari        import Ferrari
from backend.methods.horner         import Horner
from backend.methods.muller         import Muller
from backend.methods.bairstow       import Bairstow
from backend.methods.bairstow2      import Bairstow2

app = FastAPI(title="Ecuaciones Solver")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


class SolveRequest(BaseModel):
    equation: str
    method: str
    params: dict = {}


METODOS = {
    "biseccion":      Biseccion(),
    "falsa_posicion": FalsaPosicion(),
    "newton":         Newton(),
    "newton_mod":     NewtonMod(),
    "secante":        Secante(),
    "punto_fijo":     PuntoFijo(),
    "lineal":         Lineal(),
    "cuadratica":     Cuadratica(),
    "cuad_mod":       CuadMod(),
    "tartaglia":      Tartaglia(),
    "ferrari":        Ferrari(),
    "horner":         Horner(),
    "muller":         Muller(),
    "bairstow":       Bairstow(),
    "bairstow2":      Bairstow2(),
}


@app.get("/")
def root():
    return {"mensaje": "Servidor activo", "app": "/app", "docs": "/docs"}


@app.post("/solve")
def solve(req: SolveRequest):
    try:
        ec = parsear(req.equation)
    except ValueError as e:
        return {"error": True, "message": str(e), "roots": [], "iterations": []}

    metodo = METODOS.get(req.method)
    if not metodo:
        return {
            "error": False,
            "roots": [],
            "iterations": [],
            "message": f"El método '{req.method}' aún no está implementado."
        }

    return metodo.resolver(ec, req.params)