from fastapi import FastAPI
from api.routes.simulation import sim_router
from api.routes.model_api import model_router
from api.utils.logger import logger
from asyncio import Event
from model.environment import TrafficControlEnv


app = FastAPI()
app.state.sumo_pid = None  # PID del proceso de SUMO
srl_env = None


if not hasattr(app.state, 'pause_event'):
    app.state.pause_event = Event()  # Create the event
    app.state.pause_event.set()


if not hasattr(app.state, 'status_message'):
    app.state.status_message = "No SUMO simulation is currently running."



#rutas 
app.include_router(sim_router)
app.include_router(model_router)

@app.get("/")
def app_root():
    return {"TesisAPI": "Hello world"}

