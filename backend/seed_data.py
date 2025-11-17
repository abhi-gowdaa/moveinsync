stops_data = [
    {"stop_id": 1, "name": "Gavipuram", "latitude": 12.9501, "longitude": 77.5667},
    {"stop_id": 2, "name": "Peenya", "latitude": 13.0212, "longitude": 77.5113},
    {"stop_id": 3, "name": "Temple", "latitude": 12.9610, "longitude": 77.6012},
    {"stop_id": 4, "name": "BTM", "latitude": 12.9155, "longitude": 77.6101},
    {"stop_id": 5, "name": "NoShow", "latitude": 12.9000, "longitude": 77.5800},
]


paths_data = [
    {"path_id": 1, "path_name": "Path1"},
    {"path_id": 2, "path_name": "Path2"},
    {"path_id": 3, "path_name": "PathPath"},
    {"path_id": 4, "path_name": "Bulk"},
    {"path_id": 5, "path_name": "Geoone"},
    {"path_id": 6, "path_name": "AVX"},
    {"path_id": 7, "path_name": "NoShow-BTS"},
    {"path_id": 8, "path_name": "Paradise"},
    {"path_id": 9, "path_name": "Dice"},
]

path_stops_data = [
    {"path_id": 1, "stop_id": 1, "sequence_order": 1},
    {"path_id": 1, "stop_id": 3, "sequence_order": 2},
    {"path_id": 2, "stop_id": 1, "sequence_order": 1},
    {"path_id": 2, "stop_id": 2, "sequence_order": 2},
    {"path_id": 3, "stop_id": 1, "sequence_order": 1},
    {"path_id": 3, "stop_id": 2, "sequence_order": 2},
    {"path_id": 4, "stop_id": 1, "sequence_order": 1},
    {"path_id": 4, "stop_id": 3, "sequence_order": 2},
    {"path_id": 5, "stop_id": 2, "sequence_order": 1},
    {"path_id": 5, "stop_id": 3, "sequence_order": 2},
    {"path_id": 6, "stop_id": 4, "sequence_order": 1},
    {"path_id": 6, "stop_id": 5, "sequence_order": 2},
    {"path_id": 7, "stop_id": 4, "sequence_order": 1},
    {"path_id": 7, "stop_id": 5, "sequence_order": 2},
    {"path_id": 8, "stop_id": 4, "sequence_order": 1},
    {"path_id": 8, "stop_id": 5, "sequence_order": 2},
    {"path_id": 9, "stop_id": 4, "sequence_order": 1},
    {"path_id": 9, "stop_id": 5, "sequence_order": 2},
]

routes_data = [
    {"route_id": 1, "path_id": 1, "route_display_name": "Path1-2100", "shift_time": "21:00", "direction": "LOGIN", "start_point": "Gavipuram", "end_point": "Temple"},
    {"route_id": 2, "path_id": 2, "route_display_name": "Path2-1945", "shift_time": "19:45", "direction": "LOGIN", "start_point": "Gavipuram", "end_point": "Peenya"},
    {"route_id": 3, "path_id": 2, "route_display_name": "Path2-2300", "shift_time": "23:00", "direction": "LOGIN", "start_point": "Gavipuram", "end_point": "Peenya"},
    {"route_id": 4, "path_id": 3, "route_display_name": "PathPath-0010", "shift_time": "00:10", "direction": "LOGIN", "start_point": "Gavipuram", "end_point": "Peenya"},
    {"route_id": 5, "path_id": 4, "route_display_name": "Bulk-0001", "shift_time": "00:01", "direction": "LOGIN", "start_point": "Hongsandra", "end_point": "Temple"},
    {"route_id": 6, "path_id": 5, "route_display_name": "Geoone-0059", "shift_time": "00:59", "direction": "LOGIN", "start_point": "BTM", "end_point": "Temple"},
    {"route_id": 7, "path_id": 6, "route_display_name": "AVX-0515", "shift_time": "05:15", "direction": "LOGIN", "start_point": "BTM", "end_point": "Temple"},
    {"route_id": 8, "path_id": 7, "route_display_name": "NoShow-BTS-1300", "shift_time": "13:00", "direction": "LOGIN", "start_point": "BTM", "end_point": "NoShow"},
]

vehicles_data = [
    {"vehicle_id": 1, "license_plate": "KA01AB1234", "type": "Cab", "capacity": 4},
    {"vehicle_id": 2, "license_plate": "KA05MN5678", "type": "Bus", "capacity": 30},
    {"vehicle_id": 3, "license_plate": "KA03XY4321", "type": "Cab", "capacity": 4},
    {"vehicle_id": 4, "license_plate": "KA11GH7890", "type": "Bus", "capacity": 40},
]

drivers_data = [
    {"driver_id": 1, "name": "Ramesh", "phone_number": "9876543210"},
    {"driver_id": 2, "name": "Suresh", "phone_number": "9988776655"},
    {"driver_id": 3, "name": "Amit", "phone_number": "9123456789"},
    {"driver_id": 4, "name": "Kiran", "phone_number": "9345678901"},
]

daily_trips_data = [
    {"trip_id": 1, "route_id": 5, "display_name": "Bulk-0001", "booking_status_percentage": 0, "live_status": "00:01 IN"},
    {"trip_id": 2, "route_id": 4, "display_name": "Path Path-0002", "booking_status_percentage": 0, "live_status": "00:02 IN"},
    {"trip_id": 3, "route_id": 4, "display_name": "Path Path-0010", "booking_status_percentage": 0, "live_status": "00:10 IN"},
    {"trip_id": 4, "route_id": 6, "display_name": "Geoone-0059", "booking_status_percentage": 0, "live_status": "00:59 OUT"},
    {"trip_id": 5, "route_id": 7, "display_name": "AVX-0515", "booking_status_percentage": 0, "live_status": "05:15 IN"},
    {"trip_id": 6, "route_id": 8, "display_name": "NoShow-BTS-1300", "booking_status_percentage": 50, "live_status": "13:00 IN"},
]

deployments_data = [
    {"deployment_id": 1, "trip_id": 2, "vehicle_id": 1, "driver_id": 3},
    {"deployment_id": 2, "trip_id": 3, "vehicle_id": 2, "driver_id": 1},
    {"deployment_id": 3, "trip_id": 5, "vehicle_id": 4, "driver_id": 2},
]


from sqlalchemy.orm import Session
from Models.DBModels import model as models

def seed_data(db: Session):
    db.bulk_insert_mappings(models.Stop, stops_data)
    db.bulk_insert_mappings(models.Path, paths_data)
    db.bulk_insert_mappings(models.PathStop, path_stops_data)
    db.bulk_insert_mappings(models.Route, routes_data)
    db.bulk_insert_mappings(models.Vehicle, vehicles_data)
    db.bulk_insert_mappings(models.Driver, drivers_data)
    db.bulk_insert_mappings(models.DailyTrip, daily_trips_data)
    db.bulk_insert_mappings(models.Deployment, deployments_data)
    db.commit()
    

if __name__ == "__main__":
    from Service.DBService.database import SessionLocal, engine
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_data(db)
    db.close()
