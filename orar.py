import sys
import utils
import check_constraints
import copy
import math
from functools import cmp_to_key
from heapq import heappush, heappop


class Timetable:
    def __init__(self, timetable):
        self.timetable = timetable


def check_teacher_simultaneously(teacher, curr_state, day, interval):
    for classroom, subject_assigned in curr_state[day][interval].items():
        if subject_assigned != None and subject_assigned[0] == teacher:
            return True
    return False

def check_teacher_number_hours(teacher, curr_state):
    count = 0
    for day, time_intervals in curr_state.items():
        for interval, classrooms in time_intervals.items():
            for classroom, assigned_subject in classrooms.items():
                if assigned_subject != None and assigned_subject[0] == teacher:
                    count += 1
    return count

def generate_neighbours(curr_state, total_studs_assigned):
    global rooms
    global subjects
    global teachers
    global days
    global intervals
    neighbours = []

    total_studs_need_assignment = {subject: subjects[subject] - total_studs_assigned[subject] for subject in subjects.keys()}
    
    for day in days:
        for interval in intervals:
            for room in rooms:
                if curr_state[day][interval][room] != None:
                    continue
                for subject in subjects:
                    if subject not in rooms[room][utils.MATERII] or total_studs_need_assignment[subject] <= 0:
                        continue
                    for teacher in teachers:
                        if subject not in teachers[teacher][utils.MATERII] or\
                              check_teacher_simultaneously(teacher, curr_state, day, interval) or\
                                  check_teacher_number_hours(teacher, curr_state) >= 7:
                            continue
                        neighbours.append(copy.deepcopy(curr_state))
                        neighbours[-1][day][interval][room] = (teacher, subject)
                                                                           
    return neighbours


def transition_cost(neighbour, curr_state):
    global soft_constraints
    global rooms
    global subjects
    global teachers

    cost_neighbour = 10
    for day, time_interval in neighbour.items():
        for interval, classrooms in time_interval.items():
            for classroom, assigned_subject in classrooms.items():
                if assigned_subject != None:
                    if interval not in soft_constraints[assigned_subject[0]]['preffered_intervals']:
                        cost_neighbour += 10
                    if day not in soft_constraints[assigned_subject[0]]['preffered_days']:
                        cost_neighbour += 10

    return cost_neighbour
               

def heuristic(timetable, total_studs_assigned):
    global rooms
    global subjects   
    global sorted_subjects_by_rooms
    global sorted_rooms_by_capacity

    max_classroom_capacity = {subject: max(room_details['Capacitate'] for room_details in rooms.values() if subject in room_details[utils.MATERII]) 
                              for subject in subjects.keys()}
    # slots_needed = {subject: math.floor((subjects[subject] - total_studs_assigned[subject]) / max_classroom_capacity[subject])
    #                 if subjects[subject] - total_studs_assigned[subject] > 0 else 0 
    #                 for subject in subjects.keys()}
    
    slots_needed = {subject: (subjects[subject] - total_studs_assigned[subject])
                    if subjects[subject] - total_studs_assigned[subject] > 0 else 0 
                    for subject in subjects.keys()}

    # print(slots_needed)

    cost = sum(slots_needed.values()) * 100

    for day, intervals in timetable.items():
        for interval, classrooms in intervals.items():
            for classroom, assigned_subject in classrooms.items():
                if assigned_subject != None:
                    cost += sorted_subjects_by_rooms[assigned_subject[1]]
                    cost += sorted_teacher_constraints[assigned_subject[0]]

    return cost


def is_final(total_studs_assigned):
    global rooms
    global total_studs

    diff_studs = {subject: subjects[subject] - total_studs_assigned[subject] for subject in subjects.keys()}
    print(diff_studs)
    for subject, total_studs in diff_studs.items():
        if total_studs > 0:
            return False
    return True


def get_total_studs_assigned(orar):
    total_studs_assigned = {subject: 0 for subject in subjects.keys()}
    for day, intervals in orar.timetable.items():
        for interval, classrooms in intervals.items():
            for classroom, assigned_subject in classrooms.items():
                if assigned_subject != None:
                    total_studs_assigned[assigned_subject[1]] += rooms[classroom]['Capacitate']
    return total_studs_assigned

def astar(initial_state):
    opened = []
    index = 0
    heappush(opened, (0 + heuristic(initial_state.timetable, {subject: 0 for subject in subjects}), index, initial_state))
    print(opened)
    discovered = {initial_state: 0}
    print(discovered)
    # discovered.append((initial_state, 0))

    # print('aici')
    while opened:
        # print(f'LEN HEAP {len(opened)}')
        curr_f_cost, index_state, curr_state = heappop(opened)
        # print(curr_f_cost)
        total_studs_assigned = get_total_studs_assigned(curr_state)

        printable_solution = {}
        for day in days:
            printable_solution[day] = {}
            for interval in intervals:
                tuple_int = string_to_tuple(interval)
                printable_solution[day][tuple_int] = {}
                for room in rooms:
                    printable_solution[day][tuple_int][room] = {}

        for day, time_intervals in curr_state.timetable.items():
            for interval, classrooms in time_intervals.items():
                for classroom, assigned_subject in classrooms.items():
                    if assigned_subject != None:
                        printable_solution[day][string_to_tuple(interval)][classroom] = curr_state.timetable[day][interval][classroom]


        # print(utils.pretty_print_timetable_aux_zile(printable_solution, "inputs/orar_mediu_relaxat.yaml"))
        # input()

        if is_final(total_studs_assigned):
            return curr_state
        g_curr_state = discovered[curr_state] 

        total_studs_need_assignment = {subject: subjects[subject] - total_studs_assigned[subject] for subject in subjects.keys()}
        print(f'Total studs need assignment: {total_studs_need_assignment}')
    
        for day in days:
            for interval in intervals:
                for room in rooms:
                    if curr_state.timetable[day][interval][room] != None:
                        continue
                    for subject in subjects:
                        if subject not in rooms[room][utils.MATERII] or total_studs_need_assignment[subject] <= 0:
                            continue
                        for teacher in teachers:
                            if subject not in teachers[teacher][utils.MATERII] or\
                                check_teacher_simultaneously(teacher, curr_state.timetable, day, interval) or\
                                    check_teacher_number_hours(teacher, curr_state.timetable) >= 7:
                                continue
                            n = copy.deepcopy(curr_state.timetable)
                            n[day][interval][room] = (teacher, subject)
                            neighbour = Timetable(n)
                # for neighbour in neighbours: 
                            if neighbour in discovered:
                                g_neighbour = discovered[neighbour]

                            tentative_g_cost = g_curr_state + transition_cost(neighbour.timetable, curr_state.timetable)
                            if neighbour in discovered and tentative_g_cost < g_neighbour:
                                index += 1
                                discovered[neighbour] = tentative_g_cost
                                heappush(opened, (tentative_g_cost + heuristic(neighbour.timetable, total_studs_assigned), index, neighbour))
                            elif neighbour not in discovered:
                                index += 1
                                discovered[neighbour] = tentative_g_cost
                                heappush(opened, (tentative_g_cost + heuristic(neighbour.timetable, total_studs_assigned), index, neighbour))
    
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
    return cost


def check_room_availability (value, solution):
    cost = 0
    for var in solution:
        if var[3] == value[2] and var[1] == value[0] and string_to_tuple(value[1]) == string_to_tuple(var[2]):
            cost += 1000
    return cost


def check_teacher_num_hours (value, solution):
    cost = 0
    count = 0
    for var in solution:
        if var[4] == value[3]:
            count += 1
    if count >= 7:
        cost = 1000

    return cost

def check_soft_constraints(value):
    global soft_constraints

    teacher = value[3]
    day = value[0]
    interval = value[1]
    cost = 0

    if day not in soft_constraints[teacher]['preffered_days']:
        cost += 1
    if interval not in soft_constraints[teacher]['preffered_intervals']:
        cost += 1

    return cost

def solution_cost(value, solution):
    cost = check_teacher_availability(value, solution) + check_room_availability(value, solution) +\
            check_teacher_num_hours(value, solution) + check_soft_constraints(value)

    return cost
    

def csp(variables, acceptable_cost, solution, cost, apel_recursiv=0):
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

    for value in domain[chosen_var]:
        new_cost = cost + solution_cost(value, solution)
        if new_cost <= acceptable_cost:
            new_sol = solution + [(chosen_var,) + value]
            subjects[chosen_var] = subjects[chosen_var] - rooms[value[2]]['Capacitate']
            
            if subjects[chosen_var] <= 0:
                result = csp(my_vars[1:], acceptable_cost, new_sol, new_cost, apel_recursiv + 1)
            else:
                result = csp(my_vars, acceptable_cost, new_sol, new_cost, apel_recursiv + 1)
            
            if result is not None:
                return result
            else:
                subjects[chosen_var] = subjects[chosen_var] + rooms[value[2]]['Capacitate']
                new_sol.pop()

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

    global dict_yaml
    dict_yaml = utils.read_yaml_file(input_name)


    global teachers
    global rooms
    global subjects
    global days
    global intervals
    intervals = dict_yaml[utils.INTERVALE]
    days = dict_yaml[utils.ZILE]
    teachers = dict_yaml[utils.PROFESORI]
    rooms = copy.deepcopy(dict_yaml[utils.SALI])
    subjects = copy.deepcopy(dict_yaml[utils.MATERII])

    global sorted_subjects_by_rooms
    sorted_subjects_by_rooms = dict(sorted({subject: len([room for room in rooms if subject in rooms[room][utils.MATERII]]) 
                                           for subject in subjects.keys()}.items(), key = lambda it: it[1]))
    
    # print(sorted_subjects_by_room_cap)

    global soft_constraints
    soft_constraints = {}
    for teacher in teachers:
        soft_constraints[teacher] = {}
        soft_constraints[teacher]['preffered_days'], soft_constraints[teacher]['preffered_intervals'] = generate_preffered_constraints(teachers[teacher]['Constrangeri'])

    if algorithm == 'astar':
        # global astar_options
        # astar_options = []
        # initial_state = []
        initial_state = Timetable({day: {interval: {room: None for room in rooms} for interval in intervals} for day in days})

        global sorted_teacher_constraints
        sorted_teacher_constraints = {teacher: len(soft_constraints[teacher]['preffered_days']) + len(soft_constraints[teacher]['preffered_intervals']) for teacher in teachers}
        print(sorted_teacher_constraints)
        
        global sorted_rooms_by_capacity
        sorted_rooms_by_capacity = dict(sorted({room: rooms[room]['Capacitate'] for room in rooms.keys()}.items(), key = lambda it: it[1], reverse=True))

        solution = astar(initial_state)

        printable_solution = {}
        for day in days:
            printable_solution[day] = {}
            for interval in intervals:
                tuple_int = string_to_tuple(interval)
                printable_solution[day][tuple_int] = {}
                for room in rooms:
                    printable_solution[day][tuple_int][room] = {}

        for day, time_intervals in solution.timetable.items():
            for interval, classrooms in time_intervals.items():
                for classroom, assigned_subject in classrooms.items():
                    if assigned_subject != None:
                        printable_solution[day][string_to_tuple(interval)][classroom] = solution.timetable[day][interval][classroom]

        print(utils.pretty_print_timetable_aux_zile(printable_solution, input_name))
        print(f'Mandatory constraints violated: {check_constraints.check_mandatory_constraints(printable_solution, dict_yaml)}')
        print(f'Soft constraints violated: {check_constraints.check_optional_constraints(printable_solution, dict_yaml)}')
        # print(heuristic([('DS', 'Luni', '(8, 10)', 'EG390', 'Andreea Dinu')]))
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

        # print(printable_solution)
        
        # print(f'Initial subjects: {dict_yaml[utils.MATERII]}')
        # print(f'Subject status: {subjects}')
        print(utils.pretty_print_timetable_aux_zile(printable_solution, input_name))
        print(f'Mandatory constraints violated: {check_constraints.check_mandatory_constraints(printable_solution, dict_yaml)}')
        print(f'Soft constraints violated: {check_constraints.check_optional_constraints(printable_solution, dict_yaml)}')
