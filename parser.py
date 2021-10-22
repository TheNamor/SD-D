'''
csv parser & excel parser (xlsx) & tsv parser

csv parser usage: parser.ReadCsv('room/file/path', 'event/file/path')
	e.g. (rooms, events) = parser.ReadCsv('example_rooms.csv', 'example_events.csv')

xlsx parser usage: ReadXL('room/file/path', 'event/file/path')

tsv parser usage: parser.ReadTsv('room/file/path', 'event/file/path')
'''

import csv
import pandas
import util

'''
=================================================================================================
CSV PARSER
'''

def ReadCsv_Rooms(file):
	'''
	read a rooms csv file, returns a list of Room objects
	'''
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



def main():
	'''
	csv parser usage: ReadCsv('room/file/path', 'event/file/path')
	e.g. (rooms, events) = ReadCsv('example_rooms.csv', 'example_events.csv')
	'''
	
	'''
	xlsx parser usage: ReadXL('room/file/path', 'event/file/path')
	e.g. (rooms, events) = ReadXL('example_rooms.csv', 'example_events.csv')

	'''
	

if __name__ == '__main__':
	main()