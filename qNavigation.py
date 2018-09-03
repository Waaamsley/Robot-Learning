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

alpha = 0.05
capture = cv2.VideoCapture(0)
client = communicator.client()

navigated = navigation.self_navigate(client, "00")
if navigated is None:
    sys.exit(0)
navigation.pre_re_align()

ret, frame = capture.read()
frame = cv2.resize(frame, (0, 0), None, .5, .5)
frame = navigation.warp_me(frame)
color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

env_sections = navigation.section_dict(color)
wall_sections = navigation.find_walls(env_sections)
robot_sections = navigation.find_robot(env_sections)

env_keys = list(env_sections.keys())
wall_keys = list(wall_sections.keys())
robot_key = list(robot_sections.keys())[0]
goal_key = "42"

robot_env = []
i = 0
robot_state = 0
for key in env_keys:
    if key in wall_keys:
        robot_env.append(0)
    elif key == goal_key:
        robot_env.append(4)
    elif key == robot_key:
        state = i
    else:
        robot_env.append(1)
    i += 1

env = gridworld(robot_env)
Q = np.zeros((15, 4))

learning = True
while(learning):
    state, reward = env.reset(robot_state)
    while (env.terminal() == False):
        action = np.argmax(Q[state,:])
        nstate, nreward = env.step(action)
        #Q[state, action] = Q[state, action] + alpha*(reward +
        # do math
        #move robot

    with open(os.path.dirname(__file__) + '\\Qtable.data', 'w') as f:
        pickle.dump(Q, f)
    navigation.self_navigate(client, "00")
    navigation.pre_re_align()


print(Q)





#env = gridworld()




