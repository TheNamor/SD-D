from algorithm_I import *
import time
import numpy as np

time_data = []
unassigned_data = []
baseline_data = []

def checkRooms(room_list):
    errors = 0
    for room in room_list:
        room.events.sort()
        for i in range(1, len(room.events)):
            event1 = room.events[i-1]
            event2 = room.events[i]
            if event1.ends > event2.starts:
                error += 1
    return errors/len(room_list)
                

iterations = 100
organizer = Organizer()

for n in range(500):
    print("Collecting datapoint #" + str(n+1))

    # Generate a random number of rooms and events and create their objects
    # Rooms have a capacity between 10 and 30, opens between 8am and 10am, closes between 3pm and 6pm
    # Events start between 8am and 3pm, are between 1 and 3 hours long, and have between 10 and 30 attendees
    big_rooms = []
    big_events = []
    num_rooms = random.randint(100, 200)#10 + n
    num_events = int(num_rooms*(random.randint(1, 3) + random.random()))

    for i in range(num_rooms):
        big_rooms.append(Room("Room " + str(i), random.randint(10, 30), opens=random.randint(8, 10), closes=random.randint(15, 18)))

    for i in range(num_events):
        start = random.randint(8, 14) + random.random()
        length = random.randint(1, 2) + random.random()
        big_events.append(Event("Event " + str(i), start, start+length, random.randint(10, 30)))

    # Find the greedy solution
    greedy_solution, greedy_unassigned = organizer.findSolution(big_rooms, big_events.copy())

    # Find the time of the solution
    time1 = time.time()
    rooms, unassigned = organizer.assign(big_rooms, big_events, iterations=iterations, swap_num=10, temperature=10, print_level="none")
    time2 = time.time()

    #print("Average", checkRooms(rooms), "errors per room")

    time_data.append((num_events, num_rooms, time2-time1))
    unassigned_data.append((num_events, num_rooms, len(unassigned)/num_events))
    baseline_data.append(len(greedy_unassigned)/num_events)

from matplotlib import pyplot
from scipy.stats.stats import pearsonr
from scipy.optimize import curve_fit

# Find the correlations for the time data
y = [x[2] for x in time_data]
events = [x[0] for x in time_data]
rooms = [x[1] for x in time_data]
mult = [x[0]*x[1] for x in time_data]
add = [x[0] + x[1] for x in time_data]

print("******************************************")
print("TIME DATA")
print("******************************************")
print("Linear Correlations:")
print("\tJust Events:\t", pearsonr(events, y))
print("\tJust Rooms:\t", pearsonr(rooms, y))
print("\tMultiplied:\t", pearsonr(mult, y))
print("\tAdded:\t\t", pearsonr(add, y))

fit = curve_fit(lambda t,a,b: a*b**t,  events,  y)[0]

print("y =", fit[0], "*", str(fit[1]) + "^x")

fit_x = range(max(events))
fit_y = [fit[0]*fit[1]**x for x in fit_x]
corr_y = [fit[0]*fit[1]**x for x in events]

print("Exponential Correlation:")
print("\tJust Events:\t", pearsonr(corr_y, y))
pyplot.scatter(events, y, marker='.', linewidths=0.1)
pyplot.plot(fit_x, fit_y)
pyplot.xlabel('Events')
pyplot.ylabel('Time (s)')
pyplot.title("Data vs Exponential Fit")
pyplot.show()

print("******************************************")
print("ACCURACY DATA")
print("******************************************")

# Find the correlations for the evaluation data
y = [x[2] for x in unassigned_data]
events = [x[0] for x in unassigned_data]
rooms = [x[1] for x in unassigned_data]
ratio = [x[0]/x[1] for x in unassigned_data]
sub = [x[0] - x[1] for x in unassigned_data]

print("Linear Correlations:")
print("\tJust Events:\t", pearsonr(events, y))
print("\tJust Rooms:\t", pearsonr(rooms, y))
print("\tRatio:\t\t", pearsonr(ratio, y))
print("\tSubtracted:\t", pearsonr(sub, y))

fit = curve_fit(lambda t,a,b: a + b*t,  ratio,  y)[0]

print("y =", fit[0], "+", str(fit[1]) + "*x")

fit_x = np.array(range(1, int(max(ratio))+2))
fit_y = [fit[0] + fit[1]*x for x in fit_x]
corr_y = [fit[0] + fit[1]*x for x in ratio]

print("Linear Fit:")
print("\tRatio:\t\t", pearsonr(corr_y, y))
pyplot.plot(fit_x, fit_y)
pyplot.scatter(ratio, y, marker='.', linewidths=0.1)
pyplot.xlabel('Ratio of Events to Rooms')
pyplot.ylabel('Ratio Unassigned')
pyplot.title("Data vs Linear Fit")
pyplot.show()

rooms = [x[1] for x in unassigned_data]
events = [x[0] for x in unassigned_data]

pyplot.scatter(rooms, events, marker='.', linewidths=0.1)
pyplot.xlabel('# of Rooms')
pyplot.ylabel('# of Events')
pyplot.title("Events vs Rooms")
pyplot.show()

y = [(1-x[2])*100 for x in unassigned_data]
times = [x[2] for x in time_data]

print("Average % assigned:\t", sum(y)/len(y))
print("Standard deviation:\t", np.std(y))
print("Average time per iteration (s):\t", sum(times)/len(times)/iterations)

y = [(1-x)*100 for x in baseline_data]

print("Greedy Solution:")
print("\tAverage % assigned:\t", sum(y)/len(y))
print("\tStandard deviation:\t", np.std(y))

pyplot.hist(y)
pyplot.xlabel('% Assigned')
pyplot.show()