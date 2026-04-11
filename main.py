from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ecuaciones Solver")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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