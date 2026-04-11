from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # ← agregar

app = FastAPI(title="Ecuaciones Solver")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ← Montar la carpeta frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def root():
    return {"mensaje": "Servidor funcionando"}

@app.post("/solve")
def solve(data: dict):
    return {
        "method": data.get("method"),
        "equation": data.get("equation"),
        "roots": [],
        "message": "En construcción"
    }