import numpy as np
import cv2
import random
import navigation
import communicator
import sys
import os
import pickle
import time
import math
from gridworld import gridworld

alpha = 0.05
capture = cv2.VideoCapture(0)
navi = navigation.navigator()
#comms = communicator.client()
start_time = time.time()

# navi.pre_re_align()
# with open(os.path.dirname(__file__) + '/Qbase_dumb.data', 'rb') as f:
#     f.seek(0)
#     Q = pickle.load(f)
#     f.close()
# print(Q)
# quit()
def move_robot(origin, target, state):
    if origin == target:
        return state
    section = state

    # print(section, origin, target)
    diff = target - origin
    if diff == 3:
        section = str(int(section[0]) + 1) + section[1]
    elif diff == 1:
        section = section[0] + str(int(section[1]) + 1)
    elif diff == -1:
        section = section[0] + str(int(section[1]) - 1)
    else:
        section = str(int(section[0]) - 1) + section[1]

    # print(section, origin, target)
    navi.self_navigate(comms, section, True)
    return section


def get_action(values):
    results = []
    probs = []
    gamma = 5
    sum = 0

    for item in values:
        result = math.exp(gamma * item)
        results.append(result)
        sum += result

    for item in results:
        prob = item/sum
        probs.append(prob)

    #print(results, "\n", probs, "\n")
    x = random.uniform(0, 1)
    cumulative_prob = 0.0
    index = None
    for i in range(len(results)):
        cumulative_prob += probs[i]
        if x < cumulative_prob:
            index = i
            break

    return index

def get_action2(values):
    value = max(values)
    dups = []

    for i, item in enumerate(values):
        if item == value:
            dups.append(i)

    predex = random.randint(0, len(dups)-1)
    index = dups[predex]

    return index



# navigated = navi.self_navigate(comms, "00", False)
# if navigated is None:
#     comms.close_connection()
#     sys.exit(0)
# navi.pre_re_align()

ret, frame = capture.read()
frame = cv2.resize(frame, (0, 0), None, .5, .5)
frame = navi.warp_me(frame)
color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

env_sections = navi.section_dict(color)
wall_sections = navi.find_walls(env_sections)
robot_sections = navi.find_robot(env_sections)
env_keys = list(env_sections.keys())
wall_keys = list(wall_sections.keys())
robot_key = list(robot_sections.keys())[0]
goal = "42"

robot_env = []
i = 0
robot_state = 0
for key in env_keys:
    if key in wall_keys:
        robot_env.append(0)
    elif key == goal:
        robot_env.append(4)
    elif key == robot_key:
        robot_env.append(1)
        state = i
    else:
        robot_env.append(1)
    i += 1
print(robot_env)
env = gridworld(robot_env)

Q = np.random.uniform(0, 0, (15, 4))
Q[14] = [1, 1, 1, 1]
with open(os.path.dirname(__file__) + '/test.data', 'wb') as f:
    pickle.dump(Q, f)
Q = None
with open(os.path.dirname(__file__) + '/test.data', 'rb') as f:
    f.seek(0)
    Q = pickle.load(f)
    f.close()
print(Q)

learning = True
iteration = 1
tot_moves = 0
fails = 0
while(learning and Q is not None and iteration < 2001):
    print("Iteration: ", iteration)
    print("--- %s seconds ---" % (time.time() - start_time))
    seen = []
    state, reward = env.reset(robot_state)
    new_state = None
    position = "00"
    count = 0
    while (env.terminal() == False):
        #print("-------")
        action = get_action(Q[state])#np.argmax(Q[state,:])
        #print(Q[state], action)
        new_state, reward = env.step(action)
        if new_state != state:
            count += 1
        #position = move_robot(state, new_state, position)
        # print(state, action, new_state)

        if new_state in seen:
            reward = -0.5
        else:
            seen.append(new_state)

        target_score = reward + np.max(Q[new_state])
        Q[state, action] = Q[state, action] + (alpha * (target_score - Q[state, action]))
        if reward == -0.9:
            fails += 1
            print("Fail")
            break

        state = new_state

    # print(Q)
    print("Moves: ", count)
    tot_moves += count
    count = 0
    if iteration % 10 == 0:
        print("Successses: ", 10 - fails)
        fails = 0
    with open(os.path.dirname(__file__) + '/test.data', 'wb') as f:
        pickle.dump(Q, f)
    #navi.self_navigate(comms, "00", False)
    #navi.pre_re_align()
    iteration += 1

print("Total moves: ", tot_moves)
print(Q)
comms.close_connection()