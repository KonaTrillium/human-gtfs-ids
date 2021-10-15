# Human-Friendly GTFS IDs
This script is designed to convert GTFS IDs into human-readable, sensible IDs, instead of random numbers and/or letters. It has been tested only against GTFS feeds exported from Trillium's GTFS Manager software, but theoretically should work on any feed. 

Requires Python 3, tested and developed on 3.9.

## Usage 
- Clone this repo. 
- Run `python3 humanids.py /path/to/gtfs.zip`
- Modified files will export to current directory. 

## Files
- `humanids.py` contains the main execution logic. This is where you call methods to get dicts of new IDs and export new files. Send this info in a `FeedReplacementInfo` object, along with the field name to search for in every file, and any unique field names specific to certain files. 
- `convert_ids.py` makes the maps of old IDs to new IDs. If you wish to modify the format of generated IDs, this is the place to do so. Take care to ensure uniqueness.
- `make_gtfs_value_maps.py` contains functions to convert values from a provided GTFS zip to Python dictionaries for easy access. 
- `colors.py` is helpful for printing output in colors. 

## Implementation notes
- `service_id` will become the days of week served and, if needed, the service period it applies to. 
  - Sometimes, this will produce two of the same identifiers. The letter `a` will be appended until the ID is unique. 
  - Replacement values are made based on the values present in `calendar.txt` and `calendar_dates.txt`. Sometimes, a service ID can be found in other files not present in these two; these IDs will not be altered (and should have no bearing on the actual scheduling anyway).
    - If a `service_id` is only found in `calendar_dates.txt` (i.e. it's an exception-only ID), the ID will become _the date that it first appeared in the file_. For Trillium's GTFS Manager, this means the ID of an exception-only calendar that applies on multiple holidays will become an ID of the first listed holiday. 
- `trip_id` will become a concatenation of the route name, direction name (from `directions.txt`, uses `direction_id` if a name isn't found), altered `service_id`, sequence in block, and start time, separated by `_`.
  - This should always be unique. The script will fail if identical trip IDs are generated.
  - Route names are determined by `route_short_name` or `route_long_name` from `routes.txt`, whichever is available. The script will failure if neither field is populated.
- `route_id` will become the `route_short_name` or `route_long_name` from `routes.txt`, whichever is available, with certain values (like spaces or `&`) removed or altered. 
  - Some feeds contain multiple agencies, which may result in a route name that appears twice, which would lead to a duplicate route ID. Upon seeing the second route, the script will append the agency ID to that route, and will fail at that point if it's still not unique. 
- All files in the provided GTFS will be examined for these fields. Any altered files will be exported to the current directory for human review, and the human will be responsible for adding them to the feed. 