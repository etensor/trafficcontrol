import time
import xmltodict
import asyncio
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from schemas.models import WebSocketResponse
from services import lane_service, sensors_service, traffic_light_service
from utils.traci_env import sumo_cfg
import utils.traci_env as traci_env
from utils.logger import logger
import services.vehicle_service as veh_service



sim_router = APIRouter()


@sim_router.get("/simulation/details", tags=["Simulation"])
async def get_simulation_details():
    try:
        with open("../escenario/osm2.sumocfg") as xmlcfg:
            sumo_cfg["content"] = xmltodict.parse(xmlcfg.read())
        return sumo_cfg
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting simulation details: {e}")



@sim_router.get("/simulation/status", tags=["Simulation"])
async def get_simulation_status(request: Request):
    try:
        app = request.app
        if app.state.sumo_pid:
            return {"status": True, "PID": app.state.sumo_pid.pid}
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
async def start_simulation(request: Request, gui_mode: bool = False, time_step : float = 16.67):
    try:
        app = request.app # access to FastAPI app instance -> access state variables
        proc = traci_env.initialize_traci()
        app.state.sumo_pid = proc
        return {
            "status": f"Simulation started on port: {sumo_cfg['port']}",
            "PID": proc.pid
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting simulation: {e}")



@sim_router.post("/simulation/run", tags=["Simulation"])
async def run_simulation(request: Request , timestep: float):
    # run continuous simulation in background
    app = request.app

    app.state.stop_flag = False
    while True:
        if app.state.stop_flag:
            break

        if traci_env.is_traci_loaded():
            traci_env.simulationStep()
            await asyncio.sleep(timestep) 
        else:
            break



### WebSockets: real-time data streaming
@sim_router.websocket("/simulation/ws", name="sim_websocket")
async def websocket_simulation_ctrl(ws: WebSocket, time_step: float = 16.67):
    await ws.accept()
    try:
        app = ws.app
        
        # Validate SUMO and TraCI status
        if not hasattr(app.state, 'sumo_pid') or not app.state.sumo_pid:
            await ws.send_json({"status": "No SUMO process found."})
            return

        if not traci_env.is_traci_loaded():
            await ws.send_json({"status": "TraCI not connected."})
            return

        while True:
            try:
                if not traci_env.is_traci_loaded():
                    await ws.send_json({"status": "TraCI not connected."})
                    break

                # Fetch subscription data
                tls_data = traffic_light_service.get_traffic_lights_data()  
                lane_data = lane_service.get_lanes_by_street()
                e1_data = sensors_service.get_e1_sensors_data()  
                e2_data = sensors_service.get_e2_sensors_data()  
                
                # Check if data was properly retrieved
                if not tls_data:
                    await ws.send_json({"status": "No traffic light data available"})
                    break
                if not lane_data:
                    await ws.send_json({"status": "No lane data available"})
                    break
                if not e1_data or not e2_data:
                    await ws.send_json({"status": "No sensor data available"})
                    break

                sensors_data = {
                    "induction": e1_data,  # Ensure these match SensorData model
                    "lanearea": e2_data
                }

                # Construct response object
                response = WebSocketResponse(
                    traffic_lights=tls_data,
                    lanes=lane_data,
                    sensors=sensors_data,
                    timestamp=time.time()
                )

                # Send response to WebSocket
                await ws.send_json(response.model_dump())  # Ensure model_dump is valid
                await asyncio.sleep(time_step / 1000)  # Adjust time step appropriately
            
            except Exception as e:
                print(f"Error during data transmission: {e}")
                await ws.send_json({"status": "Error", "message": str(e)})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await ws.send_json({"status": "Error", "message": str(e)})
    finally:
        try:
            await ws.close()  # Close WebSocket connection
        except Exception:
            logger.error("Error closing WebSocket.")