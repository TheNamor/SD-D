"""
This document contains the OOP that assigns a list of events to a list of rooms in the best way

Authors:
    Roman Nett

Ver 1- (iterations=100, swap_num=10, temperature=10)
    Accuracy ~ 72.9%
    Time per point ~ 0.159
Ver 2- (iterations=100, swap_num=10, temperature=10)
    Accuracy ~ 87%
    Time per iteration ~ 0.0007
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
    events (list):      list of events assigned to the room
    """

    def __init__(self, name, capacity, opens=-1, closes=24, id=0):
        """
        Creates a new Room instance

        Arguments-
        name (string):      the name of the new room
        capacity (int):     the number of people that can fit in the room

        Named Arguments-
        opens (float)=-1:    the 24h decimal representation of when the room opens, -1 shows always open
        closes (float)=24:   the 24h decimal representation of when the room closes, 24 shows never closes
        """
        self.id = id
        self.name = name
        self.capacity = capacity
        self.opens = opens
        self.closes = closes
        self.events = []
    
    def export(self):
        """
        Transforms the object into a dictionary for exporting to the frontend

        Returns-
        (dict):     dictionary of the object's properties
        """
        event_dicts = [event.export() for event in self.events]
        return {"name": self.name, "capacity": self.capacity, "opens": self.opens, "closes": self.closes, "events": event_dicts}

class Event(object):
    """
    This class represents an event such as a class or a meeting. Each event has its own object

    Properties-
    name (string):      the name of the event
    starts (float):     the 24h decimal representation of when the class starts (8:30am -> 8.5)
    ends (float):       the 24h decimal representation of when the class ends (5:30pm -> 17.5)
    attendance (int):   the maximum number of people attending the event
    """

    def __init__(self, name, starts, ends, attendance, id=0):
        """
        Creates a new Event instance

        Arguments-
        name (string):      the name of the event
        starts (float):     the 24h decimal representation of when the class starts
        ends (float):       the 24h decimal representation of when the class ends
        attendance (int):   the maximum number of people attending the event
        """
        self.id = id
        self.name = name
        self.starts = starts
        self.ends = ends
        self.attendance = attendance
    
    def __lt__(self, other):
        """
        Determines the sorting order of two Events, earlier and longer events should be less than later and shorter ones
        ties are broken by attendance

        Arguments-
        other (Event):      the other Event being compared to this one

        Returns-
        (bool):     whether the other Event should be before or after this one in order
        """
        if other.starts == self.starts:
            if (self.ends - self.starts) == (other.ends - other.starts):
                return self.attendance > other.attendance
            return (self.ends - self.starts) > (other.ends - other.starts)
        return self.starts < other.starts
    
    def copy(self):
        """
        Copies the current event object

        Returns-
        (Event):        copy of the event
        """
        return Event(self.name, self.starts, self.ends, self.attendance, id=self.id)
    
    def getLength(self):
        """
        The length of the event in hours getter

        Returns-
        (float):        the length of the event in hours
        """
        return self.ends - self.starts
    
    def moveBy(self, change):
        """
        Moves the event by the specified amount

        Arguments-
        change (float):     the number of hours to move by

        Returns-
        (bool):     bool whether the change was successfully made and valid
        """

        if self.starts+change < 0 or self.starts+change > 24:
            return False
        if self.ends+change < 0 or self.ends+change > 24:
            return False
        
        self.starts += change
        self.ends += change

        return True
    
    def shortenBy(self, change):
        """
        Shortens the event by the specified amount

        Arguments-
        change (float):     amount to shorten the event by, negative will change the ends, positive will change the starts

        Returns-
        (bool):     whether the shorten was successfully made and valid
        """

        if change == 0:
            return False

        if change > 0:
            if self.starts+change >= self.ends or self.starts+change > 24:
                return False
            self.starts += change
            return True
        else:
            if self.ends+change <= self.starts or self.ends+change < 0:
                return False
            self.ends += change
            return True
    
    def export(self):
        """
        Transforms the object into a dictionary for exporting to the frontend

        Returns-
        (dict):     dictionary of the object's properties
        """
        return {"name": self.name, "attendance": self.attendance, "starts": self.starts, "ends": self.ends, "id": self.id}

class Organizer(object):

    def __init__(self):
        pass

    def findSolution(self, rooms, events):
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
                    if event.starts >= earliest and event.ends <= rooms[i].closes and event.attendance <= rooms[i].capacity:
                        found = events.pop(j)
                        break
                if not found is None:
                    out[i].append(found)
                    assigned = True
        
        return out, events

    def fitUnassigned(self, room, room_list, unassigned):
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
        # Continues looking for open spots until no events can fit in
        while assigned:
            assigned = False
            # For every event assigned to the room
            for i in range(len(room_list)):
                # For every unassigned event
                for j in range(len(unassigned)):
                    event = unassigned[j]
                    # Check if the unassigned event fits before the assigned event in the room
                    if room_list[i].starts >= event.ends and event.starts >= room.opens and event.ends <= room.closes and event.attendance <= room.capacity and (i == 0 or room_list[i-1].ends <= event.starts):
                        # If a fit is found, assign it and start the process over
                        assigned = True
                        room_list.insert(i, unassigned.pop(j))
                        break
            # Check if any of the unassigned events fit after the last assigned event
            if len(room_list):
                for j in range(len(unassigned)):
                    event = unassigned[j]
                    if room_list[-1].ends <= event.starts and event.ends <= room.closes and event.attendance <= room.capacity:
                        assigned = True
                        room_list.append(unassigned.pop(j))
                        break
            # Check if any unassigned events fit in an empty room
            else:
                for j in range(len(unassigned)):
                    event = unassigned[j]
                    if event.starts >= room.opens and event.ends <= room.closes and event.attendance <= room.capacity:
                        assigned = True
                        room_list.append(unassigned.pop(j))
                        break
        
        return room_list, unassigned

    def findCandidate(self, rooms, current, swap_num, unassigned):
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
        # Create copies of the room list and unassigned events list
        new_candidate = [current[i].copy() for i in range(len(current))]
        unassigned = unassigned.copy()

        swap_indices = []
        # Pick a set of random room lists and remove a random event from them
        for i in range(swap_num):
            index = random.randrange(len(new_candidate))
            swap_indices.append(index)
            if len(new_candidate[index]):
                unassigned.append(new_candidate[index].pop(random.randrange(len(new_candidate[index]))))
        
        # For each room list that had an event removed see if unassigned events can fit into it
        for index in swap_indices:
            new_candidate[index], unassigned = self.fitUnassigned(rooms[index], new_candidate[index], unassigned)
        
        return new_candidate, unassigned

    def assign(self, rooms, events, iterations=500, swap_num=10, temperature=10, print_level="all"):
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

        # Find the first best solution using a greedy first fit decreasing method
        events.sort()
        best, best_unassigned = self.findSolution(rooms, events.copy())
        best_eval = len(best_unassigned)

        curr, curr_eval, curr_unassigned = best, best_eval, best_unassigned

        # Simulated annealing over a number of iterations
        for i in range(iterations):
            if best_eval == 0:
                #break
                pass
            # Find the neighboring candidate by swapping a random number of events in the ordered list
            candidate, candidate_unassigned = self.findCandidate(rooms, curr, random.randrange(swap_num), curr_unassigned)
            candidate_eval = len(candidate_unassigned)
            if print_level in ["some", "all", "epoch"]:
                print("Epoch", str(i) + ":", curr_eval, "vs", candidate_eval)

            # If you have found a new best soluton save it
            if candidate_eval < best_eval:
                best, best_eval, best_unassigned = candidate, candidate_eval, candidate_unassigned
            
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
        
        return rooms, best_unassigned


def printEvents(events):
    """
    Testing function to print out the names of a list of events

    Arguments-
    events (list):      list of events to print the names of
    """

    for event in events:
        print("\t", event.name, "(" + str(event.starts), "-", str(event.ends) + ")", event.attendance)

if __name__ == "__main__":
    import algorithm_II
    
    random.seed(100)
    big_rooms = []
    big_events = []
    num_rooms = 200
    num_events = 800

    for i in range(num_rooms):
        big_rooms.append(Room("Room " + str(i), random.randint(10, 30), opens=random.randint(8, 10), closes=random.randint(15, 18)))

    for i in range(num_events):
        start = random.randint(8, 14) + random.random()
        length = random.randint(1, 2) + random.random()
        big_events.append(Event("Event " + str(i), start, start+length, random.randint(10, 30)))

    organizer = Organizer()

    rooms, unassigned = organizer.assign(big_rooms, big_events, iterations=400, swap_num=10, temperature=10, print_level="epoch")

    print(str((100-(len(unassigned)/num_events)*100))+"% Assigned")

    suggester = algorithm_II.Suggester(rooms, unassigned)

    parameters = [(5, 0, 0, 400), (10, 0.5, 0.25, 300), (20, 1, 0.25, 200), (30, 2, 0.5, 100), (40, 4, 0.75, 0)]
    
    suggestions, still_unassigned = suggester.weightedGridSearch(parameters)

    for suggestion in suggestions:
        print(suggestion[0], suggestion[1])
    
    print("\n" + str(len(still_unassigned)), len(suggestions), len(unassigned)-len(suggestions))
