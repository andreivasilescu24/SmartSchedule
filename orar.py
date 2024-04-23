import sys
import utils
import check_constraints
import copy

def astar(input_name):
    pass


def check_subject_teacher_compatibility (subject, teacher, subjects, teachers):
    return subject in teachers[teacher][utils.MATERII]


def check_subject_room_compatibility (subject, room, subjects, rooms):
    if subject in rooms[room][utils.MATERII]:
        subjects[subject] -= rooms[room]['Capacitate']
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
    

# def csp(variables, domain, soft_constraints, rooms, acceptable_cost, solution, cost):
#     global best_sol
#     global best_cost
#     global subjects
    
#     variables.sort(key=lambda x: subjects[x], reverse=True)
#     print(domain)

#     print(subjects)
#     print(variables)
#     print(solution)
#     if len(variables) == 0:
#         print('AICI')
#         if cost < best_cost:
#             best_cost = cost
#             best_sol = copy.deepcopy(solution)
#         if cost <= acceptable_cost:
#             return True
        
#     elif len(domain[variables[0]]) == 0:
#         print('AICI2')
#         return False
#     elif cost == best_cost:
#         print('AICI3')
#         return False
#     else:
#         print('HERE')
#         chosen_var = variables[0]
#         chosen_value = domain[chosen_var].pop(0)

#         new_solution = copy.deepcopy(solution)

#         new_cost = solution_cost(chosen_value, soft_constraints, new_solution)
#         new_solution.append((chosen_var,) + chosen_value)
#         subjects[chosen_var] -= rooms[chosen_value[2]]['Capacitate']
#         # print('COST', new_cost)
#         # print('NEW SOL', new_solution)
#         # input()
#         # if new_cost >= 1000:
#         #     subjects[chosen_var] += rooms[chosen_value[2]]['Capacitate']

#         if new_cost < best_cost and new_cost <= acceptable_cost:
#             # print('before')
#             if subjects[chosen_var] <= 0:
#                 if csp(variables[1:], copy.deepcopy(domain), soft_constraints, rooms, acceptable_cost,
#                         new_solution, new_cost):
#                     return True
#             else:
#                 if csp(variables, copy.deepcopy(domain), soft_constraints, rooms, acceptable_cost,
#                         new_solution, new_cost):
#                     return True
#         else:
#             subjects[chosen_var] += rooms[chosen_value[2]]['Capacitate']
#         return csp(variables, copy.deepcopy(domain), soft_constraints, rooms, acceptable_cost, solution, cost)

    
def csp(variables, subjects, acceptable_cost, solution, cost, apel_recursiv=0):
    # global best_cost
    global rooms
    global domain

    if len(variables) == 0:
        return solution

    my_vars = copy.deepcopy(variables)
    my_vars.sort(key=lambda x: subjects[x], reverse=True)
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
                result = csp(my_vars[1:], subjects, acceptable_cost, new_sol, new_cost, apel_recursiv + 1)
            else:
                # print(f'Variable {chosen_var} is not done!')
                # input()
                result = csp(my_vars, subjects, acceptable_cost, new_sol, new_cost, apel_recursiv + 1)
            
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

    if algorithm == 'astar':
        pass
    elif algorithm == 'csp':
        dict_yaml = utils.read_yaml_file(input_name)
        days = dict_yaml[utils.ZILE]
        intervals = dict_yaml[utils.INTERVALE]
        teachers = dict_yaml[utils.PROFESORI]

        global rooms
        global best_sol
        global best_cost

        rooms = copy.deepcopy(dict_yaml[utils.SALI])
        subjects = copy.deepcopy(dict_yaml[utils.MATERII])
        best_sol = []
        best_cost = 100

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

        soft_constraints = {}
        for teacher in teachers:
            soft_constraints[teacher] = {}
            soft_constraints[teacher]['preffered_days'], soft_constraints[teacher]['preffered_intervals'] = generate_preffered_constraints(teachers[teacher]['Constrangeri'])

        print('Enter acceptable cost: ')
        acceptable_cost = int(input())

        solution = csp(variables, subjects, acceptable_cost, [], 0)

        # Making the solution printable
        printable_solution = {}
        for day in days:
            printable_solution[day] = {}
            for interval in intervals:
                my_interval = tuple(int(element) for element in interval.strip('()').split(','))
                printable_solution[day][my_interval] = {}
                for room in rooms:
                    printable_solution[day][my_interval][room] = {}

        for var in solution:
            day, interval, room, teacher = var[1], var[2], var[3], var[4]
            my_interval = tuple(int(element) for element in interval.strip('()').split(','))
            printable_solution[day][my_interval][room] = (teacher, var[0])
        
        print(f'Initial subjects: {dict_yaml[utils.MATERII]}')
        print(f'Subject status: {subjects}')
        print(utils.pretty_print_timetable_aux_zile(printable_solution, input_name))
        print(check_constraints.check_mandatory_constraints(printable_solution, dict_yaml))
        print(check_constraints.check_optional_constraints(printable_solution, dict_yaml))
