'''
Room & Event class
some helper functions
'''





class Room(object):
    """
    This class represents a room object. Each room has its own object and can be assigned multiple events

    Properties-
    name (string):      the name of the room
    opens (float):      the 24h decimal representation of when the room opens (8:30am -> 8.5)
    closes (float):     the 24h decimal representation of when the room closes (5:30pm -> 17.5)
    capacity (int):     the number of people that can fit in the room
    events (list):     list of events assigned to the room
    """

    def __init__(self, name, capacity, opens=-1, closes=24):
        """
        Creates a new Room instance

        Arguments-
        name (string):      the name of the new room
        capacity (int):     the number of people that can fit in the room

        Named Arguments-
        opens (float)=-1:    the 24h decimal representation of when the room opens, -1 shows always open
        closes (float)=24:   the 24h decimal representation of when the room closes, 24 shows never closes
        """
        self.name = name
        self.capacity = capacity
        self.opens = opens
        self.closes = closes
        self.events = []

class Event(object):
    """
    This class represents an event such as a class or a meeting. Each event has its own object

    Properties-
    name (string):      the name of the event
    starts (float):     the 24h decimal representation of when the class starts (8:30am -> 8.5)
    ends (float):       the 24h decimal representation of when the class ends (5:30pm -> 17.5)
    attendees (int):    the maximum number of people attending the event
    """

    def __init__(self, name, starts, ends, attendees):
        """
        Creates a new Event instance

        Arguments-
        name (string):      the name of the event
        starts (float):     the 24h decimal representation of when the class starts
        ends (float):       the 24h decimal representation of when the class ends
        attendees (int):    the maximum number of people attending the event
        """
        self.name = name
        self.starts = starts
        self.ends = ends
        self.attendees = attendees
    
    def __lt__(self, other):
        """
        Determines the sorting order of two Events, earlier and longer events should be less than later and shorter ones
        ties are broken by attendees

        Arguments-
        other (Event):      the other Event being compared to this one

        Returns-
        (bool):     whether the other Event should be before or after this one in order
        """
        if other.starts == self.starts:
            if (self.ends - self.starts) == (other.ends - other.starts):
                return self.attendees > other.attendees
            return (self.ends - self.starts) > (other.ends - other.starts)
        return self.starts < other.starts

def printEvents(events):
    """
    Testing function to print out the names of a list of events

    Arguments-
    events (list):      list of events to print the names of
    """

    for event in events:
        print("\t", event.name, "(" + str(event.starts), "-", str(event.ends) + ")", event.attendees)

def printRoom(r):
    '''
    testing function, print a room object
    '''
    print("\nname: " + r.name, "\ncapacity: ", r.capacity, "\nopens: ", r.opens, "\ncloses: ", r.closes)

def printEvent(e):
    '''
    testing function, print a event object
    '''
    print("\nname: " + e.name, "\nstarts: ", e.starts, "\nends: ", e.ends, "\nattendance: ", e.attendees)