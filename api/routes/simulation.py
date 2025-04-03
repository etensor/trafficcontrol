import sys
import os

from model.environment import TrafficControlEnv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import xmltodict
import asyncio
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
#from model.gymenv import TrafficControlEnv
from api.schemas.models import WebSocketResponse
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
   


@sim_router.post("/simulation/step", tags=["Simulation"])
async def simulation_step(steps: int = 1):
    try:
        if traci_env.is_traci_loaded():
            for _ in range(steps):
                traci_env.simulationStep() # better for performance
            return {"status": f"Simulation stepped forward X{steps}"} if steps > 1 else {"status": "Simulation stepped forward."}
        else:
            return {"status": "TraCI not connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stepping simulation: {e}")




@sim_router.post("/simulation/start", tags=["Simulation"])
async def start_simulation(request: Request, gui_mode: bool = False, step_length: float = 1, training_mode: bool = False):
    global srl_env
    try:
        app = request.app
        if training_mode:
            srl_env = TrafficControlEnv()
            app.state.training_mode = True
        else:
            proc = traci_env.initialize_traci(use_gui=gui_mode, step_length=step_length)
            app.state.sumo_pid = proc
        app.state.stop_flag = False
        app.state.pause_flag = False

        # SumoRL Env in control
        srl_env = TrafficControlEnv()
        return {
            "status": f"Simulation started on port: {sumo_cfg['port']}",
            "PID": proc.pid
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting simulation: {e}")



@sim_router.post("/simulation/run", tags=["Simulation"])
async def run_simulation(request: Request , timestep: float = 16.7):
    # run continuous simulation in background
    app = request.app

    app.state.stop_flag = False
    app.state.pause_flag = False

    proc = traci_env.initialize_traci(use_gui=True, step_length=20)
    srl_env = TrafficControlEnv()


    try:
        while not app.state.stop_flag:
            if not app.state.pause_flag:
                if traci_env.is_traci_loaded():
                    traci_env.simulationStep()
                    await asyncio.sleep(timestep/ 1000)
                else:
                    await traci_env.try_reconnect_sumo() # -> limit to N attempts maybe
            else:
                await asyncio.sleep(0.1) # cpu load reduction at pause
    except Exception as e:
        logger.error(f"Error in simulation/run: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in simulation/run: {str(e)}")
        
    finally:
        return {"status": "Simulation run loop completed.","completed": True } # quiza verbose para el cliente?



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
async def websocket_simulation_ctrl(ws: WebSocket, time_step: float = 16.67):
    await ws.accept()
    global srl_env
    try:
        app = ws.app
        last_sent = None

        if not hasattr(app.state, 'sumo_pid') or not app.state.sumo_pid:
            if not try_reconnect_sumo():
                await ws.send_json({"status": "No SUMO process found, unable to reconnect."})
                return

        if not traci_env.is_traci_loaded():
            await ws.send_json({"status": "TraCI not connected."})
            return

        while True:
            try:
                if not traci_env.is_traci_loaded():
                    await ws.send_json({"status": "TraCI not connected."})
                    break

                # Handle pause state
                if not app.state.pause_event.is_set():
                    if last_sent:
                        app.state.status_message = "Simulation paused"
                        last_sent["message"] = app.state.status_message
                        await ws.send_json(last_sent)
                    await app.state.pause_event.wait()
                    app.state.status_message = "Simulation running"

                # Build response based on environment mode
                if srl_env:
                    # RL Environment Mode
                    observation = srl_env.get_observation()
                    observation = convert_numpy_to_lists(observation)
                    response = WebSocketResponse(
                        observation=observation,
                        message=app.state.status_message,
                        timestamp=time.time(),
                        vehicles=veh_service.get_vehicle_count()
                    ).model_dump()
                else:
                    # Regular Data Collection Mode
                    tls_data = traffic_light_service.get_traffic_lights_data()
                    lane_data = lane_service.get_lanes_by_street()
                    e1_data = sensors_service.get_e1_sensors_data()
                    e2_data = sensors_service.get_e2_sensors_data()
                    agg_e2 = sensors_service.aggregate_e2_sensor_data_per_edge()

                    # Validate data
                    if not all([tls_data, lane_data, e1_data, e2_data]):
                        await ws.send_json({"status": "Missing subscription data"})
                        break

                    response = WebSocketResponse(
                        traffic_lights=tls_data,
                        lanes=lane_data,
                        e1_sensors=e1_data,
                        e2_sensors=e2_data,
                        e2_aggregated=agg_e2,
                        vehicles=veh_service.get_vehicle_count(),
                        timestamp=time.time(),
                        message=app.state.status_message
                    ).model_dump()

                # Send response
                last_sent = response
                await ws.send_json(response)
                await asyncio.sleep(time_step / 1000)

            except Exception as e:
                print(f"Error during data transmission: {e}")
                await ws.send_json({"status": "Error", "message": str(e)})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await ws.send_json({"status": "Error", "message": str(e)})
    finally:
        await ws.close()