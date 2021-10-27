'''
csv parser & excel parser (xlsx) & tsv parser

csv parser usage: parser.ReadCsv('room/file/path', 'event/file/path')
	e.g. (rooms, events) = parser.ReadCsv('example_rooms.csv', 'example_events.csv')

xlsx parser usage: ReadXL('room/file/path', 'event/file/path')

tsv parser usage: parser.ReadTsv('room/file/path', 'event/file/path')
'''

from io import StringIO
import csv
from .algorithm_I import Room, Event

'''
=================================================================================================
CSV PARSER
'''

def parseRooms(csv_file):
	'''
	read a rooms csv string, returns a list of Room objects
	'''
	reader = csv.reader(StringIO(csv_file.read().decode("utf-8")))
	data = list(reader)
	
	titles = [title.lower().strip() for title in data.pop(0)]
	nameid = titles.index('name')
	capacityid = titles.index('capacity')
	opensid = titles.index('opens')
	closesid = titles.index('closes')

	Retlist = []
	for room in data:
		Retlist.append( Room( room[nameid], int(room[capacityid])
			, float(room[opensid]), float(room[closesid]) ).export() )

	return Retlist

def parseEvents(csv_file):
	'''
	read an events csv file, returns a list of Events
	'''
	reader = csv.reader(StringIO(csv_file.read().decode("utf-8")))
	data = list(reader)

	titles = [title.lower().strip() for title in data.pop(0)]
	nameid = titles.index('name')
	startid = titles.index('starts')
	endid = titles.index('ends')
	attendanceid = titles.index('attendance')

	Retlist = []
	for event in data:
		Retlist.append( Event( event[nameid], float(event[startid])
			, float(event[endid]), int(event[attendanceid]) ).export() )

	return Retlist

'''
=================================================================================================
'''