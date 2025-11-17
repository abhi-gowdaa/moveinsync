# Add these endpoints to your app.py (or create a separate routes.py)

from fastapi import FastAPI, Depends, HTTPException, Query,APIRouter
from sqlalchemy.orm import Session, joinedload
from Service.DBService.database import get_db
from Models.DBModels import model as models
from typing import List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# ============================================
# Pydantic Response Models
# ============================================
router = APIRouter()

class VehicleResponse(BaseModel):
    vehicle_id: int
    license_plate: str
    type: str
    capacity: int
    is_assigned: bool = False
    
    class Config:
        from_attributes = True

class DriverResponse(BaseModel):
    driver_id: int
    name: str
    phone_number: str
    
    class Config:
        from_attributes = True

class DeploymentResponse(BaseModel):
    deployment_id: int
    vehicle: VehicleResponse
    driver: DriverResponse
    
    class Config:
        from_attributes = True

class TripResponse(BaseModel):
    trip_id: int
    display_name: str
    booking_status_percentage: int
    live_status: str
    route_id: int
    deployment: Optional[DeploymentResponse] = None
    
    class Config:
        from_attributes = True

class StopResponse(BaseModel):
    stop_id: int
    name: str
    latitude: float
    longitude: float
    
    class Config:
        from_attributes = True

class PathStopResponse(BaseModel):
    sequence_order: int
    stop: StopResponse
    
    class Config:
        from_attributes = True

class RouteResponse(BaseModel):
    route_id: int
    route_display_name: str
    shift_time: str
    direction: str
    start_point: str
    end_point: str
    status: str
    path_id: int
    capacity: Optional[int] = None
    allowed_waitlist: Optional[int] = None
    
    class Config:
        from_attributes = True

class RouteDetailResponse(RouteResponse):
    path_stops: List[PathStopResponse] = []
    trips: List[TripResponse] = []

class DashboardStatsResponse(BaseModel):
    total_trips: int
    vehicles_not_assigned: int
    trips_not_assigned: int
    employees_scheduled: int
    ongoing_trips: int
    total_vehicles: int
    total_routes: int
    total_drivers: int

# ============================================
# TRIPS ENDPOINTS
# ============================================

@router.get("/api/trips/", response_model=List[TripResponse])
async def get_all_trips(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all daily trips with optional status filter.
    
    Query params:
    - status: Filter by live_status (e.g., "Scheduled", "00:01 IN")
    """
    try:
        query = db.query(models.DailyTrip).options(
            joinedload(models.DailyTrip.deployments).joinedload(models.Deployment.vehicle),
            joinedload(models.DailyTrip.deployments).joinedload(models.Deployment.driver)
        )
        
        if status:
            query = query.filter(models.DailyTrip.live_status == status)
        
        trips = query.all()
        
        # Transform to response format
        result = []
        for trip in trips:
            trip_data = {
                "trip_id": trip.trip_id,
                "display_name": trip.display_name,
                "booking_status_percentage": trip.booking_status_percentage,
                "live_status": trip.live_status,
                "route_id": trip.route_id,
                "deployment": None
            }
            
            # Add deployment info if exists
            if trip.deployments:
                deployment = trip.deployments[0]  # Assuming one deployment per trip
                trip_data["deployment"] = {
                    "deployment_id": deployment.deployment_id,
                    "vehicle": {
                        "vehicle_id": deployment.vehicle.vehicle_id,
                        "license_plate": deployment.vehicle.license_plate,
                        "type": deployment.vehicle.type,
                        "capacity": deployment.vehicle.capacity,
                        "is_assigned": True
                    },
                    "driver": {
                        "driver_id": deployment.driver.driver_id,
                        "name": deployment.driver.name,
                        "phone_number": deployment.driver.phone_number
                    }
                }
            
            result.append(trip_data)
        
        logger.info(f"Returned {len(result)} trips")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching trips: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/trips/{trip_id}", response_model=TripResponse)
async def get_trip_by_id(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific trip by ID with deployment details."""
    try:
        trip = db.query(models.DailyTrip).options(
            joinedload(models.DailyTrip.deployments).joinedload(models.Deployment.vehicle),
            joinedload(models.DailyTrip.deployments).joinedload(models.Deployment.driver)
        ).filter(models.DailyTrip.trip_id == trip_id).first()
        
        if not trip:
            raise HTTPException(status_code=404, detail=f"Trip {trip_id} not found")
        
        trip_data = {
            "trip_id": trip.trip_id,
            "display_name": trip.display_name,
            "booking_status_percentage": trip.booking_status_percentage,
            "live_status": trip.live_status,
            "route_id": trip.route_id,
            "deployment": None
        }
        
        if trip.deployments:
            deployment = trip.deployments[0]
            trip_data["deployment"] = {
                "deployment_id": deployment.deployment_id,
                "vehicle": {
                    "vehicle_id": deployment.vehicle.vehicle_id,
                    "license_plate": deployment.vehicle.license_plate,
                    "type": deployment.vehicle.type,
                    "capacity": deployment.vehicle.capacity,
                    "is_assigned": True
                },
                "driver": {
                    "driver_id": deployment.driver.driver_id,
                    "name": deployment.driver.name,
                    "phone_number": deployment.driver.phone_number
                }
            }
        
        return trip_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trip {trip_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ROUTES ENDPOINTS
# ============================================

@router.get("/api/routes/", response_model=List[RouteResponse])
async def get_all_routes(
    status: Optional[str] = "active",
    db: Session = Depends(get_db)
):
    """
    Get all routes with optional status filter.
    
    Query params:
    - status: Filter by status ("active", "deactivated", or null for all)
    """
    try:
        query = db.query(models.Route)
        
        if status:
            query = query.filter(models.Route.status == status)
        
        routes = query.all()
        
        result = []
        for route in routes:
            result.append({
                "route_id": route.route_id,
                "route_display_name": route.route_display_name,
                "shift_time": route.shift_time,
                "direction": route.direction,
                "start_point": route.start_point,
                "end_point": route.end_point,
                "status": route.status,
                "path_id": route.path_id,
                "capacity": 0,  # You can calculate from path/vehicle
                "allowed_waitlist": 0
            })
        
        logger.info(f"Returned {len(result)} routes")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching routes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/routes/{route_id}", response_model=RouteDetailResponse)
async def get_route_by_id(
    route_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific route with path stops and trips."""
    try:
        route = db.query(models.Route).options(
            joinedload(models.Route.path).joinedload(models.Path.stops).joinedload(models.PathStop.stop),
            joinedload(models.Route.trips)
        ).filter(models.Route.route_id == route_id).first()
        
        if not route:
            raise HTTPException(status_code=404, detail=f"Route {route_id} not found")
        
        # Build path stops
        path_stops = []
        if route.path and route.path.stops:
            sorted_stops = sorted(route.path.stops, key=lambda x: x.sequence_order)
            for path_stop in sorted_stops:
                path_stops.append({
                    "sequence_order": path_stop.sequence_order,
                    "stop": {
                        "stop_id": path_stop.stop.stop_id,
                        "name": path_stop.stop.name,
                        "latitude": path_stop.stop.latitude,
                        "longitude": path_stop.stop.longitude
                    }
                })
        
        # Build trips
        trips = []
        for trip in route.trips:
            trips.append({
                "trip_id": trip.trip_id,
                "display_name": trip.display_name,
                "booking_status_percentage": trip.booking_status_percentage,
                "live_status": trip.live_status,
                "route_id": trip.route_id,
                "deployment": None
            })
        
        result = {
            "route_id": route.route_id,
            "route_display_name": route.route_display_name,
            "shift_time": route.shift_time,
            "direction": route.direction,
            "start_point": route.start_point,
            "end_point": route.end_point,
            "status": route.status,
            "path_id": route.path_id,
            "capacity": 0,
            "allowed_waitlist": 0,
            "path_stops": path_stops,
            "trips": trips
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching route {route_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# VEHICLES ENDPOINTS
# ============================================

@router.get("/api/vehicles/", response_model=List[VehicleResponse])
async def get_all_vehicles(db: Session = Depends(get_db)):
    """Get all vehicles with assignment status."""
    try:
        vehicles = db.query(models.Vehicle).all()
        
        # Get assigned vehicle IDs
        assigned_ids = db.query(models.Deployment.vehicle_id).distinct().all()
        assigned_ids = [v[0] for v in assigned_ids]
        
        result = []
        for vehicle in vehicles:
            result.append({
                "vehicle_id": vehicle.vehicle_id,
                "license_plate": vehicle.license_plate,
                "type": vehicle.type,
                "capacity": vehicle.capacity,
                "is_assigned": vehicle.vehicle_id in assigned_ids
            })
        
        logger.info(f"Returned {len(result)} vehicles")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching vehicles: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/vehicles/unassigned", response_model=List[VehicleResponse])
async def get_unassigned_vehicles(db: Session = Depends(get_db)):
    """Get only unassigned vehicles."""
    try:
        assigned_ids = db.query(models.Deployment.vehicle_id).distinct().all()
        assigned_ids = [v[0] for v in assigned_ids]
        
        vehicles = db.query(models.Vehicle).filter(
            ~models.Vehicle.vehicle_id.in_(assigned_ids) if assigned_ids else True
        ).all()
        
        result = []
        for vehicle in vehicles:
            result.append({
                "vehicle_id": vehicle.vehicle_id,
                "license_plate": vehicle.license_plate,
                "type": vehicle.type,
                "capacity": vehicle.capacity,
                "is_assigned": False
            })
        
        logger.info(f"Returned {len(result)} unassigned vehicles")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching unassigned vehicles: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle_by_id(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific vehicle by ID."""
    try:
        vehicle = db.query(models.Vehicle).filter(
            models.Vehicle.vehicle_id == vehicle_id
        ).first()
        
        if not vehicle:
            raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")
        
        # Check if assigned
        is_assigned = db.query(models.Deployment).filter(
            models.Deployment.vehicle_id == vehicle_id
        ).first() is not None
        
        return {
            "vehicle_id": vehicle.vehicle_id,
            "license_plate": vehicle.license_plate,
            "type": vehicle.type,
            "capacity": vehicle.capacity,
            "is_assigned": is_assigned
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vehicle {vehicle_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# DRIVERS ENDPOINTS
# ============================================

@router.get("/api/drivers/", response_model=List[DriverResponse])
async def get_all_drivers(db: Session = Depends(get_db)):
    """Get all drivers."""
    try:
        drivers = db.query(models.Driver).all()
        
        result = []
        for driver in drivers:
            result.append({
                "driver_id": driver.driver_id,
                "name": driver.name,
                "phone_number": driver.phone_number
            })
        
        logger.info(f"Returned {len(result)} drivers")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching drivers: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# STOPS ENDPOINTS
# ============================================

@router.get("/api/stops/", response_model=List[StopResponse])
async def get_all_stops(db: Session = Depends(get_db)):
    """Get all stops."""
    try:
        stops = db.query(models.Stop).all()
        
        result = []
        for stop in stops:
            result.append({
                "stop_id": stop.stop_id,
                "name": stop.name,
                "latitude": stop.latitude,
                "longitude": stop.longitude
            })
        
        logger.info(f"Returned {len(result)} stops")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching stops: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# DASHBOARD STATS ENDPOINT
# ============================================

@router.get("/api/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics for overview."""
    try:
        # Total trips
        total_trips = db.query(models.DailyTrip).count()
        
        # Vehicles not assigned
        assigned_vehicle_ids = db.query(models.Deployment.vehicle_id).distinct().all()
        assigned_vehicle_ids = [v[0] for v in assigned_vehicle_ids]
        total_vehicles = db.query(models.Vehicle).count()
        vehicles_not_assigned = total_vehicles - len(assigned_vehicle_ids)
        
        # Trips not assigned
        assigned_trip_ids = db.query(models.Deployment.trip_id).distinct().all()
        trips_not_assigned = total_trips - len(assigned_trip_ids)
        
        # Ongoing trips (trips with status containing "IN")
        ongoing_trips = db.query(models.DailyTrip).filter(
            models.DailyTrip.live_status.like("%IN%")
        ).count()
        
        # Total routes
        total_routes = db.query(models.Route).filter(
            models.Route.status == "active"
        ).count()
        
        # Total drivers
        total_drivers = db.query(models.Driver).count()
        
        # Employees scheduled (sum of booking percentages / 100 * capacity)
        # This is a simplified calculation
        trips_with_booking = db.query(models.DailyTrip).all()
        employees_scheduled = sum(
            trip.booking_status_percentage for trip in trips_with_booking
        ) // 10  # Rough estimate
        
        result = {
            "total_trips": total_trips,
            "vehicles_not_assigned": vehicles_not_assigned,
            "trips_not_assigned": trips_not_assigned,
            "employees_scheduled": employees_scheduled,
            "ongoing_trips": ongoing_trips,
            "total_vehicles": total_vehicles,
            "total_routes": total_routes,
            "total_drivers": total_drivers
        }
        
        logger.info(f"Dashboard stats: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))