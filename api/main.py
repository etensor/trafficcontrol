from fastapi import FastAPI
from routes.simulation import sim_router
from utils.logger import logger
from asyncio import Event


app = FastAPI()
app.state.sumo_pid = None  # PID del proceso de SUMO


if not hasattr(app.state, 'pause_event'):
    app.state.pause_event = Event()  # Create the event
    app.state.pause_event.set()


if not hasattr(app.state, 'status_message'):
    app.state.status_message = "No SUMO simulation is currently running."



#rutas 
app.include_router(sim_router)

@app.get("/")
def app_root():
    return {"TesisAPI": "Hello world"}

