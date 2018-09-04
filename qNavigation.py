import numpy as np
import cv2
import navigation
import communicator
import sys
import os
import pickle
import random
import math
import threading
from gridworld import gridworld

alpha = 0.01
capture = cv2.VideoCapture(0)
navi = navigation.navigator()
comms = communicator.client()


def move_robot(origin, target, state):
    if origin == target:
        return state
    section = state

    print(section, origin, target)
    diff = target - origin
    if diff == 3:
        section = str(int(section[0]) + 1) + section[1]
    elif diff == 1:
        section = section[0] + str(int(section[1]) + 1)
    elif diff == -1:
        section = section[0] + str(int(section[1]) - 1)
    else:
        section = str(int(section[0]) - 1) + section[1]

    print(section, origin, target)
    navi.self_navigate(comms, section, True)
    return section


navigated = navi.self_navigate(comms, "00", True)

if navigated is None:
    comms.close_connection()
    sys.exit(0)
navi.pre_re_align()

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

env = gridworld(robot_env)
Q = None#np.zeros((15, 4))
with open(os.path.dirname(__file__) + '/Qtable.data', 'rb') as f:
    f.seek(0)
    Q = pickle.load(f)
    f.close()

learning = True
while(learning and Q is not None):
    state, reward = env.reset(robot_state)
    position = "00"
    while (env.terminal() == False):
        action = np.argmax(Q[state,:])
        new_state, new_reward = env.step(action)

        target_score = reward + np.max(Q[new_state, :])
        Q[state, action] = Q[state, action] + (alpha*(target_score - Q[state, action]))
        position = move_robot(state, new_state, position)
        state, reward = new_state, new_reward

    navi.self_navigate(comms, "00", True)
    navi.pre_re_align()
    # env.show(Q=Q, gamma=2)
    with open(os.path.dirname(__file__) + '/Qtable.data', 'wb') as f:
        pickle.dump(Q, f)
    # learning = False

comms.close_connection()