import json
import sys
import os

import traci

from model.environment import TrafficControlEnv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import xmltodict
import asyncio
from typing import List, Dict, Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, Query
#from model.gymenv import TrafficControlEnv
from api.schemas.models import WebSocketResponse, SimulationStartConfig, SimulationRunConfig
from api.services import lane_service, sensors_service, traffic_light_service
from api.utils.traci_env import sumo_cfg, try_reconnect_sumo
import api.utils.traci_env as traci_env
from api.utils.model_observation import convert_numpy_to_lists
from api.utils.logger import logger
import api.services.vehicle_service as veh_service



sim_router = APIRouter()


@sim_router.get("/simulation/details", tags=["Simulation"])
async def get_simulation_details():
    try:
        with open("../../escenario/osm2.sumocfg") as xmlcfg:
            sumo_cfg["content"] = xmltodict.parse(xmlcfg.read())
        return sumo_cfg
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting simulation details: {e}")



@sim_router.get("/simulation/status", tags=["Simulation"])
async def get_simulation_status(request: Request):
    try:
        app = request.app
        if app.state.sumo_pid:
            return {
                "status": True, 
                "PID": app.state.sumo_pid.pid,
                "paused": app.state.pause_flag
                }
        else:
            return {"status": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting simulation status: {e}")



@sim_router.post("/simulation/stop", tags=["Simulation"])
async def stop_simulation(request: Request):
    try:
        app = request.app
        app.state.stop_flag = True # set flag
        try:
            traci_env.traci.close() # attempt to close traci connection
            await asyncio.sleep(1) # wait for it to stop gracefully

            if app.state.sumo_pid:
                app.state.sumo_pid.terminate()
                # X traci_env.close_traci() # -> traci.terminate
                app.state.sumo_pid = None
            else:
                return {"status": "Simulation not running"}
    
        except Exception as e:
            print(f"Error closing traci connection: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping simulation: {e}")
    finally:
        return {"status": "Simulation stopped successfully"}
   




@sim_router.post("/simulation/step", tags=["Simulation"],
    summary="Advance simulation steps",
    description="""By a specified number of steps.
    Use this for manual control of simulation progression.""",
    response_description="Confirmation of steps executed"
)
async def simulation_step(
    steps: Annotated[
        int,
        Query(
            ge=1,
            le=1000,
            description="Number of steps to advance (1-1000)",
            example=10
        )
    ] = 1
):
    """
    Parameters:
    - steps: Number of simulation steps to execute (1-1000)
    
    Returns:
    - Status message with step count execution confirmation
    """
    try:
        if traci_env.is_traci_loaded():
            for _ in range(steps):
                traci_env.simulationStep()
            return {
                "status": f"Advanced {steps} steps",
                "steps_executed": steps
            }
        return {"status": "TraCI not connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@sim_router.post("/simulation/start",tags=["Simulation"],
    summary="Initialize simulation",
    response_description="Simulation initialization status",
    responses={
        200: {"description": "Simulation successfully started"},
        500: {"description": "SUMО initialization error"}
    }
)
async def start_simulation(
    request: Request,
    config: SimulationStartConfig = Depends() # Depends means it will be injected
):
    """
    Initialize SUMO simulation instance with optional RL training environment.
    
    - **gui_mode**: Visual interface for debugging
    - **step_length**: Simulation time precision
    - **training_mode**: Enable reinforcement learning control
    """
    try:
        app = request.app
        if config.training_mode:
            if not app.state.rl_env:
                app.state.rl_env = TrafficControlEnv()
            app.state.training_mode = True
            return {"status": "RL training environment initialized"}
        
        proc = traci_env.initialize_traci(
            use_gui=config.gui_mode,
            step_length=config.step_length
        )
        app.state.sumo_pid = proc
        return {
            "status": f"Simulation started on port: {sumo_cfg['port']}",
            "PID": proc.pid
        }
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise HTTPException(500, detail="Simulation initialization failed")




@sim_router.post("/simulation/run",tags=["Simulation"],
    summary="Run continuous simulation",
    response_description="Background simulation status",
    responses={
        200: {"description": "Simulation running in background"},
        422: {"description": "Invalid timestep parameter"},
        500: {"description": "Simulation runtime error"}
    }
)
async def run_simulation(
    request: Request,
    config: SimulationRunConfig = Depends()
):
    """Run continuous simulation with automatic stepping"""
    app = request.app
    app.state.stop_flag = False
    app.state.pause_flag = False

    try:
        start = time.time() 
        while not app.state.stop_flag:
            if not app.state.pause_flag and traci_env.is_traci_loaded():
                traci_env.simulationStep()
                await asyncio.sleep(config.timestep / 1000)
            else:
                await asyncio.sleep(0.1)
                
        return {"status": "Simulation completed", "duration": time.time() - start}
    except traci.TraCIException as e:
        logger.critical(f"TRACI failure: {str(e)}")
        raise HTTPException(500, detail="Connection to SUMO lost")
    except Exception as e:
        logger.error(f"Runtime error: {str(e)}")
        raise HTTPException(500, detail="Simulation execution failed")




# pause and resume actions
@sim_router.post("/simulation/toggle_pause", tags=["Simulation"])
async def toggle_pause_simulation(request: Request):
    app = request.app  # Access FastAPI app instance
    
    # Check if a SUMO simulation is running
    if not hasattr(app.state, 'sumo_pid') or not app.state.sumo_pid:
        return {"status": "No SUMO simulation is currently running."}
    
    #using flag
    if app.state.pause_event.is_set():
        # app.state.status_message = "Simulation paused"
        app.state.pause_event.clear()
        
        return {"message": app.state.status_message}
    
    else: # if paused then resume
        app.state.pause_event.set()
        # app.state.status_message = "Simulation running"
        return {"message": app.state.status_message}



    # Toggle between pause and resume
    # if hasattr(app.state, 'pause_flag') and app.state.pause_flag:
    #     # Resume the simulation
    #     app.state.pause_flag = False
    #     return {"status": "Simulation resumed"}
    # else:
    #     # Pause the simulation
    #     app.state.pause_flag = True
    #     return {"status": "Simulation paused"}


@sim_router.get("/test/tls", tags=["Debug"])
async def test_tls_data():
    data = traffic_light_service.get_traffic_lights_data()
    return {
        "raw": data,
        "json_ready": json.dumps(data, default=str)
    }


# ## Training the model API
# @sim_router.post("/simulation/train", tags=["Simulation"])
# async def train_model(request: Request, episodes: int = 10):
#     global traffic_env
#     if traffic_env is None:
#         raise HTTPException(status_code=500, detail="Simulation environment is not initialized.")

#     # Example using a basic loop to interact with the environment
#     for episode in range(episodes):
#         obs = traffic_env.reset()
#         done = False

#         while not done:
#             # Take a random action for now (can replace with actual RL model)
#             action = traffic_env.action_space.sample()
#             obs, reward, done, _ = traffic_env.step(action)
#             print(f"Episode: {episode + 1}, Reward: {reward}")

#     return {"status": "Training complete"}



### WebSockets: real-time data streaming
@sim_router.websocket("/simulation/ws", name="sim_websocket")
async def websocket_simulation_ctrl(
    ws: WebSocket,
    time_step: float = Query(16.67, gt=5.0, le=1000.0,
                           description="WebSocket update interval in ms")
):
    """
    Real-time monitoring channel with two modes:
    
    - **Training Mode**: RL observation space data
    - **Simulation Mode**: Live traffic metrics
    
    Message format adheres to WebSocketResponse model
    """
    await ws.accept()
    try:
        app = ws.app
        validate_simulation_state(app)
        
        while True:
            try:
                response = await form_ws_response(app)
                await ws.send_json(response)
                await asyncio.sleep(time_step / 1000)
                
            except WebSocketDisconnect:
                logger.info("Client disconnected")
                break
            except Exception as e:
                logger.error(f"WS transmission error: {str(e)}")
                await ws.send_json({"error": str(e)})
                
    finally:
        await handle_ws_cleanup(app, ws)




def validate_simulation_state(app):
    if not app.state.sumo_pid or not traci_env.is_traci_loaded():
        raise HTTPException(400, detail="Simulation not initialized")



async def form_ws_response(app) -> dict:
    base_data = {
        "timestamp": time.time(),
        "vehicles": veh_service.get_vehicle_count(),
        "message": app.state.status_message
    }
    
    if app.state.training_mode and app.state.rl_env:
        obs = convert_numpy_to_lists(app.state.rl_env.get_observation())
        response_model = WebSocketResponse(
            observation=obs,
            **base_data
        )
    else:
        response_model = WebSocketResponse(
            traffic_lights=traffic_light_service.get_traffic_lights_data(),
            lanes=lane_service.get_lanes_by_street(),
            e1_sensors=sensors_service.get_e1_sensors_data(),
            e2_sensors=sensors_service.get_e2_sensors_data(),
            e2_aggregated=sensors_service.aggregate_e2_sensor_data_per_edge(),
            **base_data
        )
    
    return response_model.model_dump()



async def handle_ws_cleanup(app, ws):
    try:
        await ws.close()
    except RuntimeError as e:
        logger.warning(f"Cleanup error: {str(e)}")
    finally:
        app.state.ws_connections.discard(ws)