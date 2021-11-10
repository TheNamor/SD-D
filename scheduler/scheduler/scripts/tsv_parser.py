'''
=================================================================================================
TSV PARSER
'''

from io import StringIO
import csv
from .algorithm_I import Room, Event

def parseRooms(tsv_file):
	'''
	read a rooms tsv file, returns a list of Room objects
	'''
	reader = csv.reader(StringIO(tsv_file.read().decode("utf-8")), delimiter = "\t", quotechar = '"')
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

def parseEvents(tsv_file):
	'''
	read an events tsv file, returns a list of Events
	'''
	reader = csv.reader(StringIO(tsv_file.read().decode("utf-8")), delimiter = "\t", quotechar = '"')
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