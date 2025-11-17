
from pydantic import BaseModel
from typing import List, Optional

# Base schemas
class StopBase(BaseModel):
    name: str
    latitude: float
    longitude: float

class StopCreate(StopBase):
    pass

class Stop(StopBase):
    stop_id: int
    
    class Config:
        orm_mode = True

class PathStopBase(BaseModel):
    stop_id: int
    sequence_order: int

class PathStopCreate(PathStopBase):
    pass

class PathStop(PathStopBase):
    id: int
    path_id: int
    
    class Config:
        orm_mode = True

class PathBase(BaseModel):
    path_name: str

class PathCreate(PathBase):
    stops: List[PathStopCreate] = []

class Path(PathBase):
    path_id: int
    stops: List[PathStop] = []
    
    class Config:
        orm_mode = True

class RouteBase(BaseModel):
    path_id: int
    route_display_name: str
    shift_time: str
    direction: str
    start_point: str
    end_point: str
    status: str = "active"

class RouteCreate(RouteBase):
    pass

class RouteUpdate(BaseModel):
    route_display_name: Optional[str] = None
    shift_time: Optional[str] = None
    direction: Optional[str] = None
    start_point: Optional[str] = None
    end_point: Optional[str] = None
    status: Optional[str] = None

class Route(RouteBase):
    route_id: int
    
    class Config:
        orm_mode = True

class VehicleBase(BaseModel):
    license_plate: str
    type: str
    capacity: int

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    vehicle_id: int
    
    class Config:
        orm_mode = True

class DriverBase(BaseModel):
    name: str
    phone_number: str

class DriverCreate(DriverBase):
    pass

class Driver(DriverBase):
    driver_id: int
    
    class Config:
        orm_mode = True

class DailyTripBase(BaseModel):
    route_id: int
    display_name: str
    booking_status_percentage: int = 0
    live_status: str = "Scheduled"

class DailyTripCreate(DailyTripBase):
    pass

class DailyTrip(DailyTripBase):
    trip_id: int
    
    class Config:
        orm_mode = True

class DeploymentBase(BaseModel):
    trip_id: int
    vehicle_id: int
    driver_id: int

class DeploymentCreate(DeploymentBase):
    pass

class Deployment(DeploymentBase):
    deployment_id: int
    
    class Config:
        orm_mode = True