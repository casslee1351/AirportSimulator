import simpy
import random
from statistics import mean

random.seed(42)

# globals
total_passengers = 0
checker_times = []
scanner_times = []
total_times = []
num_checkers = 37
num_scanners = 37

# number of replications
NUM_REPL = 50

class Airport(object):
    def __init__(self, env, num_checkers, check_rate, num_scanners, scan_rate):
        self.env = env
        self.num_checkers = num_checkers
        self.check_rate = check_rate
        self.num_scanners = num_scanners
        self.scan_rate = scan_rate

        # checkers are one block with multiple resources
        self.checker = simpy.Resource(env, self.num_checkers)


        self.scanner = []
        for i in range(self.num_scanners):
            # each scanner only has 1 resource
            self.scanner.append(simpy.Resource(env, 1))

  # checking process
    def check(self, passenger):
        yield self.env.timeout(random.expovariate(1.0/self.check_rate))

    # scanning process
    def scan(self, passenger):
        yield self.env.timeout(random.uniform(self.scan_rate[0], self.scan_rate[1]))


# how the passenger passes through the security system
def passenger(env, passenger_name, airport):
    # some more globals
    global scan_time
    global check_time
    global total_time
    global total_passengers

    time_arrive = env.now 
    wait_check_time = 0
    time_checked = 0
    wait_scan_time = 0
    time_scanned = 0

    with airport.checker.request() as request:
        yield request
        check_start = env.now
        wait_check_time = check_start - time_arrive

        # check the passenger
        yield env.process(airport.check(passenger_name))
        # time spent in check queue
        check_end = env.now
        time_checked = check_end- check_start

    min_scan_que = 0
    for i in range(1, num_scanners):
        if (len(airport.scanner[i].queue) < len(airport.scanner[min_scan_que].queue)):
            min_scan_que = i

    with airport.scanner[min_scan_que].request() as request:
        yield request
        scan_start = env.now
        wait_scan_time = scan_start - check_end

        # check the passenger
        yield env.process(airport.scan(passenger_name))
        # time spent in check queue
        time_scanned = env.now - scan_start

    
    # save these queue times
    checker_times.append([wait_check_time, time_checked])
    scanner_times.append([wait_scan_time, time_scanned])
    total_times.append(env.now - time_arrive)
    total_passengers += 1


def PassengerArrive(env, airport, arrival_rate):
    global total_passengers
    num_passengers = 0

    while True:
        yield env.timeout(random.expovariate(arrival_rate))
        num_passengers += 1
        total_passengers += 1

        # create the passenger using process()
        env.process(passenger(env, f'Passenger {num_passengers}', airport))
        

for i in range(0, NUM_REPL):
    # declare SimPy Environment
    env = simpy.Environment()

    airport = Airport(env, num_checkers, 0.75, num_scanners, [0.5, 1])
    env.process(PassengerArrive(env, airport, 50))

    env.run(8*60)
    

print(f'Average number of passengers {total_passengers/NUM_REPL}')
avg_check_wait = round(mean(list(zip(*checker_times))[0]),2)
avg_check_time = round(mean(list(zip(*checker_times))[1]),2)
avg_scan_wait = round(mean(list(zip(*scanner_times))[0]),2)
avg_scan_time = round(mean(list(zip(*scanner_times))[1]),2)
avg_sys_time = round(mean(total_times),2)
print(f'Avg check wait time {avg_check_wait}')
print(f'Avg check time {avg_check_time}')
print(f'Avg scan wait time {avg_scan_wait}')
print(f'Avg scan time {avg_scan_time}')
print(f'Avg sys time {avg_sys_time}')