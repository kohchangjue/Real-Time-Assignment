
from FEL import FEL
from tello_sim import Simulator
import threading
from time import sleep
# num_processors = 1
# execution_times = [160, 48, 40, 48, 56, 80, 10]
# periods = [1600, 2560, 120, 96, 168, 240, 100]
#
# READY_STATUS = 0
# RUNNING_STATUS = 1


'''
rules:

1 unit time will move 10 unit instance 
all period for predefined route is same (lowest priority) ---> periodic
period for checking obstacle is shorter (higher priority)
interrupt has shotest period (highest priority, result preempt)
interrupt include (keyboard,obstacle observer) --->aperiodic
'''

# Flight path to Checkpoint 1 to 5 and back to Checkpoint 0 sequentially
task = [
    ['takeoff'],
    ["ccw", 150],
    ["forward", 50],
    ["cw", 90],
    ["forward", 100],
    ["ccw", 90],
    ["forward", 80],
    ["ccw", 90],
    ["forward", 40],
    ["ccw", 90],
    ["forward", 40],
    ["cw", 90],
    ["forward", 60],
    ["ccw", 90],
    ["forward", 40],
    ["ccw", 150],
    ["forward", 50] #to base
]
num_processors = 1

execution_times = [1,1,1,1, 10,1, 8, 1,4, 1,4, 1,6,1,4,1,5]
periods = [75,75, 75, 75, 75, 75, 75, 75,75,75,75,75, 75, 75,75,75,75]
arrive_time = [0,1,2,3,4,14,15,23,24,28,29,33,34,40,41,45,46]
READY_STATUS = 0
RUNNING_STATUS = 1
drone = Simulator()
arrival_events = FEL()
deadlines_met = {}

for i in range(len(execution_times)):
    deadlines_met[i]=False

class Process:
    def __init__(self, number, deadline, time_left, period,command):
        self.id = number
        self.deadline = deadline
        self.time_left = time_left
        self.period = period
        self.status = READY_STATUS  # 0 for ready, 1 for running
        self.command = command

class RMS:
    def __init__(self):
        assert num_processors >= 1
        assert len(execution_times) >= 1
        assert len(execution_times) == len(periods)
        self.current_time = 0

    def insertInterruptTask(self,curr_time,id,command):
        arrival_events.addEvent(curr_time,
                                    lambda id=id:Process(id, curr_time+5, 1,
                                                        0, command))
        deadlines_met[id-1]=False
        print('\n','------preemption happen------','\n')

    def schedular_wrapper(self):
        threading.Thread(target=self.buildSchedule()).start()

    def build_predefined_route(self,current_time):
        # first, find the largest period
        # (if we can meet all deadlines over this time, we always meet deadlines)
        max_period = max(periods)
        # next, get all the arrival times for each process

        for i in range(len(execution_times)):
            next_time = arrive_time[i]+current_time
            while next_time <= max_period:
                arrival_events.addEvent(next_time,
                                        lambda i=i: Process(i + 1, self.current_time + periods[i], execution_times[i],
                                                            periods[i], task[i]))
                next_time += periods[i]

    def buildSchedule(self):
        # this list will represent processes currently in the system
        processes = list()

        # this list will keep track of which process have met thier first deadline
        ## if all processes met their first deadline in the first max period, then we can stop early
        # deadlines_met = [False] * len(execution_times)

        running_process_set = {}
        # now we simulate processes running

        # for time in range(0, max_period):
        time = 0
        while(True):
            self.current_time = time
            if(len(arrival_events.events) == 0):
                sleep(2)
            # decrement time left for each running process
            for process in processes:
                if process.status == RUNNING_STATUS:
                    for command in process.command:
                        if command == 'takeoff':
                            # print('takeoff')
                            drone.takeoff()
                        if command == 'land':
                            # print('takeoff')
                            drone.land()
                        if command== 'cw':
                            # print('cw',process.command[1])
                            drone.cw(process.command[1])
                        if command == 'ccw':
                            # print('ccw',process.command[1])
                            drone.ccw(process.command[1])
                        if command == 'forward':
                            # print('forward',10)
                            drone.forward(10)
                        if command == 'backward':
                            # print('forward',10)
                            drone.back(process.command[1])
                        if command == 'left':
                            drone.left(process.command[1])
                        if command == 'right':
                            drone.right(process.command[1])
                        if command == 'up':
                            drone.up(process.command[1])
                        if command == 'down':
                            drone.down(process.command[1])

                    process.time_left -= 1

            # remove any processes that have finished execution
            for process in processes:
                if process.status == RUNNING_STATUS and process.time_left == 0:
                    processes.remove(process)
                    print("process", process.id, "completed at time", time)
                    if deadlines_met[process.id - 1] == False:
                        deadlines_met[process.id - 1] = True

            # check if we have missed any deadlines
            for process in processes:
                if process.deadline <= time:
                    print("deadline missed for process", process.id, "at time", time)
                    return

            # check if all deadlines have been met once in thie first period
            if sum(1 for met in deadlines_met if not met) == 0:
                print("all deadlines met within", time, "milliseconds with", num_processors, "processors")
                return

            while len(arrival_events.events)>0 and arrival_events.events[0].time == time:
                p = arrival_events.popEvent().function()
                print("process", p.id, "arriving at time", time)
                processes.append(p)

                # if there is an idle processor, run the process with the shortest period
            sorted_processes = sorted(processes, key=lambda p: p.period)
            ready_processes = [p for p in sorted_processes if p.status == READY_STATUS]
            while sum(1 for p in processes if p.status == RUNNING_STATUS) < num_processors and len(ready_processes) > 0:
                ready_processes = [p for p in sorted_processes if p.status == READY_STATUS]
                if len(ready_processes) > 0:
                    ready_processes[0].status = RUNNING_STATUS

            # if any of the ready processes have periods shorter than any running process, swap the processes
            for p in sorted_processes:
                p.status = READY_STATUS
            for i in range(min(num_processors, len(sorted_processes))):
                sorted_processes[i].status = RUNNING_STATUS

            running_processes = [p.id for p in sorted_processes if p.status == RUNNING_STATUS]
            if running_process_set != running_processes:
                running_process_set = running_processes
                print("time:", time, running_processes, "now running",'\n')

            time = time + 1


        print("all deadlines met for", max_period, "milliseconds with", num_processors, "processors")


# RMS()
#


# my_drone = Simulator()
# my_drone.takeoff()
# my_drone.send_command("forward", 50)
# my_drone.cw(45)
# my_drone.forward(40)
# my_drone.ccw(45)
# my_drone.forward(40)
# my_drone.cw(45)
# my_drone.forward(80)