from fastapi import FastAPI
from routes.simulation import sim_router
from utils.logger import logger


app = FastAPI()
app.state.sumo_pid = None  # PID del proceso de SUMO

#rutas 
app.include_router(sim_router)

@app.get("/")
def app_root():
    return {"TesisAPI": "Hello world"}

