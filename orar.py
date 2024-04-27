import sys
import utils
import check_constraints
import copy
import math
from functools import cmp_to_key
from heapq import heappush, heappop

def generate_neighbours(curr_state):
    global astar_options
    neighbours = []

    curr_neighbour = []
    if len(curr_state) != 0:
        curr_neighbour += curr_state

    for option in astar_options:
        if solution_cost(option[1:], curr_neighbour) < 1000:
            curr_neighbour.append(option)
        if len(curr_neighbour) == len(curr_state) + 1:
            neighbours.append(curr_neighbour)
            curr_neighbour = []
            curr_neighbour += curr_state

    return neighbours

# def heuristic(timetable):
#     # assigned_subjects = set(slot[0] for slot in timetable)
#     global rooms
#     global subjects
#     unassigned_subjects = set(list(lambda subj: subjects[subj] > 0, filter(subjects.keys())))
#     return len(unassigned_subjects
def transition_cost(neighbour):
    global soft_constraints
    cost_neighbour = 1
    for slot in neighbour:
        if slot[1] not in soft_constraints[teacher]['preffered_days']:
            cost_neighbour += 1
        if slot[2] not in soft_constraints[teacher]['preffered_intervals']:
            cost_neighbour += 1

    return cost_neighbour
               

def heuristic(timetable):
    global rooms
    global subjects   

    total_studs_assigned = {}
    for subject in subjects.keys():
        total_studs_assigned[subject] = 0

    for slot in timetable:
        total_studs_assigned[slot[0]] += rooms[slot[3]]['Capacitate']

    max_classroom_capacity = {subject: max(room_details['Capacitate'] for room_details in rooms.values() if subject in room_details[utils.MATERII]) for subject in subjects.keys()}
    slots_needed = {subject: math.ceil((subjects[subject] - total_studs_assigned[subject]) / max_classroom_capacity[subject]) if subjects[subject] - total_studs_assigned[subject] > 0 else 0 for subject in subjects.keys()}

    cost = sum(slots_needed.values())
    return cost


def is_final(timetable):
    global rooms
    global total_studs

    total_studs_assigned = {}
    for subject in subjects.keys():
        total_studs_assigned[subject] = 0
    
    diff_studs = {subject: subjects[subject] - total_studs_assigned[subject] for subject in subjects.keys()}
    return sum(diff_studs.values()) <= 0
    

def is_in_discovered(timetable, discovered):
    # timetable_set = set(timetable)
    for state in discovered:
        if set(state[0]) == set(timetable):
            return True
    return False

def get_g(timetable, discovered):
    for index, state in enumerate(discovered):
        if set(state[0]) == set(timetable):
            return state[1], index
    return -1, -1


def print_heap(heap):
    for elem in heap:
        print(f'timetable {elem[0]}, cost {elem[1]}')

def astar(initial_state):
    opened = []
    heappush(opened, (0 + heuristic(initial_state), initial_state))
    # print(opened)
    discovered = []
    discovered.append((initial_state, 0))

    while opened:
        #  DEBUG
        # input()
        print_heap(opened)
        
        curr_cost, curr_state = heappop(opened)
        print(f'\nCurrent state {curr_state} with cost {curr_cost}')
        print()
        # input()

        if is_final(curr_state):
            return curr_state

        for neighbour in generate_neighbours(curr_state):
            g_neighbour, index_neighbour = get_g(neighbour, discovered)
            g_curr_state, index_curr_state = get_g(curr_state, discovered)
            if is_in_discovered(neighbour, discovered) and g_curr_state + transition_cost(neighbour) < g_neighbour:
                print(f'Updated neighbour {neighbour} with cost {g_curr_state + transition_cost(neighbour) + heuristic(neighbour)}')
                discovered.pop(index_neighbour)
                discovered.append((neighbour, g_curr_state + transition_cost(neighbour)))
                heappush(opened, (g_curr_state + transition_cost(neighbour) + heuristic(neighbour), neighbour))
            elif not is_in_discovered(neighbour, discovered):
                print(f'Added neighbour {neighbour} with cost {g_curr_state + transition_cost(neighbour) + heuristic(neighbour)}')
                discovered.append((neighbour, g_curr_state + transition_cost(neighbour)))
                heappush(opened, (g_curr_state + transition_cost(neighbour) + heuristic(neighbour), neighbour))
    
    return None


# ****************** CSP ******************
def check_subject_teacher_compatibility (subject, teacher, teachers):
    return subject in teachers[teacher][utils.MATERII]

def check_subject_room_compatibility (subject, room, subjects, rooms):
    if subject in rooms[room][utils.MATERII]:
        return True
    return False

def string_to_tuple(string):
    return tuple(int(element) for element in string.strip('()').split(','))

def check_teacher_availability (value, solution):
    cost = 0
    for var in solution:
        if var[4] == value[3] and var[1] == value[0] and string_to_tuple(value[1]) == string_to_tuple(var[2]):
            cost += 1000
            # print(f'Teacher availability {value} is not available because of {var}')
    return cost


def check_room_availability (value, solution):
    cost = 0
    for var in solution:
        if var[3] == value[2] and var[1] == value[0] and string_to_tuple(value[1]) == string_to_tuple(var[2]):
            cost += 1000
            # print(f'Intervals {var[2][0]} {value[1][0]},  {var[2][1]}, {value[1][1]}')
            # print(f' Room availability {value} is not available because of {var}')
    return cost


def check_teacher_num_hours (value, solution):
    cost = 0
    count = 0
    for var in solution:
        if var[4] == value[3]:
            count += 1
    if count >= 7:
        cost = 1000
        # print(f'{value} is not available because of {count}')

    return cost

def check_soft_constraints(value):
    global soft_constraints

    teacher = value[3]
    day = value[0]
    interval = value[1]
    cost = 0

    if day not in soft_constraints[teacher]['preffered_days']:
        # print(f'**** Teacher {teacher} doesn\'t want to work on day {day}')
        cost += 1
    if interval not in soft_constraints[teacher]['preffered_intervals']:
        # print(f'**** Teacher {teacher} doesn\'t want to work on interval {interval}')
        cost += 1

    return cost

def solution_cost(value, solution):
    cost = check_teacher_availability(value, solution) + check_room_availability(value, solution) +\
            check_teacher_num_hours(value, solution) + check_soft_constraints(value)

    return cost
    

def csp(variables, acceptable_cost, solution, cost, apel_recursiv=0):
    # global best_cost
    global rooms
    global domain
    global subjects

    if len(variables) == 0:
        return solution

    my_vars = copy.deepcopy(variables)
    my_vars.sort(key=lambda x: subjects[x], reverse=True)
    # my_vars.sort(key=lambda x, y: len(domain[x]) - len(domain[y]), reverse=True)
    # my_vars.sort(key=cmp_to_key(compare))
    chosen_var = my_vars[0]

    # print(f'VARS {my_vars}')
    # print(f'CHOSEN VAR {chosen_var}')
    # print(f'**** Subjects before: {subjects}')
    # print(f'DOMENII {domain}')
    # # print(f'COST {cost} SOLUTION {solution}')
    # print(f'WE ARE IN DOMAINE OF {chosen_var}')
    for value in domain[chosen_var]:
        # print(f'APEL {apel_recursiv}')  
        new_cost = cost + solution_cost(value, solution)
        # print(f'Value {value} has cost {new_cost}')
        if new_cost <= acceptable_cost:
            new_sol = solution + [(chosen_var,) + value]
            # print(f'**** OK! {new_sol}')
            # print(f'**** Accommodated more {rooms[value[2]]["Capacitate"]} students')
            # domains[chosen_var].remove(value)
            subjects[chosen_var] = subjects[chosen_var] - rooms[value[2]]['Capacitate']
            # print(f'**** Subjects BEFORE CALL: {subjects}')

            # index_to_remove = domain[chosen_var].index(value)
            # domain[chosen_var].pop(index_to_remove)
            
            if subjects[chosen_var] <= 0:
                # print(f'Variable {chosen_var} is done!')
                # input()
                result = csp(my_vars[1:], acceptable_cost, new_sol, new_cost, apel_recursiv + 1)
            else:
                # print(f'Variable {chosen_var} is not done!')
                # input()
                result = csp(my_vars, acceptable_cost, new_sol, new_cost, apel_recursiv + 1)
            
            if result is not None:
                return result
            else:
                # print(f'REZULTAT DE LA APELUL {apel_recursiv + 1}')
                # print('********************** Am primit FAIL ***********************')
                subjects[chosen_var] = subjects[chosen_var] + rooms[value[2]]['Capacitate']
                new_sol.pop()
                # index_to_remove = domain[chosen_var].index(popped_val)
                # domain[chosen_var].append(value)
                # print(f'Am dat pop la {popped_val}')
                # print(f'Am updatat studenti la {chosen_var} cu {rooms[value[2]]["Capacitate"]}')
                # print(f'**** Subjects after FAIL: {subjects}')
                # domains[chosen_var].append(value)

    return None


def generate_preffered_intervals(intervals_constr):
    all_intervals = []
    for interval in intervals_constr:
        interval_down_lim, interval_up_lim = tuple(int(hour) for hour in interval.split('-'))
        if interval_up_lim - interval_down_lim == 2:
            all_intervals.append(str((interval_down_lim, interval_up_lim)))
            continue
        for hour in range(interval_down_lim, interval_up_lim, 2):
            all_intervals.append(str((hour, hour + 2)))   
       
    return all_intervals

def generate_preffered_constraints(teacher_constraint):
    preffered_days = list(filter(lambda constraint: constraint[0] != '!' and constraint[0].isdigit() == False, teacher_constraint))
    preffered_intervals = generate_preffered_intervals(list(filter(lambda constraint: constraint[0].isdigit(), teacher_constraint)))
    return preffered_days, preffered_intervals



if __name__ == '__main__':
    file_dict = {1: 'dummy', 2: 'orar_mic_exact', 3: 'orar_mediu_relaxat', 4: 'orar_mare_relaxat', 5: 'orar_constrans_incalcat'}
    algorithm = sys.argv[1]

    file_no = int(sys.argv[2])
    input_name = f'inputs/{file_dict[file_no]}.yaml'

    dict_yaml = utils.read_yaml_file(input_name)
    days = dict_yaml[utils.ZILE]
    intervals = dict_yaml[utils.INTERVALE]
    teachers = dict_yaml[utils.PROFESORI]

    global rooms
    global subjects
    rooms = copy.deepcopy(dict_yaml[utils.SALI])
    subjects = copy.deepcopy(dict_yaml[utils.MATERII])

    global soft_constraints
    soft_constraints = {}
    for teacher in teachers:
        soft_constraints[teacher] = {}
        soft_constraints[teacher]['preffered_days'], soft_constraints[teacher]['preffered_intervals'] = generate_preffered_constraints(teachers[teacher]['Constrangeri'])

    solution = None
    if algorithm == 'astar':
        global astar_options
        astar_options = []
        initial_state = []

        for subject in subjects:
            for day in days:
                for interval in intervals:
                    for room in rooms:
                        if check_subject_room_compatibility(subject, room, subjects, rooms):
                            for teacher in teachers:
                                if check_subject_teacher_compatibility(subject, teacher, teachers):
                                    astar_options.append((subject, day, interval, room, teacher))

        global total_studs
        total_studs = 0
        for subject, students in subjects.items():
            total_studs += students

        # print(f'SUBJECTS {subjects}')
        # print(f'ROOMS {rooms}')
        # print(heuristic([('DS', 'Luni', '(8, 10)', 'EG390', 'Andreea Dinu')]))

        solution = astar(initial_state)
        # print(solution)

    elif algorithm == 'csp':
        variables = []
        for subject, total_studs in subjects.items():
            variables.append(subject)


        global domain
        domain = {}
        for subject in variables:
            for day in days:
                for interval in intervals:
                    for room in rooms:
                        if subject in rooms[room][utils.MATERII]:
                            for teacher in teachers:
                                if subject in teachers[teacher][utils.MATERII]:
                                    if subject not in domain:
                                        domain[subject] = [(day, interval, room, teacher)]
                                    else:
                                        domain[subject].append((day, interval, room, teacher))

        for subject, values in domain.items():
            values.sort(key=lambda x: rooms[x[2]]['Capacitate'], reverse=True)

        # variables.sort(key = lambda x: len(domain[x]))
        # print(variables)

        print('Enter acceptable cost: ')
        acceptable_cost = int(input())

        solution = csp(variables, acceptable_cost, [], 0)
        # print(solution)

        # Making the solution printable
    printable_solution = {}
    for day in days:
        printable_solution[day] = {}
        for interval in intervals:
            my_interval = string_to_tuple(interval)
            printable_solution[day][my_interval] = {}
            for room in rooms:
                printable_solution[day][my_interval][room] = {}

    for var in solution:
        day, interval, room, teacher = var[1], var[2], var[3], var[4]
        my_interval = string_to_tuple(interval)
        printable_solution[day][my_interval][room] = (teacher, var[0])
    
    # print(f'Initial subjects: {dict_yaml[utils.MATERII]}')
    # print(f'Subject status: {subjects}')
    print(utils.pretty_print_timetable_aux_zile(printable_solution, input_name))
    print(f'Mandatory constraints violated: {check_constraints.check_mandatory_constraints(printable_solution, dict_yaml)}')
    print(f'Soft constraints violated: {check_constraints.check_optional_constraints(printable_solution, dict_yaml)}')
