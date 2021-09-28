"""
This document contains the OOP that assigns a list of events to a list of rooms in the best way

Authors:
    Roman Nett

Ver 1- (iterations=100, swap_num=10, temperature=10)
    Accuracy ~ 77.9%
    Time per point ~ 0.159
Ver 2- (iterations=100, swap_num=10, temperature=10)
    Accuracy ~ 90%
    Time per point ~ 0.026
"""

import random, math

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

def findSolution(rooms, events):
    """
    Takes a list of Rooms and a list of Events and assigns each Event to a Room in such a way
    that there are no overlapping Events in Rooms and that the most number of Events are assigned

    Arguments-
    rooms (list):       a list of Room objects that can be assigned Events
    events (list):      an ordered list of Events to be assigned to Rooms

    Returns-
    (tuple):     a list of lists of Events corresponding to Rooms, a list of unassigned Events
    """
    out = [[] for i in range(len(rooms))]
    assigned = True
    events = events.copy()

    # Run while events can fit and you haven't fit in all the events
    while assigned and len(events):
        assigned = False
        for i in range(len(rooms)):
            earliest = out[i][-1].ends if len(out[i]) else rooms[i].opens
            found = None
            for j in range(len(events)):
                # For each room place in the earliest room that can fit
                event = events[j]
                if event.starts >= earliest and event.ends <= rooms[i].closes and event.attendees <= rooms[i].capacity:
                    found = events.pop(j)
                    break
            if not found is None:
                out[i].append(found)
                assigned = True
    
    return out, events

def fitUnassigned(room, room_list, unassigned):
    """
    Fits unassigned events into a room in between any events already assigned

    Arguments-
    room (Room):        the Room object that events are being assigned to
    room_list (list):   the list of Event objects corresponding to the Room
    unassigned (list):  list of unassigned Events

    Returns-
    (tuple):        room_list with new Events assigned to it, new unassigned with assigned Events removed
    """
    assigned = True
    while assigned:
        assigned = False
        for i in range(len(room_list)):
            for j in range(len(unassigned)):
                event = unassigned[j]
                if room_list[i].starts >= event.ends and event.starts >= room.opens and event.ends <= room.closes and event.attendees <= room.capacity:
                    assigned = True
                    room_list.insert(i, unassigned.pop(j))
                    break
        if len(room_list):
            for j in range(len(unassigned)):
                event = unassigned[j]
                if room_list[-1].ends <= event.starts and event.ends <= room.closes and event.attendees <= room.capacity:
                    assigned = True
                    room_list.append(unassigned.pop(j))
                    break
        else:
            for j in range(len(unassigned)):
                event = unassigned[j]
                if event.starts >= room.opens and event.ends <= room.closes and event.attendees <= room.capacity:
                    assigned = True
                    room_list.append(unassigned.pop(j))
                    break
    
    return room_list, unassigned

def findCandidate(rooms, current, swap_num, unassigned):
    """
    Removes a number of events from random rooms and adds them back to the pool of unassigned rooms
    Then it fits unassigned rooms back into them

    Arguments-
    rooms (list):       list of rooms
    current (list):     current solution
    swap_num (int):     the number of swaps to make
    unassigned (list):  list of current unassigned events

    Returns-
    (tuple):    new candidate solution, list of unassigned events
    """
    new_candidate = [current[i].copy() for i in range(len(current))]
    unassigned = unassigned.copy()

    swap_indices = []
    for i in range(swap_num):
        index = random.randrange(len(new_candidate))
        swap_indices.append(index)
        if len(new_candidate[index]):
            unassigned.append(new_candidate[index].pop(random.randrange(len(new_candidate[index]))))
    
    for index in swap_indices:
        new_candidate[index], unassigned = fitUnassigned(rooms[index], new_candidate[index], unassigned)
    
    return new_candidate, unassigned

def assign(rooms, events, iterations=500, swap_num=10, temperature=10, print_level="all"):
    """
    Performs greedy first fit decreasing to find an initial best solution and then uses simulated
    annealing to optimize the greedy solution

    Arguments-
    rooms (list):       a list of Room objects that can be assigned Events
    events (list):      a list of Event objects that need to be assigned to a Room

    Named Arguments-
    iterations (int)=500:           the number of iterations to run simulated annealing over
    swap_num (int)=10:              the number of swaps in the current list of events to make to get the candidate solution
    temperature (int)=10:           the starting temperature for annealing, the likelihood a worse candidate will become the current solution
    print_level (string)="all":     a string representing how much to print to the console when testing

    Returns-
    (tuple):        the best solution, list of unassigned events, list of times the number of unassigned events was decreased
    """
    evals = []

    # Find the first best solution using a greedy first fit decreasing method
    events.sort()
    best, best_unassigned = findSolution(rooms, events.copy())
    best_eval = len(best_unassigned)

    curr, curr_eval, curr_unassigned = best, best_eval, best_unassigned

    # Simulated annealing over a number of iterations
    for i in range(iterations):
        if best_eval == 0:
            #break
            pass
        # Find the neighboring candidate by swapping a random number of events in the ordered list
        candidate, candidate_unassigned = findCandidate(rooms, curr, random.randrange(swap_num), curr_unassigned)
        candidate_eval = len(candidate_unassigned)
        if print_level in ["some", "all", "epoch"]:
            print("Epoch", str(i) + ":", curr_eval, "vs", candidate_eval)

        # If you have found a new best soluton save it
        if candidate_eval < best_eval:
            best, best_eval, best_unassigned = candidate, candidate_eval, candidate_unassigned
            evals.append(best_eval)
        
        # Use the current temperature to find the metropolis acceptance criterion
        eval_diff = candidate_eval - curr_eval
        temp = temperature / (i + 1)
        metropolis = math.exp(-eval_diff/temp)

        # If you have a best solution or get below the criterion, set the current solution to the candidate
        if eval_diff < 0 or random.random() < metropolis:
            curr, curr_eval, curr_unassigned = candidate, candidate_eval, candidate_unassigned

    # Assign the best found solution to the rooms
    for i in range(len(best)):
        rooms[i].events = best[i]
    
    # Print some things
    if print_level != "none":
        print(len(best_unassigned), "events not assigned")
    if print_level == "all":
        printEvents(best_unassigned)

    if print_level in ["some", "all"]:
        for room in rooms:
            print("Room:", room.name)
            if print_level == "all":
                printEvents(room.events)
            else:
                print(len(room.events), "events assigned")
    
    return best, best_unassigned, evals

if __name__ == "__main__":
    big_rooms = []
    big_events = []
    num_rooms = 200
    num_events = 900

    for i in range(num_rooms):
        big_rooms.append(Room("Room " + str(i), random.randint(10, 30), opens=random.randint(8, 10), closes=random.randint(15, 18)))

    for i in range(num_events):
        start = random.randint(8, 14) + random.random()
        length = random.randint(1, 2) + random.random()
        big_events.append(Event("Event " + str(i), start, start+length, random.randint(10, 30)))

    rooms, unassigned, evals = assign(big_rooms, big_events, iterations=100, swap_num=10, temperature=10, print_level="epoch")

    print(str((100-(len(unassigned)/num_events)*100))+"% Assigned")