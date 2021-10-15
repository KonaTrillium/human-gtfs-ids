from typing import Optional
import zipfile, os, csv, io
from make_gtfs_value_maps import * 
from convert_ids import *
from colors import *
import argparse

class FeedReplacementInfo:
    def __init__(self, field_name: str, values: Dict[str, str], special_field_names: Optional[Dict[str, List[str]]] = None):
        self.field_name = field_name
        self.values = values 
        self.special_field_names = special_field_names

def convert_feed_ids():
    parser = argparse.ArgumentParser(description="Human-Friendly GTFS IDs")
    parser.add_argument('filepath', action='store', type=str, help='Path to GTFS zip.')
    parser.add_argument("--skip-trip-ids", dest="skip_trips", action="store_true", default=False)
    parser.add_argument("--skip-route-ids", dest="skip_routes", action="store_true", default=False)
    parser.add_argument("--skip-service-ids", dest="skip_service", action="store_true", default=False)
    args = parser.parse_args()
    filepath = args.filepath
    if not os.path.isfile(filepath):
        print_red("File does not exist!")
    gtfs_zipped = zipfile.ZipFile(filepath)
    first_stop_times = get_first_stop_times(gtfs_zipped)
    routes = get_routes(gtfs_zipped)
    direction_map = get_directions(gtfs_zipped)
    service_id_map = make_new_service_id_map(gtfs_zipped)
    routeid_map = make_new_routeid_map(gtfs_zipped)
    tripid_map = make_new_tripid_map(gtfs_zipped, first_stop_times, routes, direction_map, service_id_map)
    if len(tripid_map) == 0:
        print_red("No new trip_ids generated! Exiting...")
        exit()
    replacements = []
    if not args.skip_routes:
        replacements.append(FeedReplacementInfo("route_id", routeid_map))
    else:
        print_blue("will NOT replace route_id")
    if not args.skip_service: 
        replacements.append(FeedReplacementInfo("service_id", service_id_map))
    else: 
        print_blue("will NOT replace service_id")
    if not args.skip_trips:
        replacements.append(FeedReplacementInfo("trip_id", tripid_map, {"runcut.txt": ["start_trip_id", "end_trip_id"]}))
    else: 
        print_blue("will NOT replace trip_id")
    if len(replacements) == 0:
        print_red("No replacements selected! Exiting...")
        exit()
    generate_new_files(
        gtfs_zipped, 
        replacements
    )

def generate_new_files(gtfs: zipfile.ZipFile, fields_to_replace: List[FeedReplacementInfo]):
    replacement_field_info : Dict[str, FeedReplacementInfo] = {}
    special_replacement_info : Dict[str, Dict[str, FeedReplacementInfo]] = {}
    for r in fields_to_replace:
        replacement_field_info[r.field_name] = r 
        if r.special_field_names is not None:
            for special_file_name in r.special_field_names.keys():
                if special_file_name not in special_replacement_info:
                    special_replacement_info[special_file_name] = {}
                for special_file_field in r.special_field_names[special_file_name]:
                    special_replacement_info[special_file_name][special_file_field] = r
    for file in gtfs.filelist:
        filename = file.filename
        with gtfs.open(filename) as file_raw:
            file_wrapper = io.TextIOWrapper(file_raw)
            csvfile = csv.DictReader(file_wrapper)
            replacement_values = {}
            for file_field in csvfile.fieldnames:
                if file_field in replacement_field_info:
                    replacement_values[file_field] = replacement_field_info[file_field]
                elif filename in special_replacement_info and file_field in special_replacement_info[filename]:
                    replacement_values[file_field] = special_replacement_info[filename][file_field]
            if len(replacement_values) > 0:
                if os.path.exists(filename):
                    print_red("File with name " + filename + " already exists in directory; cannot create a new one. Move this file and try again. Skipping...")
                    continue
                new_file = open(filename, "w")
                new_csv_writer = csv.DictWriter(new_file, fieldnames=csvfile.fieldnames)
                new_csv_writer.writeheader()
                for row in csvfile:
                    row_copy = row.copy()
                    for field_name in csvfile.fieldnames:
                        if field_name in replacement_values:
                            field_value = row[field_name]
                            if field_value:
                                if field_value in replacement_values[field_name].values:
                                    row_copy[field_name] = replacement_values[field_name].values[field_value]
                                else: 
                                    print_blue("caution: %s %s is not being replaced in %s" % (field_name, field_value, filename))
                    new_csv_writer.writerow(row_copy)
                new_file.close()
                print(COLOR_GREEN + "Exported " + filename + " with every " + ",".join(replacement_values.keys()) + " set to human-readable IDs" + COLOR_RESET)

if __name__ == "__main__":
    convert_feed_ids()