from django.http import HttpResponse

import json, base64
from requests_toolbelt.multipart import decoder
from .scripts import algorithm_I, csv_parser, tsv_parser, xlsx_parser, json_parser, txt_parser


def upload(request):
    """
    This view takes a set of files and converts them into room and event dictionaries to be
    returned to the frontend. Catches and returns exceptions as error text

    Arguments-
    request (HTTP Request):     Request containing the uploaded files, room file found under 'rooms', event file found under 'events'

    Returns-
    (HTTP Response):    Response containing room or event dictionaries if files were provided and parsing was successful, else appropriate error text
    """

    try:
        # Collect files and find file names and types
        files = request.FILES
        rooms_file = files.get("rooms")
        events_file = files.get("events")
        rooms_name, events_name, rooms_type, events_type = "", "", "", ""

        if not rooms_file is None:
            rooms_name = rooms_file.name
            rooms_type = rooms_name[rooms_name.rfind("."):]
        
        if not events_file is None:
            events_name = events_file.name
            events_type = events_name[events_name.rfind("."):]
    except Exception as e:
        return HttpResponse(json.dumps({"error": "File Error: " + str(e), "rooms": [], "events": []}))

    rooms_list, events_list = None, None
    
    if not rooms_file is None:
        # Use json, csv, xlsc, tsv parsers on their respective files
        if rooms_type.lower() == ".json":
            try:
                rooms_list = json_parser.parseRooms(rooms_file)
            except Exception as e:
                return HttpResponse(json.dumps({"error": str(rooms_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
        elif rooms_type.lower() == ".csv":
            try:
                rooms_list = csv_parser.parseRooms(rooms_file)
            except Exception as e:
                return HttpResponse(json.dumps({"error": str(rooms_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
        elif rooms_type.lower() == ".xlsx":
            try:
                rooms_list = xlsx_parser.parseRooms(rooms_file)
            except Exception as e:
                return HttpResponse(json.dumps({"error": str(rooms_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
        elif rooms_type.lower() == ".tsv":
            try:
                rooms_list = tsv_parser.parseRooms(rooms_file)
            except Exception as e:
                return HttpResponse(json.dumps({"error": str(rooms_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
        elif rooms_type.lower() == ".txt":
            # For txt files try to guess the delimeter, tab -> comma -> space -> error
            file_string = rooms_file.read().decode("utf-8")
            rooms_file.seek(0)
            response = None
            if "\t" in file_string:
                try:
                    rooms_list = tsv_parser.parseRooms(rooms_file)
                except Exception as e:
                    response = HttpResponse(json.dumps({"error": str(rooms_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
            if rooms_list is None and ("," in file_string or not response is None):
                try:
                    rooms_list = csv_parser.parseRooms(rooms_file)
                except Exception as e:
                    if response is None:
                        response = HttpResponse(json.dumps({"error": str(rooms_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
            if rooms_list is None and (" " in file_string or not response is None):
                try:
                    rooms_list = txt_parser.parseRooms(file_string)
                except Exception as e:
                    if response is None:
                        response = HttpResponse(json.dumps({"error": str(rooms_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
            if rooms_list is None:
                if not response is None:
                    return response
                return HttpResponse(json.dumps({"error": str(rooms_name)+ " File Error: could not parse file, invalid delimeter", "rooms": [], "events": []}))

    if not events_file is None:
        # Use json, csv, xlsc, tsv parsers on their respective files
        if events_type.lower() == ".json":
            try:
                events_list = json_parser.parseEvents(events_file)
            except Exception as e:
                return HttpResponse(json.dumps({"error": str(events_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
        elif events_type.lower() == ".csv":
            try:
                events_list = csv_parser.parseEvents(events_file.read())
            except Exception as e:
                return HttpResponse(json.dumps({"error": str(events_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
        elif events_type.lower() == ".xlsx":
            try:
                events_list = xlsx_parser.parseEvents(events_file.read())
            except Exception as e:
                return HttpResponse(json.dumps({"error": str(events_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
        elif events_type.lower() == ".tsv":
            try:
                events_list = tsv_parser.parseEvents(events_file)
            except Exception as e:
                return HttpResponse(json.dumps({"error": str(events_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
        elif events_type.lower() == ".txt":
            # For txt files try to guess the delimeter, tab -> comma -> space -> error
            file_string = events_file.read().decode("utf-8")
            events_file.seek(0)
            response = None
            if "\t" in file_string:
                try:
                    events_list = tsv_parser.parseEvents(events_file)
                except Exception as e:
                    response = HttpResponse(json.dumps({"error": str(events_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
            if events_list is None and ("," in file_string or not response is None):
                try:
                    events_list = csv_parser.parseEvents(events_file)
                except Exception as e:
                    if response is None:
                        response = HttpResponse(json.dumps({"error": str(events_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
            if events_list is None and (" " in file_string or not response is None):
                try:
                    events_list = txt_parser.parseEvents(file_string)
                except Exception as e:
                    if response is None:
                        response = HttpResponse(json.dumps({"error": str(events_name)+ " File Error: " + str(e), "rooms": [], "events": []}))
            if events_list is None:
                if not response is None:
                    return response
                return HttpResponse(json.dumps({"error": str(events_name)+ " File Error: could not parse file, invalid delimeter", "rooms": [], "events": []}))

    rooms_list = [] if rooms_list is None else rooms_list
    events_list = [] if events_list is None else events_list

    out = {"rooms": rooms_list, "events": events_list}
    # Return parsed rooms or events
    return HttpResponse(json.dumps(out))

def schedule(request):
    body = json.loads(request.body)

    room_list = []
    event_list = []

    for room in body.get("rooms", []):
        room_list.append(algorithm_I.Room(room.get("name", ""), int(room.get("capacity", 1)), float(room.get("opens", -1)), float(room.get("closes", 24))))

    for event in body.get("events", []):
        event_list.append(algorithm_I.Event(event.get("name", ""), float(event.get("starts", 0)), float(event.get("ends", 24)), int(event.get("attendance", 1))))

    try:
        time = 0.013 * 1.004**len(event_list)
        iterations = max(min(int(6/time), 400), 100)
        organizer = algorithm_I.Organizer()
        solution, unassigned = organizer.algorithm_I.assign(room_list, event_list, iterations=iterations, swap_num=10, temperature=10, print_level="none")
    except Exception as e:
        return HttpResponse(json.dumps({"error": "Assign Error: " + str(e), "solution": [], "unassigned": []}))

    return HttpResponse(json.dumps({"solution": [room.export() for room in solution], "unassigned": [event.export() for event in unassigned]}))