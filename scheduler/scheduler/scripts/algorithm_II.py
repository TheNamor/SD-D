"""
This document contains the module that makes the best suggestions to encorporate unassigned rooms

Authors:
    Roman Nett

"""

class Suggester(object):

    def __init__(self, rooms, unassigned):
        """
        Creates a suggester for a set of rooms and unassigned events

        Arguments-
        rooms (list):           list of rooms with assigned events
        unassigned (list):      list of unassigned events
        """
        self.rooms = rooms
        self.unassigned = sorted(unassigned)
        self.capacity_tolerance = None
        self.self_tolerance = None
        self.event_tolerance = None
        self.event_length_tolerance = None
        self.suggestions = []

    def getShortest(self):
        """
        Returns the shortest unassigned event, for effeciency purposes - UNTESTED

        Returns-
        (float):        the length of the shortest event, in hours
        """
        return min([event.getLength() for event in self.unassigned])
    
    def checkMove(self, room, index, difference):
        """
        Checks whether an event can be legally shifted within a room

        Arguments-
        room (Room):            Room object whose event we are shifting
        index (int):            the index of the event being shifted
        difference (float):     the amount we are trying to shift the event by

        Returns-
        (bool):         Whether the event can be shifted and still be in a valid position
        """
        if abs(difference) > self.event_tolerance:
            return False
        move_by = difference
        events = room.events
        event = events[index]
        new_start, new_end = event.starts + move_by, event.ends + move_by
        valid_start = new_start >= room.opens and (index == 0 or new_start >= events[index-1].ends)
        valid_end = new_end <= room.closes and (index == len(events)-1 or new_end <= events[index+1].starts)
        return valid_start and valid_end
    
    def checkFit(self, room, starts, ends, difference, index=None):
        """
        Checks whether an event can fit into a room

        Arguments-
        room (Room):        room that is being checked
        starts (float):     when the event starts
        ends (float):       when the event ends
        difference (float): how much the event is shifted

        Named Arguments-
        index (int)=None:       optional index to fit the event into

        Returns-
        (bool):         whether the event can be legally fit into the room
        """
        if abs(difference) > self.self_tolerance:
            return False
        
        starts += difference
        ends += difference

        if starts < room.opens or ends > room.closes:
            return False
        
        if len(room.events) == 0:
            return True
        
        if index is None:
            if ends <= room.events[0].starts:
                return True
            for i in range(len(room.events)-1):
                if starts >= room.events[i].ends and ends <= room.events[i+1].starts:
                    return True
            if starts >= room.events[-1].ends:
                return True
        else:
            if (index == 0 or starts >= room.events[index-1].ends) and (index >= len(room.events) or ends <= room.events[index].starts):
                return True
        
        return False
    
    def generate(self, capacity_tolerance=5, self_tolerance=1, event_tolerance=0.5, event_length_tolerance=0.25, booster=0):
        """
        Generates a list of suggestions with quality scores that assign as many unassigned events as possible
        Suggestions follow the form (score, suggestion, event(s), room)

        Named Arguments-
        capacity_tolerance (int)=5:             the maximum additional capacity that will be suggested
        event_tolerance (float)=0.5:            the most an event will be suggested to be moved by
        event_length_tolerance (float)=0.25:    the most an event's length will be suggested to be changed by

        Returns-
        (list):         list of suggestion tuples
        """
        # Assigning parameters
        self.capacity_tolerance = capacity_tolerance
        self.self_tolerance = self_tolerance
        self.event_tolerance = event_tolerance
        self.event_length_tolerance = event_length_tolerance

        # First check if more events can be fit in by changing the room capacities
        for room in self.rooms:
            room_list = [event for event in room.events]
            new_suggestion = [55, ["capacity", 0], [], room]
            assigned = True
            # Continues looking for open spots until no events can fit in
            while assigned and len(self.unassigned):
                assigned = False
                # For each unassigned event
                for i in range(len(self.unassigned)):
                    event = self.unassigned[i]
                    # Skip events that have attendance above the allowed capacity
                    if event.attendance > room.capacity + self.capacity_tolerance:
                        continue
                    # Add events to empty rooms
                    if len(room_list) == 0:
                        if event.starts >= room.opens and event.ends <= room.closes:
                            room_list.append(event)
                            if event.attendance-room.capacity > new_suggestion[1][1]:
                                new_suggestion[1][1] = event.attendance-room.capacity
                            new_suggestion[2].append(self.unassigned.pop(i))
                            assigned = True
                            break
                    else:
                        # Check before the first event
                        if event.starts >= room.opens and event.ends <= room_list[0].starts:
                            room_list.insert(0, event)
                            if event.attendance-room.capacity > new_suggestion[1][1]:
                                new_suggestion[1][1] = event.attendance-room.capacity
                            new_suggestion[2].append(self.unassigned.pop(i))
                            assigned = True
                            break
                        
                        # Check in between each pair of events
                        for j in range(len(room_list)-1):
                            event_before = room_list[j]
                            event_after = room_list[j+1]
                            if event_before.ends <= event.starts and event.ends <= event_after.starts:
                                room_list.insert(j+1, event)
                                if event.attendance-room.capacity > new_suggestion[1][1]:
                                    new_suggestion[1][1] = event.attendance-room.capacity
                                new_suggestion[2].append(self.unassigned.pop(i))
                                assigned = True
                                break
                        if assigned: break
                        
                        # Check after the last event
                        if event.starts >= room_list[-1].ends and event.ends <= room.closes:
                            room_list.append(event)
                            if event.attendance-room.capacity > new_suggestion[1][1]:
                                new_suggestion[1][1] = event.attendance-room.capacity
                            new_suggestion[2].append(self.unassigned.pop(i))
                            assigned = True
                            break
            
            if len(new_suggestion[2]) > 0:
                new_suggestion[0] += len(new_suggestion[2])
                self.suggestions.append(new_suggestion)
        
        # Next check if events can be fit in by moving the event itself
        for room in self.rooms:
            # Assuming only 1 extra event can get fit in per suggestion
            # For each unassigned event
            new_unassigned = []
            for i in range(len(self.unassigned)):
                event = self.unassigned[i]
                assigned = False
                # Skip events that have attendance above the allowed capacity
                if event.attendance > room.capacity + self.capacity_tolerance:
                    new_unassigned.append(event)
                    continue
                capacity_diff = event.attendance - room.capacity
                    
                # Check if event is out of bounds
                if event.starts < room.opens:
                    difference = room.opens - event.starts
                    if self.checkFit(room, event.starts, event.ends, difference, index=0):
                        if capacity_diff > 0:
                            self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "self shift", difference), [event], room])
                        else:
                            self.suggestions.append([50-abs(difference), ("self shift", difference), [event], room])
                        continue
                    new_unassigned.append(event)
                    continue
                elif event.ends > room.closes:
                    difference = room.closes - event.ends
                    if self.checkFit(room, event.starts, event.ends, difference, index=(len(room.events))):
                        if capacity_diff > 0:
                            self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "self shift", difference), [event], room])
                        else:
                            self.suggestions.append([50-abs(difference), ("self shift", difference), [event], room])
                        continue
                    new_unassigned.append(event)
                    continue
                
                # Skip empty rooms as they will have been filled by now
                if len(room.events) == 0:
                    continue

                # Check before first event
                difference = room.events[0].starts - event.ends
                if self.checkFit(room, event.starts, event.ends, difference, index=0):
                    if capacity_diff > 0:
                        self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "self shift", difference), [event], room])
                    else:
                        self.suggestions.append([50-abs(difference), ("self shift", difference), [event], room])
                    continue
                
                # Check in between each pair of events
                for j in range(len(room.events)-1):
                    event_before = room.events[j]
                    event_after = room.events[j+1]
                    before, after = event.starts >= event_before.ends, event.ends <= event_after.starts
                    # Overlap on both sides
                    if not before and not after:
                        continue
                    # Overlap with just before event
                    difference = event_before.ends - event.starts
                    if not before:
                        if self.checkFit(room, event.starts, event.ends, difference, index=j+1):
                            if capacity_diff > 0:
                                self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "self shift", difference), [event], room])
                            else:
                                self.suggestions.append([50-abs(difference), ("self shift", difference), [event], room])
                            assigned = True
                            break
                    # Overlap with just after event
                    difference = event_after.starts - event.ends
                    if not after:
                        if self.checkFit(room, event.starts, event.ends, difference, index=j+1):
                            if capacity_diff > 0:
                                self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "self shift", difference), [event], room])
                            else:
                                self.suggestions.append([50-abs(difference), ("self shift", difference), [event], room])
                            assigned = True
                            break
                if assigned:
                    continue
                
                # Check after last event
                difference = room.events[-1].ends - event.starts
                if self.checkFit(room, event.starts, event.ends, difference, index=len(room.events)):
                    if capacity_diff > 0:
                        self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "self shift", difference), [event], room])
                    else:
                        self.suggestions.append([50-abs(difference), ("self shift", difference), [event], room])
                    continue

                new_unassigned.append(event)
            self.unassigned = new_unassigned

        # Next check if events can be fit in by moving nearby event times
        for room in self.rooms:
            # Assuming only 1 extra event can get fit in per suggestion

            # No need to check for empty rooms as those will have been filled by the capacity step
            if len(room.events) == 0:
                continue

            # For each unassigned event
            new_unassigned = []
            for i in range(len(self.unassigned)):
                event = self.unassigned[i]
                assigned = False
                # Skip events that have attendance above the allowed capacity
                if event.attendance > room.capacity + self.capacity_tolerance:
                    new_unassigned.append(event)
                    continue
                capacity_diff = event.attendance - room.capacity

                # Check before the first event
                difference = event.ends-room.events[0].starts
                if event.starts >= room.opens and self.checkMove(room, 0, difference):
                    if capacity_diff > 0:
                        self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "shift", 0, difference), [event], room])
                    else:
                        self.suggestions.append([50-abs(difference), ("shift", 0, difference), [event], room])
                    continue
                
                # Check in between each pair of events
                for j in range(len(room.events)-1):
                    event_before = room.events[j]
                    event_after = room.events[j+1]
                    before, after = event.starts >= event_before.ends, event.ends <= event_after.starts
                    # If after event doesn't have to change, just move before event
                    difference = event.starts - event_before.ends
                    if not before and self.checkMove(room, j, difference) and after:
                        if capacity_diff > 0:
                            self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "shift", j, difference), [event], room])
                        else:
                            self.suggestions.append([50-abs(difference), ("shift", j, difference), [event], room])
                        assigned = True
                        break
                    # If before event does't have to change, just move after event
                    difference = event.ends - event_after.starts
                    if not after and self.checkMove(room, j+1, difference) and before:
                        if capacity_diff > 0:
                            self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "shift", j+1, difference), [event], room])
                        else:
                            self.suggestions.append([50-abs(difference), ("shift", j+1, difference), [event], room])
                        assigned = True
                        break
                    # Move both events if necessary
                    difference_before = event.starts - event_before.ends
                    difference_after = event.ends - event_after.starts
                    if not after and not before and self.checkMove(room, j, difference_before) and self.checkMove(room, j+1, difference_after):
                        if capacity_diff > 0:
                            self.suggestions.append([40-abs(difference_before)-abs(difference_after)-4, ("capacity", capacity_diff, "shift", j, difference_before, j+1, difference_after), [event], room])
                        else:
                            self.suggestions.append([40-abs(difference_before)-abs(difference_after), ("shift", j, difference_before, j+1, difference_after), [event], room])
                        assigned = True
                        break
                if assigned:
                    continue
                
                # Check after the last event
                difference = event.starts - room.events[-1].ends
                if self.checkMove(room, len(room.events)-1, difference) and event.ends <= room.closes:
                    if capacity_diff > 0:
                        self.suggestions.append([50-abs(difference)-4, ("capacity", capacity_diff, "shift", -1, difference), [event], room])
                    else:
                        self.suggestions.append([50-abs(difference), ("shift", -1, difference), [event], room])
                    continue

                new_unassigned.append(event)
            self.unassigned = new_unassigned
        
        # Finally check if events can be fit by modifying nearby event lengths
        for room in self.rooms:
            # Assuming only 1 extra event can get fit in per suggestion

            # No need to check for empty rooms as those will have been filled by the capacity step
            if len(room.events) == 0:
                continue

            # For each unassigned event
            new_unassigned = []
            for i in range(len(self.unassigned)):
                event = self.unassigned[i]
                assigned = False
                # Skip events that have attendance above the allowed capacity
                if event.attendance > room.capacity + self.capacity_tolerance:
                    new_unassigned.append(event)
                    continue
                capacity_diff = event.attendance - room.capacity

                # Check before the first event
                difference = event.ends-room.events[0].starts
                if event.starts >= room.opens and event.ends < room.events[0].ends and abs(difference) <= self.event_length_tolerance:
                    if capacity_diff > 0:
                        self.suggestions.append([45-abs(difference)-4, ("capacity", capacity_diff, "length", 0, difference), [event], room])
                    else:
                        self.suggestions.append([45-abs(difference), ("length", 0, difference), [event], room])
                    continue
                
                # Check in between each pair of events
                for j in range(len(room.events)-1):
                    event_before = room.events[j]
                    event_after = room.events[j+1]
                    before, after = event.starts >= event_before.ends, event.ends <= event_after.starts
                    # If after event doesn't have to change, just move before event
                    difference = event.starts - event_before.ends
                    if not before and event_before.starts < event.starts and after and abs(difference) <= self.event_length_tolerance:
                        if capacity_diff > 0:
                            self.suggestions.append([45-abs(difference)-4, ("capacity", capacity_diff, "length", j, difference), [event], room])
                        else:
                            self.suggestions.append([45-abs(difference), ("length", j, difference), [event], room])
                        assigned = True
                        break
                    # If before event does't have to change, just move after event
                    difference = event.ends - event_after.starts
                    if not after and event.ends < event_after.ends and before and abs(difference) <= self.event_length_tolerance:
                        if capacity_diff > 0:
                            self.suggestions.append([45-abs(difference)-4, ("capacity", capacity_diff, "length", j+1, difference), [event], room])
                        else:
                            self.suggestions.append([45-abs(difference), ("length", j+1, difference), [event], room])
                        assigned = True
                        break
                    # Move both events if necessary
                    difference_before = event.starts - event_before.ends
                    difference_after = event.ends - event_after.starts
                    if not after and not before and event_before.starts < event.starts and event.ends < event_after.ends and abs(difference_before) <= self.event_length_tolerance and abs(difference_after) <= self.event_length_tolerance:
                        if capacity_diff > 0:
                            self.suggestions.append([35-abs(difference_before)-abs(difference_after)-4, ("capacity", capacity_diff, "length", j, difference_before, j+1, difference_after), [event], room])
                        else:
                            self.suggestions.append([35-abs(difference_before)-abs(difference_after), ("length", j, difference_before, j+1, difference_after), [event], room])
                        assigned = True
                        break
                if assigned:
                    continue
                
                # Check after the last event
                difference = event.starts - room.events[-1].ends
                if room.events[-1].starts < event.starts and event.ends <= room.closes and abs(difference) <= self.event_length_tolerance:
                    if capacity_diff > 0:
                        self.suggestions.append([45-abs(difference)-4, ("capacity", capacity_diff, "length", -1, difference), [event], room])
                    else:
                        self.suggestions.append([45-abs(difference), ("length", -1, difference), [event], room])
                    continue
                new_unassigned.append(event)
            self.unassigned = new_unassigned
        
        for suggestion in self.suggestions:
            suggestion[0] += booster

        return self.suggestions

    def weightedGridSearch(self, parameters):
        """
        Finds suggestions over a list of parameters where the parameters become less and less strict

        Arguments-
        parameters (list):      list of lists of parameters where an entry is in form (capacity_tolerance, self_tolerance, event_tolerance, event_length_tolerance, booster)
        
        Returns-
        (list):         list of suggestions sorted by score from best to worst
        """

        suggestions = []

        for parameter in parameters:

            if len(self.unassigned) == 0:
                break

            new_suggestions = self.generate(
                capacity_tolerance=parameter[0],
                self_tolerance = parameter[1],
                event_tolerance=parameter[2],
                event_length_tolerance=parameter[3],
                booster=parameter[4]
            )
            
            suggestions += new_suggestions
            self.suggestions = []
        
        return sorted(suggestions, key=lambda x: (x[0], -x[1][-1]), reverse=True), self.unassigned