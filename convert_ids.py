import csv, io
from typing import List, Dict 
from colors import *

# This file contains methods for generating maps of old IDs to new IDs. 

def make_new_tripid_map(gtfs, first_stop_times: Dict[str, List], routes: Dict[str, List], directions: Dict[str, List[str]], new_service_ids: Dict[str, str]):
    trip_id_map = {}
    with gtfs.open("trips.txt", "r") as trips_file_raw:
        trips_file = io.TextIOWrapper(trips_file_raw)
        trips_csv = csv.DictReader(trips_file)
        route_direction_counts = {}
        trips = list(trips_csv)
        sorted_trips = sorted(trips, key=lambda k: (k['block_id'], k['service_id'], first_stop_times[k['trip_id']]['departure_time']))
        for row in sorted_trips:
            route_info = routes[row['route_id']]
            route_name = route_info['route_short_name'] or route_info['route_long_name']
            if not route_name:
                print_red("A route name could not be found for trip ID %s, exiting..." % (row['trip_id'], ))
            direction = row['direction_id']
            service_id = new_service_ids[row['service_id']]
            route_direction_key = route_name + direction + row['block_id'] + service_id
            if route_direction_key not in route_direction_counts:
                route_direction_counts[route_direction_key] = 0
            route_direction_counts[route_direction_key] += 1
            count = route_direction_counts[route_direction_key]
            direction_name = directions[row['route_id']][int(direction)] or direction
            first_time = first_stop_times[row['trip_id']]['departure_time']
            time = ":".join(first_time.split(":")[:2])
            # This is where the new trip ID comes together
            new_trip_id = route_name + "_" + direction_name + "-" + service_id + "_" + str(count) + "_" + time
            new_trip_id = new_trip_id.replace(" ", "-")
            if new_trip_id in trip_id_map:
                print_red("Generated trip ID " + new_trip_id + " has already been created! Second original trip_id is " + row['trip_id'] + ". Will not create duplicates. Exiting...")
                exit()
            trip_id_map[row['trip_id']] = new_trip_id
    return trip_id_map

def make_new_service_id_map(gtfs):
    new_id_components = []
    service_ids_seen_in_main_cal = set()
    with gtfs.open("calendar.txt") as cal_file_raw:
        cal_file = io.TextIOWrapper(cal_file_raw)
        cal_csv = csv.DictReader(cal_file)
        day_fields_and_abbrv = [("monday", "M"), ("tuesday", "T"), ("wednesday", "W"), ("thursday", "R"), ("friday", "F"), ("saturday", "Sa"), ("sunday", "Su")]
        for row in cal_csv:
            days = ""
            for day_name in day_fields_and_abbrv:
                if row[day_name[0]] == "1":
                    days += day_name[1]
            if not days:
                days = "x" 
            elif days == "MTWRF":
                days = "wkdy"
            elif days == "SaSu":
                days = "wknd"
            elif days == "MTWRFSaSu":
                days = "daily"
            new_id_components.append((row['service_id'], days, row['start_date'], row['end_date']))   
            service_ids_seen_in_main_cal.add(row['service_id']) 

    with gtfs.open("calendar_dates.txt") as dates_file_raw:
        dates_file = io.TextIOWrapper(dates_file_raw)
        dates_csv = csv.DictReader(dates_file)
        seen_exception_only_ids = set()
        for row in dates_csv:
            service_id = row['service_id']
            if service_id not in service_ids_seen_in_main_cal and service_id not in seen_exception_only_ids:
                new_id_components.append((service_id, "", row['date']))
                seen_exception_only_ids.add(service_id)
    
    service_id_map = {}
    seen_day_groups = [g for g in map(lambda k: k[1]+k[2]+k[3] if k[1] else None, new_id_components) if g]
    created_service_ids = set()
    for comp in new_id_components:
        if comp[0] in service_id_map:
            print_red("Attempted to modify service ID %s twice, exiting" % comp[0])
            exit()
        day_group = comp[1]
        # New service IDs come together below. This is a little more complex to allow certain flexibilities. 
        # It's ugly, sensitive, and not very readable, so be careful. 
        if day_group:
            appearances = len([g for g in seen_day_groups if g.startswith(day_group)])
            if appearances > 1:
                new_id = comp[1] + "-" + comp[2] + "-" + comp[3]
            else: 
                new_id = comp[1]
        else: 
            new_id = comp[2]
        while new_id in created_service_ids:
            new_id += "a"
        else:
            created_service_ids.add(new_id)
        service_id_map[comp[0]] = new_id
    return service_id_map

def make_new_routeid_map(gtfs):
    output_ids = {}
    with gtfs.open("routes.txt") as file_raw:
        file_wrapper = io.TextIOWrapper(file_raw)
        file_csv = csv.DictReader(file_wrapper)
        for route in file_csv:
            new_id = route['route_short_name'] or route['route_long_name']
            new_id = new_id.replace(" ", "").replace("&", "-")
            if new_id in output_ids:
                new_id = new_id + "-" + route['agency_id']
            if new_id in output_ids:
                print_red("created duplicate route_id %s" % new_id)
                exit()
            output_ids[route['route_id']] = new_id
    return output_ids
