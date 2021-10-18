from django.http import HttpResponse

import json
from requests_toolbelt.multipart import decoder
from .scripts import algorithm_I


def upload(request):
    multipart_text = str(request.body)
    content_type = "multipart/form-data; boundary=" + multipart_text[multipart_text.index("----WebKitFormBoundary"):multipart_text.index("Content-Disposition")-4]

    rooms_string = None
    rooms_type = None
    events_string = None
    events_type = None

    try:
        for part in decoder.MultipartDecoder(request.body, content_type).parts:
            headers_strings = part.headers.get(b'Content-Disposition').decode("utf-8").split("; ")
            headers = {}
            for string in headers_strings:
                if "=" in string:
                    headers[string[:string.index("=")]] = string[string.index("=")+1:].strip("\"'")
            filename = headers.get("filename", "")
            if headers.get("name", "") == "rooms":
                rooms_string = part.text
                rooms_type = filename[filename.rfind("."):]
            elif headers.get("name", "") == "events":
                events_string = part.text
                events_type = filename[filename.rfind("."):]
    except Exception as e:
        return HttpResponse(json.dumps({"error": "File Error: " + str(e), "rooms": [], "events": []}))

    
    """
    if not rooms_string is None:
        if rooms_type.lower() == ".json":
            rooms_list = json_parser.parseRooms(rooms_string)
        elif...
    else:
        return error
    
    if not events_string is None:
        if events_type.lower() == ".json":
            events_list = json_parser.parseEvents(events_string)
        elif...
    else:
        return error
    
    if rooms_list and events_list:
        solution, unassigned = algorithm_I.assign(rooms_list, events_list)
    """

    out = {"solution": "Uploaded rooms of type " + str(rooms_type) + " and events of type " + str(events_type), "rooms": [], "events": []}

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
        solution, unassigned = algorithm_I.assign(room_list, event_list, iterations=100, swap_num=10, temperature=10, print_level="none")
    except Exception as e:
        return HttpResponse(json.dumps({"error": "Assign Error: " + str(e), "solution": [], "unassigned": []}))

    return HttpResponse(json.dumps({"solution": [room.export() for room in solution], "unassigned": [event.export() for event in unassigned]}))