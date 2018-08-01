class state:
    key = None
    cost = 0
    heuristic = None
    total_cost = None
    history = None

    def __init__(self, key, cost, heuristic, parent_history, parent_key):
        self.key = key
        self.cost = cost
        self.heuristic = heuristic
        self.total_cost = cost + heuristic
        if (parent_key != ''):
            self.history = parent_history
            self.history.append(parent_key)
        else:
            self.history = []

def get_moves(state, wall_sections):
    move_keys = []
    s_key = state.key

    if (int(s_key[0]) - 1 >= 0):
        temp_key = str(int(s_key[0]) - 1) + s_key[1]
        if (temp_key not in wall_sections):
            move_keys.append(temp_key)

    if (int(s_key[0]) + 1 <= 5):
        temp_key = str(int(s_key[0]) + 1) + s_key[1]
        if (temp_key not in wall_sections):
            move_keys.append(temp_key)

    if (int(s_key[1]) - 1 >= 0):
        temp_key = s_key[0] + str(int(s_key[1]) - 1)
        if (temp_key not in wall_sections):
            move_keys.append(temp_key)

    if (int(s_key[1]) + 1 <= 2):
        temp_key = s_key[0] + str(int(s_key[1]) + 1)
        if (temp_key not in wall_sections):
            move_keys.append(temp_key)

    return move_keys

def get_heuristic(robot_key, goal_key):
    heuristic = 0

    x_heur = abs(int(robot_key[0]) - int(goal_key[0]))
    y_heur = abs(int(robot_key[1]) - int(goal_key[1]))

    heuristic = x_heur + y_heur

    return heuristic

def find_path(sections, wall_sections, goal_key, robot_key):
    parent = state(robot_key, 0, get_heuristic(robot_key, goal_key), None, '')
    open_list = []
    closed_list = []
    open_list.append(parent)
    closed_list.append(parent.key)

    searching = True
    while (searching):
        p_moves = get_moves(parent, wall_sections)
        for move in p_moves:
            if move not in closed_list:
                child = state(move, parent.cost + 1, get_heuristic(move, goal_key), parent.history.copy(), parent.key)
                open_list.append(child)
                closed_list.append(child.key)

        open_list.remove(parent)

        temp_state = None
        cost = 999
        for element in open_list:
            if (element.total_cost < cost):
                temp_state = element
                cost = element.total_cost

        parent = temp_state
        if parent is None:
            return None
        elif (parent.key == goal_key):
            searching = False
    parent.history.append(parent.key)
    return parent.history