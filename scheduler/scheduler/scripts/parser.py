'''
csv parser & excel parser (xlsx) & tsv parser & json parser

Might need to install csv, pandas, json modules beforehand



Usage:
csv parser: parser.ReadCsv('room/file/path', 'event/file/path')
	e.g. (rooms, events) = parser.ReadCsv('example_rooms.csv', 'example_events.csv')

xlsx parser: parser.ReadXL('room/file/path', 'event/file/path')

tsv parser: parser.ReadTsv('room/file/path', 'event/file/path')

json parser: parser.ReadJson('room/file/path', 'event/file/path')
'''

import csv
import pandas
import json
import util

'''
=================================================================================================
CSV PARSER
'''

def ReadCsv_Rooms(file):
	'''
	read a rooms csv file, returns a list of Room objects
	'''
	if (file.find('.csv') == -1):
		print("ERROR: {} is not a csv file".format(file))
		return []

	with open(file, newline = '') as f:
		reader = csv.reader(f)
		data = list(reader)
	
	titles = data.pop(0)
	nameid = titles.index('name')
	capacityid = titles.index('capacity')
	opensid = titles.index('opens')
	closesid = titles.index('closes')

	Retlist = []
	for room in data:
		Retlist.append( util.Room( room[nameid], int(room[capacityid])
			, float(room[opensid]), float(room[closesid]) ) )

	return Retlist

def ReadCsv_Events(file):
	'''
	read an events csv file, returns a list of Events
	'''
	if (file.find('.csv') == -1):
		print("ERROR: {} is not a csv file".format(file))
		return []

	with open(file, newline = '') as f:
		reader = csv.reader(f)
		data = list(reader)

	titles = data.pop(0)
	nameid = titles.index('name')
	startid = titles.index('start')
	endid = titles.index('end')
	attendanceid = titles.index('attendance')

	Retlist = []
	for event in data:
		Retlist.append( util.Event( event[nameid], float(event[startid])
			, float(event[endid]), int(event[attendanceid]) ) )

	return Retlist

def ReadCsv(roomfile, eventfile):
	'''
	read the two csv files, return a tuple (roomslist, eventslist)
	'''
	return (ReadCsv_Rooms(roomfile), ReadCsv_Events(eventfile))

'''
=================================================================================================
'''



'''
=================================================================================================
EXCEL PARSER (.xlsx)
'''

def ReadXL_Rooms(file):
	if (file.find('.xlsx') == -1):
		print("ERROR: {} is not a xlsx file".format(file))
		return []

	data = pandas.read_excel(file)
	namelist = data['name'].tolist()
	capacitylist = data['capacity'].tolist()
	openslist = data['opens'].tolist()
	closeslist = data['closes'].tolist()

	Retlist = []
	for i in range(0, len(namelist)):
		Retlist.append( util.Room( namelist[i], int(capacitylist[i])
			, float(openslist[i]), float(closeslist[i]) ) )
	return Retlist

def ReadXL_Events(file):
	if (file.find('.xlsx') == -1):
		print("ERROR: {} is not a xlsx file".format(file))
		return []

	data = pandas.read_excel(file)
	namelist = data['name'].tolist()
	startlist = data['start'].tolist()
	endlist = data['end'].tolist()
	attendancelist = data['attendance'].tolist()

	Retlist = []
	for i in range(0, len(namelist)):
		Retlist.append( util.Event( namelist[i], float(startlist[i])
			, float(endlist[i]), int(attendancelist[i]) ) )
	return Retlist

def ReadXL(roomfile, eventfile):
	'''
	read the two xlsx files, return a tuple (roomslist, eventslist)
	'''
	return (ReadXL_Rooms(roomfile), ReadXL_Events(eventfile))

'''
=================================================================================================
'''



'''
=================================================================================================
TSV PARSER
'''

def ReadTsv_Rooms(file):
	'''
	read a rooms tsv file, returns a list of Room objects
	'''
	if (file.find('.tsv') == -1):
		print("ERROR: {} is not a tsv file".format(file))
		return []

	with open(file) as f:
		reader = csv.reader(f, delimiter = "\t", quotechar = '"')
		data = list(reader)
	
	titles = data.pop(0)
	nameid = titles.index('name')
	capacityid = titles.index('capacity')
	opensid = titles.index('opens')
	closesid = titles.index('closes')

	Retlist = []
	for room in data:
		Retlist.append( util.Room( room[nameid], int(room[capacityid])
			, float(room[opensid]), float(room[closesid]) ) )

	return Retlist

def ReadTsv_Events(file):
	'''
	read an events tsv file, returns a list of Events
	'''
	if (file.find('.tsv') == -1):
		print("ERROR: {} is not a tsv file".format(file))
		return []

	with open(file) as f:
		reader = csv.reader(f, delimiter = "\t", quotechar = '"')
		data = list(reader)

	titles = data.pop(0)
	nameid = titles.index('name')
	startid = titles.index('start')
	endid = titles.index('end')
	attendanceid = titles.index('attendance')

	Retlist = []
	for event in data:
		Retlist.append( util.Event( event[nameid], float(event[startid])
			, float(event[endid]), int(event[attendanceid]) ) )

	return Retlist

def ReadTsv(roomfile, eventfile):
	'''
	read the two csv files, return a tuple (roomslist, eventslist)
	'''
	return (ReadTsv_Rooms(roomfile), ReadTsv_Events(eventfile))

'''
=================================================================================================
'''



'''
=================================================================================================
JSON PARSER
'''

def ReadJson_Room(file):
	if (file.find('.json') == -1):
		print("ERROR: {} is not a json file".format(file))
		return []

	f = open(file)
	data = json.load(f)
	Retlist = []
	for r in data['rooms']:
		Retlist.append( util.Room( r['name'], int(r['capacity'])
			, float(r['opens']), float(r['closes']) ) )
	return Retlist

def ReadJson_Event(file):
	if (file.find('.json') == -1):
		print("ERROR: {} is not a json file".format(file))
		return []

	f = open(file)
	data = json.load(f)
	Retlist = []
	for e in data['events']:
		Retlist.append( util.Event( e['name'], float(e['start'])
			, float(e['end']), float(e['attendance']) ) )
	return Retlist

def ReadJson(roomfile, eventfile):
	'''
	return tuple (roomslist, eventslist)
	'''
	return (ReadJson_Room(roomfile), ReadJson_Event(eventfile))

'''
=================================================================================================
'''



def main():
	
	

if __name__ == '__main__':
	main()