
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from Service.DBService.database import Base
from sqlalchemy.orm import relationship

 

class Stop(Base):
    __tablename__ = "stops"
    
    stop_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    path_stops = relationship("PathStop", back_populates="stop")

class Path(Base):
    __tablename__ = "paths"
    
    path_id = Column(Integer, primary_key=True, index=True)
    path_name = Column(String, unique=True, index=True)
    
    # Relationships
    stops = relationship("PathStop", back_populates="path")
    routes = relationship("Route", back_populates="path")
 
class PathStop(Base):
    __tablename__ = "path_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("paths.path_id"))
    stop_id = Column(Integer, ForeignKey("stops.stop_id"))
    sequence_order = Column(Integer)
    
    # Relationships
    path = relationship("Path", back_populates="stops")
    stop = relationship("Stop", back_populates="path_stops")

class Route(Base):
    __tablename__ = "routes"
    
    route_id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("paths.path_id"))
    route_display_name = Column(String, index=True)
    shift_time = Column(String)
    direction = Column(String, default="LOGIN")  # e.g., "up", "down"
    start_point = Column(String)
    end_point = Column(String)
    status = Column(String, default="active")  # "active", "deactivated"
    
    # Relationships
    path = relationship("Path", back_populates="routes")
    trips = relationship("DailyTrip", back_populates="route")

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    vehicle_id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True, index=True)
    type = Column(String)  # "Bus", "Cab"
    capacity = Column(Integer)
    
    # Relationships
    deployments = relationship("Deployment", back_populates="vehicle")

class Driver(Base):
    __tablename__ = "drivers"
    
    driver_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String)
    
    # Relationships
    deployments = relationship("Deployment", back_populates="driver")

class DailyTrip(Base):
    __tablename__ = "daily_trips"
    
    trip_id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.route_id"))
    display_name = Column(String, index=True)
    booking_status_percentage = Column(Integer, default=0)
    live_status = Column(String, default="Scheduled")  # e.g., "00:01 IN", "Scheduled"
    
    # Relationships
    route = relationship("Route", back_populates="trips")
    deployments = relationship("Deployment", back_populates="trip")

class Deployment(Base):
    __tablename__ = "deployments"
    
    deployment_id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("daily_trips.trip_id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.vehicle_id"))
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"))
    
    # Relationships
    trip = relationship("DailyTrip", back_populates="deployments")
    vehicle = relationship("Vehicle", back_populates="deployments")
    driver = relationship("Driver", back_populates="deployments")