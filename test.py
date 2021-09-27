from algorithm_I import *
import time
import numpy as np

time_data = []
unassigned_data = []

for n in range(200):
    print("Collecting datapoint #" + str(n+1))

    # Generate a random number of rooms and events and create their objects
    # Rooms have a capacity between 10 and 30, opens between 8am and 10am, closes between 3pm and 6pm
    # Events start between 8am and 3pm, are between 1 and 3 hours long, and have between 10 and 30 attendees
    big_rooms = []
    big_events = []
    num_rooms = random.randrange(1, 400)
    num_events = random.randrange(1, 400)

    for i in range(num_rooms):
        big_rooms.append(Room("Room " + str(i), random.randint(10, 30), opens=random.randint(8, 10), closes=random.randint(15, 18)))

    for i in range(num_events):
        start = random.randint(8, 14) + random.random()
        length = random.randint(1, 2) + random.random()
        big_events.append(Event("Event " + str(i), start, start+length, random.randint(10, 30)))

    # Find the time of the solution
    time1 = time.time()
    rooms, unassigned, evals = assign(big_rooms, big_events, iterations=100, swap_num=10, temperature=10, print_level="none")
    time2 = time.time()

    time_data.append((num_events, num_rooms, time2-time1))
    unassigned_data.append((num_events, num_rooms, len(unassigned)/num_events))

from matplotlib import pyplot
from scipy.stats.stats import pearsonr
from scipy.optimize import curve_fit

# Find the correlations for the time data
y = [x[2] for x in time_data]
events = [x[0] for x in time_data]
rooms = [x[1] for x in time_data]
mult = [x[0]*x[1] for x in time_data]
add = [x[0] + x[1] for x in time_data]

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

# Find the correlations for the evaluation data
y = [x[2] for x in unassigned_data]
events = [x[0] for x in unassigned_data]
rooms = [x[1] for x in unassigned_data]
ratio = [x[0]/x[1] for x in unassigned_data]
sub = [x[0] - x[1] for x in unassigned_data]

ind = ratio.index(max(ratio))

print("Linear Correlations:")
print("\tJust Events:\t", pearsonr(events, y))
print("\tJust Rooms:\t", pearsonr(rooms, y))
print("\tRatio:\t\t", pearsonr(ratio, y))
print("\tSubtracted:\t", pearsonr(sub, y))

fit = curve_fit(lambda t,a,b: a + b*np.log(t),  ratio,  y)[0]

print("y =", fit[0], "+", str(fit[1]) + "*log(x)")

fit_x = range(1, int(max(ratio)))
fit_y = [fit[0] + fit[1]*np.log(x) for x in fit_x]
corr_y = [fit[0] + fit[1]*np.log(x) for x in ratio]

print("Logarithmic Fit:")
print("\tRatio:\t\t", pearsonr(corr_y, y))
pyplot.plot(fit_x, fit_y)
pyplot.scatter(ratio, y, marker='.', linewidths=0.1)
pyplot.xlabel('Ratio of Events to Rooms')
pyplot.ylabel('Ratio Unassigned')
pyplot.title("Data vs Logarithmic Fit")
pyplot.show()