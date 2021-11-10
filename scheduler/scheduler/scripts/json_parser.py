'''
=================================================================================================
JSON PARSER
'''

import json
from .algorithm_I import Room, Event

def parseRooms(json_file):

	data = json.load(json_file)
	Retlist = []
	for r in data['rooms']:
		Retlist.append( Room( r['name'], int(r['capacity'])
			, float(r['opens']), float(r['closes']) ).export() )
	return Retlist

def parseEvents(json_file):

	data = json.load(json_file)
	Retlist = []
	for e in data['events']:
		Retlist.append( Event( e['name'], float(e['starts'])
			, float(e['ends']), float(e['attendance']) ).export() )
	return Retlist
'''
=================================================================================================
'''