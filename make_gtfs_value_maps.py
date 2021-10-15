import io, zipfile, csv
from typing import Dict, List 

def get_first_stop_times(gtfs: zipfile.ZipFile) -> Dict[str, List]:
    """Returns a dictionary. Key: `trip_id` from GTFS. Value: Dictionary for entry with lowest `stop_sequence` for that trip in stop_times.txt"""
    with gtfs.open('stop_times.txt') as file_raw:
        wrapper = io.TextIOWrapper(file_raw)
        times_csv = csv.DictReader(wrapper)
        result : Dict[str, dict] = {}
        for row in times_csv:
            trip_id = row['trip_id']
            if trip_id not in result or row['stop_sequence'] < result[trip_id]['stop_sequence']:
                result[trip_id] = row 
        return result 

def get_routes(gtfs: zipfile.ZipFile) -> Dict[str, List]:
    """Returns a dictionary. Key: `route_id` from GTFS. Value: Dictionary for entry for that `route_id`."""
    with gtfs.open('routes.txt') as file_raw:
        wrapper = io.TextIOWrapper(file_raw)
        times_csv = csv.DictReader(wrapper)
        result : Dict[str, dict] = {}
        for row in times_csv:
            route_id = row['route_id']
            result[route_id] = row 
        return result 

def get_directions(gtfs: zipfile.ZipFile) -> Dict[str, List[str]]:
    """Returns a dictionary. Key: `route_id` from GTFS. Value: List with two values naming directions 0 and 1 for that route."""
    with gtfs.open('directions.txt') as file_raw:
        wrapper = io.TextIOWrapper(file_raw)
        times_csv = csv.DictReader(wrapper)
        result : Dict[str, List[str]] = {}
        for row in times_csv:
            route_id = row['route_id']
            direction_id = row['direction_id']
            direction = row['direction']
            if route_id not in result:
                result[route_id] = [None, None]
            result[route_id][int(direction_id)] = direction
        return result 