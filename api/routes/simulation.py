import json
import sys
import os

import traci

from model.environment import TrafficControlEnv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import xmltodict
import asyncio
from typing import List, Dict, Annotated, Optional
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
                "paused": app.state.pause_event
                }
        else:
            return {"status": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting simulation status: {e}")



@sim_router.post("/simulation/stop", tags=["Simulation"])
async def stop_simulation(request: Request):
    try:
        app = request.app
        #app.state.pause_event = True # set flag
        
        try:
            traci_env.traci.close() # attempt to close traci connection
            await asyncio.sleep(1) # wait for it to stop gracefully

            if app.state.sumo_pid:
                app.state.sumo_pid.terminate()
                # X traci_env.close_traci() # -> traci.terminate
                app.state.status_message = "Simulation stopped"
                app.state.sumo_pid = None
            else:
                app.state.status_message = "No active simulation to stop"
                return {"status": "Simulation not running"}
    
        except Exception as e:
            print(f"Error closing traci connection: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping simulation: {e}")
    finally:
        app.state.status_message = "No active simulation"
        return {"status": "Simulation stopped successfully"}
   




@sim_router.post("/simulation/step", tags=["Simulation"],
    summary="Advance simulation steps",
    description="""By a specified number of steps.
    Use this for manual control of simulation progression.""",
    response_description="Confirmation of steps executed"
)
async def simulation_step(
    request: Request,
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
        app = request.app
        if not traci_env.is_traci_loaded():
            return {"status": "TraCI not connected"}
        
        executed = 0
        for _ in range(steps):
            if app.state.pause_event:
                traci_env.simulationStep()
                executed += 1
            else:
                await asyncio.sleep(0.1)
        
        return {"status": f"Advanced {executed}/{steps} steps"}
    
    except Exception as e:
        raise HTTPException(500, detail=str(e))




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
    use_gui: bool = Query(False, description="Enable visual interface"),
    step_length: float = Query(1.0, description="Simulation step duration in seconds"),
    num_steps: int = Query(0, description="Immediate steps to execute (headless only)"),
    autostart: bool = Query(True, description="Auto-start GUI simulation"),
    gui_delay: int = Query(20, description="GUI refresh delay in milliseconds")
):
    """Initialize SUMO simulation instance"""
    try:
        app = request.app

        app.state.status_message = "Simulation starting..."

        proc = await traci_env.initialize_traci(
            use_gui=use_gui,
            step_length=step_length,
            autostart=autostart,
            gui_delay=gui_delay,
            num_steps=num_steps
        )

        if hasattr(app.state, "pause_event"):
            app.state.status_message = "Simulation running"
            app.state.pause_event.set() # Initially running


        app.state.sumo_pid = proc
        app.state.status_message = f"Simulation started on port {str(sumo_cfg['port'])} with PID {proc.pid}"
        
        return {
            "status": f"Simulation {'GUI' if use_gui else 'headless'} started",
            "steps_executed": num_steps,
            "port": sumo_cfg['port'],
            "message": app.state.status_message,
            "pid": proc.pid
        }
    
    except FileNotFoundError as e:
        logger.critical(f"Config file missing: {str(e)}")
        app.state.status_message = f"Startup failed, {str(e)}"
        raise HTTPException(500, detail="Simulation configuration error")
    except traci.FatalTraCIError as e:
        logger.error(f"TraCI failed: {str(e)}")
        app.state.status_message = f"Startup failed, {str(e)}"
        raise HTTPException(500, detail="TraCI connection failed")



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
    timestep: float = Query(100.0, description="Update interval in milliseconds")
):
    """Run continuous simulation with flow control"""
    app = request.app
    app.state.status_message = "Simulation running"

        # Initialize pause_event if it doesn't exist
    if not hasattr(app.state, "pause_event"):
        app.state.pause_event = asyncio.Event()
        app.state.status_message = "Simulation running"
        app.state.pause_event.set() # Initially running
    
    try:
        while not app.state.pause_event:

            
            start = time.time()
            
            if not app.state.pause_event:
                traci.simulationStep()
                
                # Maintain real-time pacing
                elapsed = (time.time() - start) * 1000  # ms
                sleep_time = max(0, timestep - elapsed) / 1000
                await asyncio.sleep(sleep_time)
            else:
                await asyncio.sleep(0.1)
                
        return {"status": "Simulation stopped"}
    
    except traci.TraCIException as e:
        logger.error(f"TraCI error: {str(e)}")
        raise HTTPException(500, detail="Lost connection to SUMO")
    except Exception as e:
        logger.error(f"Runtime error: {str(e)}")
        raise HTTPException(500, detail="Simulation execution failed")





# pause and resume actions
@sim_router.post("/simulation/pause_simulation", tags=["Simulation"])
async def pause_simulation(request: Request):
    app = request.app

    if not traci.isLoaded():
        return {"status": "Simulation not running"}


    # Toggle pause state of the event
    if app.state.pause_event.is_set():
        app.state.pause_event.clear()  # Pause simulation
        app.state.status_message = "Simulation paused"
        await asyncio.sleep(0.1)  # reduce CPU usage
    else:
        app.state.pause_event.set()  # Resume simulation
        app.state.status_message = "Simulation running"

    return {"message": app.state.status_message, "paused": not app.state.pause_event.is_set()}



@sim_router.get("/simulation/tls_test", tags=["Simulation", "Test"])
async def test_tls_data():
    data = traffic_light_service.get_traffic_lights_data()
    data_aggregate = sensors_service.aggregate_e2_sensor_data_per_edge(),
    sensors_ids = sensors_service.get_sensor_ids()
    return {
        "raw": data,
        "raw_e2_aggregate": data_aggregate,
        "sensors_ids": sensors_ids
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
async def websocket_simulation_ctrl(ws: WebSocket):
    """
    Real-time simulation data channel with dual modes:
    - Training Mode: RL observation space + metrics
    - Simulation Mode: Full traffic system metrics
    """
    await ws.accept()
    app = ws.app
    last_step = -1
    
    try:
        while True:
            current_step = traci.simulation.getTime()
            # Check simulation status
            if not app.state.sumo_pid or not traci.isLoaded():
                await ws.send_json({"error": "Simulation not running"})
                break
            
            # Get current simulation time
            current_time = traci.simulation.getTime()

            if current_time != last_step or app.state.pause_event.is_set():
                response = await _build_websocket_response(app)
                response["paused"] = app.state.pause_event.is_set()
                await ws.send_json(response)
                last_step = current_time
            
            await asyncio.sleep(0.001)

            # if app.state.pause_event.is_set():
            #     await asyncio.sleep(0.1)
            
            # # Only send updates when simulation progresses or pause state changes
            # if current_time != last_step or app.state.pause_event.is_set():
            #     response = await _build_websocket_response(app)
            #     response["paused"] = app.state.pause_event.is_set()
            #     await ws.send_json(response)
            #     last_step = current_time
                
            # # Non-blocking sleep to maintain real-time updates
            # await asyncio.sleep(0)  # Yield control to event loop

    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await ws.close()


    #     _validate_simulation_state(app)
    #     start_time = time.time()
    #     update_interval = time_step / 1000
        
    #     while True:
    #         try:
    #             # Respect pause state
    #             if not app.state.pause_event:
    #                 await asyncio.sleep(0.1)
    #                 continue
                
    #             # Throttle updates
    #             elapsed = time.time() - start_time
    #             if elapsed < update_interval:
    #                 await asyncio.sleep(update_interval - elapsed)
                
    #             # Get fresh data
    #             response = await _build_websocket_response(app)
    #             await ws.send_json(response)
    #             start_time = time.time()
                
    #         except WebSocketDisconnect:
    #             logger.info("Client disconnected")
    #             break
                
    # finally:
    #     await _cleanup_websocket(app, ws)



def _validate_simulation_state(app):
    if not app.state.sumo_pid or not traci_env.is_traci_loaded():
        app.state.status_message = "Simulation not initialized"
        raise HTTPException(
            status_code=400,
            detail=app.state.status_message
        )


async def _build_websocket_response(app) -> dict:
    base_payload = {
        "timestamp": round(time.time(), 3),
        "vehicles": veh_service.get_vehicle_count(),
        "message": app.state.status_message
    }
    
    if app.state.training_mode and app.state.rl_env:
        return WebSocketResponse(
            observation=convert_numpy_to_lists(
                app.state.rl_env.get_observation()
            ),
            **base_payload
        ).model_dump()
    
    return WebSocketResponse(
        traffic_lights=traffic_light_service.get_traffic_lights_data(),
        lanes=lane_service.get_lanes_by_street(),
        e1_sensors=sensors_service.get_e1_sensors_data(),
        e2_sensors=sensors_service.get_e2_sensors_data(),
        e2_aggregated=sensors_service.aggregate_e2_sensor_data_per_edge(),
        **base_payload
    ).model_dump()


async def _cleanup_websocket(app, ws):
    """Graceful websocket disconnection"""
    try:
        await ws.close()
        app.state.ws_connections.discard(ws)
        logger.debug("WebSocket connection closed cleanly")
    except RuntimeError as e:
        logger.warning(f"Cleanup error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected cleanup error: {str(e)}")



### Trafic Lights Control
@sim_router.post("/trafficlights/{tls_id}/phase", tags=["Traffic Lights"])
async def set_traffic_phase(
    tls_id: str,
    phase_index: int = Query(..., ge=0, le=7, example=0),
    duration: Optional[int] = Query(None, gt=0)
):
    try:
        # Validate traffic light exists
        if tls_id not in traci.trafficlight.getIDList():
            raise HTTPException(404, "Traffic light not found")
            
        # Get available phases
        program = traci.trafficlight.getAllProgramLogics(tls_id)[0]
        if phase_index >= len(program.phases):
            raise HTTPException(400, "Invalid phase index")
        
        # Set phase with optional duration
        traci.trafficlight.setPhase(tls_id, phase_index)
        if duration:
            traci.trafficlight.setPhaseDuration(tls_id, duration)
            
        return {
            "status": f"Phase changed to {phase_index}",
            "new_phase": program.phases[phase_index].state,
            "phase_name": traffic_light_service.PHASE_DIRECTIONS.get(phase_index, "Unknown")
        }
        
    except traci.TraCIException as e:
        raise HTTPException(500, f"TraCI error: {str(e)}")
    


@sim_router.get("/lanes/metrics", response_model=Dict[str, lane_service.DirectionMetrics])
async def get_lane_metrics():
    return lane_service.get_detailed_directional_metrics()


@sim_router.get("/trafficlights/{tls_id}/phases")
async def get_phase_information(tls_id: str):
    return traffic_light_service.get_phase_info(tls_id)