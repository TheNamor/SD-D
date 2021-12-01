'''
=================================================================================================
EXCEL PARSER (.xlsx)
'''
from io import StringIO
import pandas
from .algorithm_I import Room, Event

def parseRooms(xlsx_file):
	data = pandas.read_excel(xlsx_file, engine='openpyxl')
	data.columns = data.columns.str.strip().str.lower()
	namelist = data['name'].tolist()
	capacitylist = data['capacity'].tolist()
	openslist = data['opens'].tolist()
	closeslist = data['closes'].tolist()

	Retlist = []
	for i in range(0, len(namelist)):
		Retlist.append( Room( namelist[i], int(capacitylist[i])
			, float(openslist[i]), float(closeslist[i]) ).export() )
	return Retlist

def parseEvents(xlsx_file):
	data = pandas.read_excel(xlsx_file, engine='openpyxl')
	data.columns = data.columns.str.strip().str.lower()
	namelist = data['name'].tolist()
	startlist = data['starts'].tolist()
	endlist = data['ends'].tolist()
	attendancelist = data['attendance'].tolist()

	Retlist = []
	for i in range(0, len(namelist)):
		Retlist.append( Event( namelist[i], float(startlist[i])
			, float(endlist[i]), int(attendancelist[i]) ).export() )
	return Retlist

'''
=================================================================================================
'''