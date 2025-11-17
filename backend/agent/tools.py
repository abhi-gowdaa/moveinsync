from langchain.tools import tool
from sqlalchemy.orm import Session
from Models.DBModels import model as models
from typing import List
import logging

logger = logging.getLogger(__name__)

_db_session = None

def set_db_session(session: Session):
    """Set the database session for tools to use."""
    global _db_session
    _db_session = session
    logger.info("Database session set for tools")


@tool
def get_unassigned_vehicles() -> str:
    """Get all vehicles that are NOT currently assigned to any trip.
    
    Use this when user asks about:
    - "How many vehicles are not assigned?"
    - "Available vehicles"
    - "Free vehicles"
    - "Unassigned vehicles"
    - "Which vehicles can I assign?"
    
    Returns: List of unassigned vehicles with license plate, type, and capacity.
    """
    logger.info("=== TOOL: get_unassigned_vehicles ===")
    
    try:
        if _db_session is None:
            logger.error("Database session is None!")
            return "Error: Database session not initialized."
        
        assigned_vehicle_ids = _db_session.query(models.Deployment.vehicle_id).distinct().all()
        assigned_vehicle_ids = [v[0] for v in assigned_vehicle_ids]
        logger.info(f"Found {len(assigned_vehicle_ids)} assigned vehicles")
        
        unassigned_vehicles = _db_session.query(models.Vehicle).filter(
            ~models.Vehicle.vehicle_id.in_(assigned_vehicle_ids) if assigned_vehicle_ids else True
        ).all()
        
        logger.info(f"Found {len(unassigned_vehicles)} unassigned vehicles")
        
        if not unassigned_vehicles:
            return "No unassigned vehicles found. All vehicles are currently assigned to trips."
        
        result = f"Found {len(unassigned_vehicles)} unassigned vehicle(s):\n\n"
        for v in unassigned_vehicles:
            result += f"• {v.license_plate} - {v.type} (Capacity: {v.capacity} passengers)\n"
        
        logger.info(f"Result: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error in get_unassigned_vehicles: {str(e)}", exc_info=True)
        return f"Error retrieving unassigned vehicles: {str(e)}"


@tool
def get_trip_status(trip_display_name: str) -> str:
    """Get detailed status of a specific trip.
    
    Args:
        trip_display_name: The display name of the trip (e.g., "Bulk - 00:01", "Path Path - 00:02")
    
    Returns: Trip status including booking percentage, live status, assigned vehicle and driver.
    """
    logger.info(f"=== TOOL: get_trip_status for '{trip_display_name}' ===")
    
    try:
        trip = _db_session.query(models.DailyTrip).filter(
            models.DailyTrip.display_name == trip_display_name
        ).first()
        
        if not trip:
            return f"Trip '{trip_display_name}' not found in the system."
        
        result = f" Trip: {trip.display_name}\n"
        result += f" Booking Status: {trip.booking_status_percentage}% booked\n"
        result += f" Live Status: {trip.live_status}\n"
        
        deployment = _db_session.query(models.Deployment).filter(
            models.Deployment.trip_id == trip.trip_id
        ).first()
        
        if deployment:
            vehicle = _db_session.query(models.Vehicle).filter(
                models.Vehicle.vehicle_id == deployment.vehicle_id
            ).first()
            driver = _db_session.query(models.Driver).filter(
                models.Driver.driver_id == deployment.driver_id
            ).first()
            
            if vehicle:
                result += f" Assigned Vehicle: {vehicle.license_plate} ({vehicle.type}, Capacity: {vehicle.capacity})\n"
            if driver:
                result += f"Assigned Driver: {driver.name} ({driver.phone_number})\n"
        else:
            result += " No vehicle or driver assigned to this trip yet.\n"
        
        logger.info(f"Result: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error in get_trip_status: {str(e)}", exc_info=True)
        return f"Error retrieving trip status: {str(e)}"


@tool
def get_path_stops(path_name: str) -> str:
    """Get all stops for a specific path in order.
    
    Args:
        path_name: Name of the path (e.g., "Path-1", "Path-2")
    
    Returns: Ordered list of stops with coordinates.
    """
    logger.info(f"=== TOOL: get_path_stops for '{path_name}' ===")
    
    try:
        path = _db_session.query(models.Path).filter(
            models.Path.path_name == path_name
        ).first()
        
        if not path:
            return f"Path '{path_name}' not found."
        
        path_stops = _db_session.query(models.PathStop, models.Stop).join(
            models.Stop, models.PathStop.stop_id == models.Stop.stop_id
        ).filter(
            models.PathStop.path_id == path.path_id
        ).order_by(models.PathStop.sequence_order).all()
        
        if not path_stops:
            return f"No stops found for path '{path_name}'."
        
        result = f"Stops for '{path_name}' ({len(path_stops)} stops):\n\n"
        for ps, s in path_stops:
            result += f"{ps.sequence_order}. {s.name} (📍 {s.latitude}, {s.longitude})\n"
        
        return result
    
    except Exception as e:
        logger.error(f"Error in get_path_stops: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


@tool
def get_routes_for_path(path_name: str) -> str:
    """Get all routes that use a specific path.
    
    Args:
        path_name: Name of the path
    
    Returns: List of routes using this path.
    """
    logger.info(f"=== TOOL: get_routes_for_path for '{path_name}' ===")
    
    try:
        path = _db_session.query(models.Path).filter(
            models.Path.path_name == path_name
        ).first()
        
        if not path:
            return f"Path '{path_name}' not found."
        
        routes = _db_session.query(models.Route).filter(
            models.Route.path_id == path.path_id
        ).all()
        
        if not routes:
            return f"No routes found for path '{path_name}'."
        
        result = f"Routes using '{path_name}' ({len(routes)} routes):\n\n"
        for r in routes:
            result += f"• {r.route_display_name}\n"
            result += f"  Time: {r.shift_time} | Direction: {r.direction}\n"
            result += f"  {r.start_point} → {r.end_point}\n\n"
        
        return result
    
    except Exception as e:
        logger.error(f"Error in get_routes_for_path: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


@tool
def assign_vehicle_to_trip(vehicle_license_plate: str, driver_name: str, trip_display_name: str) -> str:
    """Assign a vehicle and driver to a trip.
    
    Args:
        vehicle_license_plate: License plate of the vehicle (e.g., "KA-01-1234")
        driver_name: Full name of the driver
        trip_display_name: Display name of the trip (e.g., "Bulk - 00:01")
    
    Returns: Success or error message.
    """
    logger.info(f"=== TOOL: assign_vehicle_to_trip ===")
    logger.info(f"Vehicle: {vehicle_license_plate}, Driver: {driver_name}, Trip: {trip_display_name}")
    
    try:
        vehicle = _db_session.query(models.Vehicle).filter(
            models.Vehicle.license_plate == vehicle_license_plate
        ).first()
        
        if not vehicle:
            return f" Vehicle with license plate '{vehicle_license_plate}' not found."
        
        driver = _db_session.query(models.Driver).filter(
            models.Driver.name == driver_name
        ).first()
        
        if not driver:
            return f" Driver '{driver_name}' not found."
        
        trip = _db_session.query(models.DailyTrip).filter(
            models.DailyTrip.display_name == trip_display_name
        ).first()
        
        if not trip:
            return f" Trip '{trip_display_name}' not found."
        
        existing_deployment = _db_session.query(models.Deployment).filter(
            models.Deployment.vehicle_id == vehicle.vehicle_id
        ).first()
        
        if existing_deployment:
            return f" Vehicle '{vehicle_license_plate}' is already assigned to another trip."
        
        deployment = models.Deployment(
            trip_id=trip.trip_id,
            vehicle_id=vehicle.vehicle_id,
            driver_id=driver.driver_id
        )
        
        _db_session.add(deployment)
        _db_session.commit()
        
        return f" Successfully assigned vehicle '{vehicle_license_plate}' with driver '{driver_name}' to trip '{trip_display_name}'."
    
    except Exception as e:
        logger.error(f"Error in assign_vehicle_to_trip: {str(e)}", exc_info=True)
        _db_session.rollback()
        return f"Error: {str(e)}"


@tool
def remove_vehicle_from_trip(trip_display_name: str) -> str:
    """Remove the assigned vehicle and driver from a trip.
    
     WARNING: This action may have consequences if the trip is booked or in progress.
    The system will check for consequences before executing.
    
    Args:
        trip_display_name: Display name of the trip
    
    Returns: Success or error message.
    """
    logger.info(f"=== TOOL: remove_vehicle_from_trip for '{trip_display_name}' ===")
    
    try:
        trip = _db_session.query(models.DailyTrip).filter(
            models.DailyTrip.display_name == trip_display_name
        ).first()
        
        if not trip:
            return f" Trip '{trip_display_name}' not found."
        
        deployment = _db_session.query(models.Deployment).filter(
            models.Deployment.trip_id == trip.trip_id
        ).first()
        
        if not deployment:
            return f" No vehicle is currently assigned to trip '{trip_display_name}'."
        
        vehicle = _db_session.query(models.Vehicle).filter(
            models.Vehicle.vehicle_id == deployment.vehicle_id
        ).first()
        vehicle_license_plate = vehicle.license_plate if vehicle else "Unknown"
        
        _db_session.delete(deployment)
        _db_session.commit()
        
        return f" Successfully removed vehicle '{vehicle_license_plate}' from trip '{trip_display_name}'."
    
    except Exception as e:
        logger.error(f"Error in remove_vehicle_from_trip: {str(e)}", exc_info=True)
        _db_session.rollback()
        return f"Error: {str(e)}"


@tool
def create_stop(stop_name: str, latitude: float, longitude: float) -> str:
    """Create a new stop location.
    
    Args:
        stop_name: Name of the new stop
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns: Success or error message.
    """
    logger.info(f"=== TOOL: create_stop '{stop_name}' ===")
    
    try:
        existing_stop = _db_session.query(models.Stop).filter(
            models.Stop.name == stop_name
        ).first()
        
        if existing_stop:
            return f" Stop '{stop_name}' already exists at ({existing_stop.latitude}, {existing_stop.longitude})."
        
        new_stop = models.Stop(
            name=stop_name,
            latitude=latitude,
            longitude=longitude
        )
        
        _db_session.add(new_stop)
        _db_session.commit()
        _db_session.refresh(new_stop)
        
        return f" Successfully created stop '{stop_name}' at coordinates ({latitude}, {longitude})."
    
    except Exception as e:
        logger.error(f"Error in create_stop: {str(e)}", exc_info=True)
        _db_session.rollback()
        return f"Error: {str(e)}"


@tool
def create_path(path_name: str, stop_names: List[str]) -> str:
    """Create a new path with an ordered sequence of stops.
    
    Args:
        path_name: Name for the new path
        stop_names: List of stop names in order (e.g., ["Stop A", "Stop B", "Stop C"])
    
    Returns: Success or error message.
    """
    logger.info(f"=== TOOL: create_path '{path_name}' with {len(stop_names)} stops ===")
    
    try:
        existing_path = _db_session.query(models.Path).filter(
            models.Path.path_name == path_name
        ).first()
        
        if existing_path:
            return f" Path '{path_name}' already exists."
        
        stops = _db_session.query(models.Stop).filter(
            models.Stop.name.in_(stop_names)
        ).all()
        
        if len(stops) != len(stop_names):
            found_names = [s.name for s in stops]
            missing_names = [name for name in stop_names if name not in found_names]
            return f" Stops not found: {', '.join(missing_names)}. Please create them first using create_stop."
        
        new_path = models.Path(path_name=path_name)
        _db_session.add(new_path)
        _db_session.commit()
        _db_session.refresh(new_path)
        
        for i, stop_name in enumerate(stop_names):
            stop = next(s for s in stops if s.name == stop_name)
            path_stop = models.PathStop(
                path_id=new_path.path_id,
                stop_id=stop.stop_id,
                sequence_order=i + 1
            )
            _db_session.add(path_stop)
        
        _db_session.commit()
        
        return f" Successfully created path '{path_name}' with {len(stop_names)} stops: {' → '.join(stop_names)}"
    
    except Exception as e:
        logger.error(f"Error in create_path: {str(e)}", exc_info=True)
        _db_session.rollback()
        return f"Error: {str(e)}"


@tool
def get_all_trips() -> str:
    """Get a complete list of all daily trips with their current status.
    
    Use this when user asks about:
    - "Show all trips"
    - "List trips"
    - "What trips do we have?"
    - "Trip overview"
    
    Returns: List of all trips with booking status and live status.
    """
    logger.info("=== TOOL: get_all_trips ===")
    
    try:
        trips = _db_session.query(models.DailyTrip).all()
        
        logger.info(f"Found {len(trips)} trips")
        
        if not trips:
            return "No trips found in the system."
        
        result = f"All Daily Trips ({len(trips)} total):\n\n"
        for t in trips:
            result += f"• {t.display_name}\n"
            result += f"   Booking: {t.booking_status_percentage}%\n"
            result += f"  Status: {t.live_status}\n\n"
        
        logger.info(f"Result: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error in get_all_trips: {str(e)}", exc_info=True)
        return f"Error retrieving trips: {str(e)}"


@tool
def get_vehicle_details(license_plate: str) -> str:
    """Get complete details of a vehicle including assignment status.
    
    Args:
        license_plate: License plate of the vehicle
    
    Returns: Vehicle details and current assignment status.
    """
    logger.info(f"=== TOOL: get_vehicle_details for '{license_plate}' ===")
    
    try:
        vehicle = _db_session.query(models.Vehicle).filter(
            models.Vehicle.license_plate == license_plate
        ).first()
        
        if not vehicle:
            return f" Vehicle with license plate '{license_plate}' not found."
        
        result = f"🚐 Vehicle: {vehicle.license_plate}\n"
        result += f"Type: {vehicle.type}\n"
        result += f"Capacity: {vehicle.capacity} passengers\n\n"
        
        deployment = _db_session.query(models.Deployment).filter(
            models.Deployment.vehicle_id == vehicle.vehicle_id
        ).first()
        
        if deployment:
            trip = _db_session.query(models.DailyTrip).filter(
                models.DailyTrip.trip_id == deployment.trip_id
            ).first()
            if trip:
                result += f" Currently Assigned to: {trip.display_name}\n"
                result += f"   Booking: {trip.booking_status_percentage}% | Status: {trip.live_status}\n"
        else:
            result += " Status: Available (not assigned to any trip)\n"
        
        return result
    
    except Exception as e:
        logger.error(f"Error in get_vehicle_details: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


@tool
def get_driver_details(driver_name: str) -> str:
    """Get complete details of a driver including assignment status.
    
    Args:
        driver_name: Full name of the driver
    
    Returns: Driver details and current assignment status.
    """
    logger.info(f"=== TOOL: get_driver_details for '{driver_name}' ===")
    
    try:
        driver = _db_session.query(models.Driver).filter(
            models.Driver.name == driver_name
        ).first()
        
        if not driver:
            return f" Driver '{driver_name}' not found."
        
        result = f" Driver: {driver.name}\n"
        result += f" Phone: {driver.phone_number}\n\n"
        
        deployment = _db_session.query(models.Deployment).filter(
            models.Deployment.driver_id == driver.driver_id
        ).first()
        
        if deployment:
            trip = _db_session.query(models.DailyTrip).filter(
                models.DailyTrip.trip_id == deployment.trip_id
            ).first()
            if trip:
                result += f" Currently Assigned to: {trip.display_name}\n"
                result += f"   Booking: {trip.booking_status_percentage}% | Status: {trip.live_status}\n"
        else:
            result += " Status: Available (not assigned to any trip)\n"
        
        return result
    
    except Exception as e:
        logger.error(f"Error in get_driver_details: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"


@tool
def create_route(path_name: str, route_display_name: str, shift_time: str, 
                direction: str, start_point: str, end_point: str) -> str:
    """Create a new route for an existing path.
    
    Args:
        path_name: Name of the path to use
        route_display_name: Display name for the route
        shift_time: Shift time (e.g., '08:00 AM')
        direction: Direction ('LOGIN' or 'LOGOUT')
        start_point: Starting location name
        end_point: Ending location name
    
    Returns: Success or error message.
    """
    logger.info(f"=== TOOL: create_route '{route_display_name}' ===")
    
    try:
        path = _db_session.query(models.Path).filter(
            models.Path.path_name == path_name
        ).first()
        
        if not path:
            return f" Path '{path_name}' not found. Please create the path first."
        
        new_route = models.Route(
            path_id=path.path_id,
            route_display_name=route_display_name,
            shift_time=shift_time,
            direction=direction,
            start_point=start_point,
            end_point=end_point
        )
        
        _db_session.add(new_route)
        _db_session.commit()
        _db_session.refresh(new_route)
        
        return f" Successfully created route '{route_display_name}' for path '{path_name}'\n   Time: {shift_time} | Direction: {direction} | {start_point} → {end_point}"
    
    except Exception as e:
        logger.error(f"Error in create_route: {str(e)}", exc_info=True)
        _db_session.rollback()
        return f"Error: {str(e)}"


@tool
def get_all_stops() -> str:
    """Get a list of ALL stops in the system.
    
    Use this tool BEFORE creating a new stop to check if it already exists.
    
    Returns: Complete list of all stops with their coordinates.
    """
    logger.info("=== TOOL: get_all_stops ===")
    
    try:
        if _db_session is None:
            return "Error: Database session not initialized."
        
        stops = _db_session.query(models.Stop).all()
        
        if not stops:
            return "No stops found in the system. You can create new stops."
        
        result = f"Found {len(stops)} stop(s) in the system:\n\n"
        for stop in stops:
            result += f"• {stop.name} - ({stop.latitude}, {stop.longitude})\n"
        
        logger.info(f"Returned {len(stops)} stops")
        return result
    
    except Exception as e:
        logger.error(f"Error in get_all_stops: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

# List of all tools
TOOLS = [
    get_unassigned_vehicles,
    get_trip_status,
    get_path_stops,
    get_routes_for_path,
    assign_vehicle_to_trip,
    remove_vehicle_from_trip,
    create_stop,
    create_path,
    get_all_trips,
    get_vehicle_details,
    get_driver_details,
    create_route,
    get_all_stops
]