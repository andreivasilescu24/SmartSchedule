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


def check_teacher_availability (value, solution):
    for var in solution:
        if var[4] == value[3] and var[1] == value[0] and var[2][0] == value[1][0] and var[2][1] == value[1][1]:
            return False
    return True


def check_room_availability (value, solution):
    for var in solution:
        if var[3] == value[2] and var[1] == value[0] and var[2][0] == value[1][0] and var[2][1] == value[1][1]:
            return False
    return True


def check_teacher_num_hours (value, solution):
    count = 0
    for var in solution:
        if var[4] == value[3]:
            count += 1
    if count >= 7:
        return False
    return True


def is_consistent(value, solution):
    if check_teacher_availability(value, solution) and\
        check_room_availability(value, solution) and\
        check_teacher_num_hours(value, solution):
            return True
    return False
    


def csp(variables, domain, rooms, subjects, solution):
    if len(variables) == 0:
        return solution
    
    chosen_var = variables[0]
    # print(f'CHOSEN VAR: {chosen_var}')

    for value in domain[chosen_var]:
        if is_consistent(value, solution):
            solution.append((chosen_var,) + value)

            if subjects[chosen_var] - rooms[value[2]]['Capacitate'] <= 0:
                subjects[chosen_var] -= rooms[value[2]]['Capacitate']
                result = csp(variables[1:], domain, rooms, subjects, solution)
            else:
                subjects[chosen_var] -= rooms[value[2]]['Capacitate']
                result = csp(variables, domain, rooms, subjects, solution)

            if result is not None:
                return result
            solution.pop()

    return None

def generate_preffered_intervals(intervals_constr):
    
    all_intervals = []
    for interval in intervals_constr:
        interval_down_lim, interval_up_lim = tuple(int(hour) for hour in interval.split('-'))
        if interval_up_lim - interval_down_lim == 2:
            all_intervals.append((interval_down_lim, interval_up_lim))
            continue
        for hour in range(interval_down_lim, interval_up_lim, 2):
            all_intervals.append((hour, hour + 2))   
       
    return all_intervals

def generate_preffered_constraints(teacher_constraint):
    preffered_days = list(filter(lambda constraint: constraint[0] != '!' and constraint[0].isdigit() == False, teacher_constraint))
    preffered_intervals = generate_preffered_intervals(list(filter(lambda constraint: constraint[0].isdigit(), teacher_constraint)))
    return preffered_days, preffered_intervals

if __name__ == '__main__':
    algorithm = sys.argv[1]
    input_name = f'inputs/{sys.argv[2]}.yaml'

    if algorithm == 'astar':
        pass
    elif algorithm == 'csp':
        dict_yaml = utils.read_yaml_file(input_name)
        days = dict_yaml[utils.ZILE]
        intervals = dict_yaml[utils.INTERVALE]
        subjects = dict_yaml[utils.MATERII]
        rooms = dict_yaml[utils.SALI]
        teachers = dict_yaml[utils.PROFESORI]

        variables = []
        place_time_room_domain = []

        print(teachers)

        for subject, total_studs in subjects.items():
            variables.append(subject)
        variables.sort(key=lambda x: subjects[x], reverse=True)

        domains = {}
        for subject in variables:
            for day in days:
                for interval in intervals:
                    for room in rooms:
                        if subject in rooms[room][utils.MATERII]:
                            for teacher in teachers:
                                if subject in teachers[teacher][utils.MATERII]:
                                    if subject not in domains:
                                        domains[subject] = [(day, interval, room, teacher)]
                                    else:
                                        domains[subject].append((day, interval, room, teacher))

        # for domain in domains:
        #     print(f'*************** {domain}')
        #     for domain_value in domains[domain]:
        #         print(domain_value)

        soft_constraints = {}
        for teacher in teachers:
            soft_constraints[teacher] = {}
            soft_constraints[teacher]['preffered_days'], soft_constraints[teacher]['preffered_intervals'] = generate_preffered_constraints(teachers[teacher]['Constrangeri'])

        solution = csp(variables, domains, rooms, subjects, [])
        

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
        
        # print(subjects)
        print(utils.pretty_print_timetable_aux_zile(printable_solution, input_name))
        print(check_constraints.check_optional_constraints(printable_solution, dict_yaml))
