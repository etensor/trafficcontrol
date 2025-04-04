from fastapi import FastAPI
from .routes.simulation import sim_router
from .routes.model_api import model_router
from .utils.logger import logger
from asyncio import Event
#from model.environment import TrafficControlEnv


app = FastAPI(
    title="RL Traffic Control SUMO API",
    description="Real-time traffic simulation control system para la tesis",
    openapi_tags=[
        {
            "name": "Simulation",
            "description": "Core simulation control endpoints"
        },
        {
            "name": "Monitoring",
            "description": "Real-time data streaming endpoints"
        },
        {
            "name": "Configuration",
            "description": "Model and environment configuration endpoints"
        }
    ]
)

app.state.sumo_pid = None  # PID del proceso de SUMO
app.state.training_mode = False
#srl_env = None // removing this thing <- global var nuh uh
app.state.rl_env = None # Initialize the environment <- global var nuh uh


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

