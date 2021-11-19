from django.http import HttpResponse

import json, base64
from requests_toolbelt.multipart import decoder
from .scripts import algorithm_I, csv_parser, tsv_parser, xlsx_parser, json_parser, txt_parser, algorithm_II


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
        else:
            return HttpResponse(json.dumps({"error": str(rooms_name)+ " File Error: invalid filetype: " + str(rooms_type.lower()), "rooms": [], "events": []}))

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
        else:
            return HttpResponse(json.dumps({"error": str(events_name)+ " File Error: invalid filetype: " + str(events_type.lower()), "rooms": [], "events": []}))

    rooms_list = [] if rooms_list is None else rooms_list
    events_list = [] if events_list is None else events_list

    out = {"rooms": rooms_list, "events": events_list}
    # Return parsed rooms or events
    return HttpResponse(json.dumps(out))

def schedule(request):
    """
    This view takes a set of room and event dictionary objects and calls algorithm I.
    Organizer assigns events to rooms and returns the best configuration along with any
    unassigned events. Catches and returns exceptions as error text

    Arguments-
    request (HTTP Request):     Request containing the room objects found under 'rooms' and event objects found under 'events'

    Returns-
    (HTTP Response):    Response containing solution rooms and any unassigned events if successful else the apppropriate error text
    """

    body = json.loads(request.body)

    room_list = []
    event_list = []

    room_id = 0
    # Load rooms into Room class objects
    for room in body.get("rooms", []):
        room_list.append(algorithm_I.Room(room.get("name", ""), int(room.get("capacity", 1)), float(room.get("opens", -1)), float(room.get("closes", 24)), id=room_id))
        room_id += 1

    event_id = 0
    # Load events into Event class objects
    for event in body.get("events", []):
        event_list.append(algorithm_I.Event(event.get("name", ""), float(event.get("starts", 0)), float(event.get("ends", 24)), int(event.get("attendance", 1)), id=event_id))
        event_id += 1

    try:
        # Determine how many iterations we can afford using estimated time
        time = 0.013 * 1.004**len(event_list)
        iterations = max(min(int(6/time), 400), 100)
        organizer = algorithm_I.Organizer()
        solution, unassigned = organizer.assign(room_list, event_list, iterations=iterations, swap_num=10, temperature=10, print_level="none")
    except Exception as e:
        return HttpResponse(json.dumps({"error": "Assign Error: " + str(e), "solution": [], "unassigned": []}))

    return HttpResponse(json.dumps({"solution": [room.export() for room in solution], "unassigned": [event.export() for event in unassigned]}))

def suggest(request):
    """
    This view takes a solution of rooms and unassigned events and generates suggestions
    to fit the unassigned events into the solution. Catches and returns exceptions as
    error text

    Arguments-
    request (HTTP Request):     Request containing the solution found under 'rooms' and unassigned events under 'unassigned'

    Returns-
    (HTTP Response):    Response containing suggestions, else appropriate error text
    """

    body = json.loads(request.body)

    room_list = []
    unassigned = []

    for room in body.get("rooms", []):
        new_room = algorithm_I.Room(room.get("name", ""), int(room.get("capacity", 1)), float(room.get("opens", -1)), float(room.get("closes", 24)), id=int(room.get("id", 0)))
        for event in room.get("events", []):
            new_room.events.append(algorithm_I.Event(event.get("name", ""), float(event.get("starts", 0)), float(event.get("ends", 24)), int(event.get("attendance", 1)), id=int(event.get("id", 0))))
        room_list.append(new_room)

    for event in body.get("unassigned", []):
        unassigned.append(algorithm_I.Event(event.get("name", ""), float(event.get("starts", 0)), float(event.get("ends", 24)), int(event.get("attendance", 1)), id=int(event.get("id", 0))))

    try:
        parameters = [(5, 0.5, 0, 0, 400), (10, 1, 0.5, 0, 300), (20, 2, 1, 0, 200), (30, 5, 3, 0.25, 100), (40, 10, 10, 0.5, 0)]

        suggester = algorithm_II.Suggester(room_list, unassigned)

        suggestions, still_unassigned = suggester.weightedGridSearch(parameters)

        suggestion_out = []

        for i in range(len(suggestions)):
            suggestion = suggestions[i]
            suggest_string = "Add to room \"" + suggestion[3].name + "\""
            # If we suggest to change the capacity
            if suggestion[1][0] == "capacity":
                # String to show to the user describing the suggestion
                suggest_string += " by increasing capacity by " + str(suggestion[1][1])
                # Unassigned events for this suggestions
                events = [event.export() for event in suggestion[2]]
                # Modify room
                suggestion[3] = suggestion[3].copy()
                room = suggestion[3]
                room.capacity += suggestion[1][1]
                # Just capacity change
                if len(suggestion[1]) == 2:
                    for event in suggestion[2]:
                        room.events.append(event)
                    room.events.sort()
                    for event in events:
                        suggestion_out.append({
                            "suggestion_id": i,
                            "suggestion_string": suggest_string,
                            "unassigned": event,
                            "multiple": events,
                            "room": room.export(),
                            "changed_events": dict()
                        })
                    continue
                else:
                    suggest_string += " and"
                    suggestion[1] = suggestion[1][2:]
            # If we suggest to shift unassigned event
            if suggestion[1][0] == "self shift":
                # String to show to the user describing the suggestion
                suggest_string += " by shifting event \"" + suggestion[2][0].name + "\" by " + str(abs(suggestion[1][1])) + " hours"
                room = suggestion[3]
                # Dictionary mapping to changed events
                changed_events = dict()
                changed_events[suggestion[2][0].id] = suggestion[2][0].export()
                changed_events[suggestion[2][0].id]["starts"] += suggestion[1][1]
                changed_events[suggestion[2][0].id]["ends"] += suggestion[1][1]
                # Unassigned events for this suggestion
                events = suggestion[2][0].export()
                # Modify room
                for event in suggestion[2]:
                    room.events.append(event)
                room.events.sort()
                suggestion_out.append({
                    "suggestion_id": i,
                    "suggestion_string": suggest_string,
                    "unassigned": events,
                    "room": room.export(),
                    "changed_events": changed_events
                })
            # If we suggest to shift events
            if suggestion[1][0] == "shift":
                room = suggestion[3]
                # Dictionary mapping to changed events
                changed_events = dict()
                # For each shifted event
                for j in range(len(suggestion[1][1:])//2):
                    # Shift the event appropriately and add it to the map
                    current_event = room.events[suggestion[1][1:][j*2]].copy()
                    if not current_event.moveBy(suggestion[1][1:][j*2+1]):
                        return HttpResponse(json.dumps({"error": "Invalid shift suggestion: " + str(suggestion), "suggestions": []}))
                    changed_events[current_event.id] = current_event.export()
                    # Build the string
                    if j != 0:
                        suggest_string += " and "
                    suggest_string += " by shifting event \"" + current_event.name + "\" by " + str(abs(suggestion[1][1:][j*2+1])) + " hours"
                # Unassigned events for this suggestion
                events = suggestion[2][0].export()
                # Modify room
                for event in suggestion[2]:
                    room.events.append(event)
                room.events.sort()
                suggestion_out.append({
                    "suggestion_id": i,
                    "suggestion_string": suggest_string,
                    "unassigned": events,
                    "room": room.export(),
                    "changed_events": changed_events
                })
            # If we suggest to shorten events
            if suggestion[1][0] == "length":
                room = suggestion[3]
                # Dictionary mapping to changed events
                changed_events = dict()
                # For each shortened event
                for j in range(len(suggestion[1][1:])//2):
                    # Shorten the event appropriately and add it to the map
                    current_event = room.events[suggestion[1][1:][j*2]]
                    if not current_event.shortenBy(suggestion[1][1:][j*2+1]):
                        return HttpResponse(json.dumps({"error": "Invalid length suggestion: " + str(suggestion), "suggestions": []}))
                    changed_events[current_event.id] = current_event.export()
                    # Build the string
                    if j != 0:
                        suggest_string += " and "
                    suggest_string += " by shortening event \"" + current_event.name + "\" by " + str(abs(suggestion[1][1:][j*2+1])) + " hours"
                # Unassigned events for this suggestion
                events = suggestion[2][0].export()
                # Modify room
                for event in suggestion[2]:
                    room.events.append(event)
                room.events.sort()
                suggestion_out.append({
                    "suggestion_id": i,
                    "suggestion_string": suggest_string,
                    "unassigned": events,
                    "room": room.export(),
                    "changed_events": changed_events
                })
        
        for event in still_unassigned:
            suggestion_out.append({
                "suggestion_id": len(suggestions),
                "suggestion_string": "No suggestion available",
                "unassigned": event.export(),
                "room": None,
                "changed_events": dict()
            })
    except Exception as e:
        return HttpResponse(json.dumps({"error": "Suggestion Error: " + str(e), "suggestions": []}))
    
    return HttpResponse(json.dumps({"suggestions": suggestion_out}))