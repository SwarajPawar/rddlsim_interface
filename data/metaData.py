

def get_decNode(dataset_name):

    if dataset_name == 'Elevators':
        return [f'Action_{i}' for i in range(6)]
    elif dataset_name == 'Navigation':
        return [f'Action_{i}' for i in range(5)]
    elif dataset_name == 'GameOfLife':
        return [f'Action_{i}' for i in range(3)]
    elif dataset_name == 'SysAdmin':
        return [f'Action_{i}' for i in range(4)]
    else:
        print(dataset_name)


def get_utilityNode(dataset_name):

    if dataset_name == 'Elevators':
        return ['Reward']
    if dataset_name == 'Navigation':
        return ['Reward']
    if dataset_name == 'GameOfLife':
        return ['Reward']
    if dataset_name == 'SysAdmin':
        return ['Reward']

def get_scope_vars(dataset_name):

    #returns a list of all variables in sequence of partial order excluding decison variables
    #e.g.
    # if dataset_name == 'Computer_Diagnostician':
    #     return ['System_State','Logic_board_fail', 'IO_board_fail', 'Rework_Outcome', 'Rework_Cost' ]

    partial_order = get_partial_order(dataset_name)
    decision_nodes = get_decNode(dataset_name)
    var_set = [var for var_set in partial_order for var in var_set]
    for d in decision_nodes:
        var_set.remove(d)
    return var_set

def get_feature_names(dataset_name):

    partial_order = get_partial_order(dataset_name)
    var_set = [var for var_set in partial_order for var in var_set]
    return var_set


def get_partial_order(dataset_name):

    if dataset_name == 'Elevators':
        partialOrder = list()
        for i in range(6):
            partialOrder += [[f'Elevator_at_Floor_{i}', f'Person_Waiting_{i}', f'Person_in_Elevator_Going_Up_{i}', 
            					f'Elevator_Direction_{i}', f'Elevator_Closed_{i}'], [f'Action_{i}']]
        partialOrder += [[f'Elevator_at_Floor_6', f'Person_Waiting_6', f'Person_in_Elevator_Going_Up_6', 
            					f'Elevator_Direction_6', f'Elevator_Closed_6', 'Reward']]
        return partialOrder

    if dataset_name == 'Navigation':
        partialOrder = list()
        for i in range(5):
            partialOrder += [[f'Robot_at_1_t{i}', f'Robot_at_2_t{i}', f'Robot_at_3_t{i}', 
                                f'Robot_at_4_t{i}', f'Robot_at_5_t{i}', f'Robot_at_6_t{i}'], [f'Action_{i}']]
        partialOrder += [[f'Robot_at_1_t5', f'Robot_at_2_t5', f'Robot_at_3_t5', 
                                f'Robot_at_4_t5', f'Robot_at_5_t5', f'Robot_at_6_t5', 'Reward']]
        return partialOrder

    if dataset_name == 'GameOfLife':
        partialOrder = list()
        for i in range(3):
            partialOrder += [[f'Cell_1_t{i}', f'Cell_2_t{i}', f'Cell_3_t{i}', 
                                f'Cell_4_t{i}', f'Cell_5_t{i}', f'Cell_6_t{i}',
                                f'Cell_7_t{i}', f'Cell_8_t{i}', f'Cell_9_t{i}'], [f'Action_{i}']]
        partialOrder += [[f'Cell_1_t3', f'Cell_2_t3', f'Cell_3_t3', 
                                f'Cell_4_t3', f'Cell_5_t3', f'Cell_6_t3',
                                f'Cell_7_t3', f'Cell_8_t3', f'Cell_9_t3', 'Reward']]
        return partialOrder
    if dataset_name == 'SysAdmin':
        partialOrder = list()
        for i in range(4):
            partialOrder += [[f'Running_1_t{i}', f'Running_2_t{i}', f'Running_3_t{i}', 
                                f'Running_4_t{i}', f'Running_5_t{i}'], [f'Action_{i}']]
        partialOrder += [[f'Running_1_t4', f'Running_2_t4', f'Running_3_t4', 
                                f'Running_4_t4', f'Running_5_t4', 'Reward']]
        return partialOrder
    else:
        print(dataset_name)


def get_feature_labels(dataset_name):

    
    if dataset_name == 'Elevators': 
        features = list()
        for i in range(6):
            features += [f'EF{i}', f'PW{i}', f'PU{i}', f'ED{i}', f'EC{i}',  f'A{i}']
        features += [f'EF6', f'PW6', f'PU6', f'ED6', f'EC', 'RW']
        return features

    if dataset_name == 'Navigation': 
        features = list()
        for i in range(5):
            features += [f'R1{i}', f'R2{i}', f'R3{i}', f'R4{i}',  f'R5{i}', f'R6{i}', f'A{i}']
        features += [f'R15', f'R25', f'R35', f'R45', f'R55', f'R65', 'RW']
        return features

    if dataset_name == 'GameOfLife': 
        features = list()
        for i in range(3):
            features += [f'C1{i}', f'C2{i}', f'C3{i}', f'C4{i}',  f'C5{i}', f'C6{i}', f'C7{i}',  f'C8{i}', f'C9{i}', f'A{i}']
        features += [f'C13', f'C23', f'C33', f'C43', f'C53', f'C63', f'C73', f'C83', f'C93', 'RW']
        return features

    if dataset_name == 'SysAdmin': 
        features = list()
        for i in range(4):
            features += [f'R1{i}', f'R2{i}', f'R3{i}', f'R4{i}',  f'R5{i}' f'A{i}']
        features += [f'R14', f'R24', f'R34', f'R44', f'R54', 'RW']
        return features





