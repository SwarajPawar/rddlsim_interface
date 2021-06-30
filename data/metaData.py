

def get_decNode(dataset_name):

    if dataset_name == 'Elevators':
        return [f'Action_{i}' for i in range(6)]
    else:
        print(dataset_name)


def get_utilityNode(dataset_name):

    if dataset_name == 'Elevators':
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
    else:
        print(dataset_name)


def get_feature_labels(dataset_name):

    
    if dataset_name == 'Elevators': 
        features = list()
        for i in range(8):
            features += [f'EF{i}', f'PW{i}', f'PU{i}', f'ED{i}', f'EC{i}',  f'A{i}']
        features += [f'EF6', f'PW6', f'PU6', f'ED6', f'EC6', 'RW']
        return features





