import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Arc, RegularPolygon
import time
from numpy import radians as rad
import warnings
#Author: Lech Szymanski
class gridworld:

    def __init__(self, R=-0.04, slippery=True):

        self.plot_handles = []
        self.grid = np.array([1,1,1,1,
                              1,0,1,2,
                              1,1,1,4])

        # self.grid = None # needs to be set by a method.
        self.W = 4
        self.H = 3

        self.num_states = len(self.grid)

        self.R = np.ones(self.num_states)*R
        for i in range(len(self.grid)):
            if self.grid[i] > 1:
                self.R[i] = self.grid[i]-3
            elif self.grid[i] < 1:
                self.R[i] = 0

        self.num_actions = 4

        self.actions_dirs = [[0,1],
                             [1,0],
                             [0,-1],
                             [-1,0]]

        if slippery:
            self.p = [0.8, 0.1, 0.1]
        else:
            self.p = [0.1, 0.0, 0.0]

    def reset(self):
        self.state = 0
        return self.state, self.R[self.state]

    def terminal(self):
        if self.grid[self.state] != 1:
            return True
        else:
            return False

    # def set_grid(self, robot_environment):
    #     self.grid = self.robot_environment

    def next_state(self,s,a):
        if self.grid[s] != 1:
            return s

        if a==0:
            #Going north
            next_state = s + self.W
        elif a==1:
            #Going east
            next_state = s + 1
        elif a==2:
            #Going south
            next_state = s - self.W
        elif a==3:
            #Goine west
            next_state = s - 1

        if next_state >= self.num_states or next_state < 0:
            next_state = s
        elif a == 1 and next_state % self.W == 0:
            next_state = s
        elif a == 3 and next_state % self.W == self.W - 1:
            next_state = s
        elif self.grid[next_state] == 0:
            next_state = s

        return next_state


    def step(self, a):
        if a<0 or a>3:
            raise Exception('Given action a=%d is out of bounds!  Valid actions are {0,...,%d}.' % (a, self.num_actions-1))

        r = np.random.rand()
        if a==0 or a==2:
            if r < self.p[1]:
                a = 1
            elif r < self.p[1]+self.p[2]:
                a = 3
        elif a==1 or a==3:
            if r < self.p[1]:
                a = 0
            elif r < self.p[1]+self.p[2]:
                a = 2

        next_state = self.next_state(self.state, a)

        self.state = next_state
        R = self.R[self.state]

        return self.state, R

    def show(self,U=None,Q=None, gamma=10):

        if not self.plot_handles:
            fh = plt.figure(figsize=(8, 6), dpi=100)
            self.h = fh.add_subplot(1,1,1)

            for x in range(self.W+1):
                self.h.plot([x, x],[0, self.H],'k')

            for y in range(self.H+1):
                self.h.plot([0, self.W],[y, y],'k')

            s = 0
            for y in range(self.H):
                for x in range(self.W):
                    if self.grid[s]==0:
                        self.h.add_patch(
                            patches.Rectangle(
                            (x, y),  # (x,y)
                            1,  # width
                            1,  # height
                            )
                        )
                    s += 1

        plt.axis('off')
        plt.ion()
        plt.show()

        for p in self.plot_handles:
            p.remove()

        self.plot_handles = []

        if U is not None:
            for u in range(len(U)):
                if self.grid[u]<1:
                    continue

                y = np.floor(u/self.W)+0.5
                x = u%self.W+0.5

                if self.grid[u]==2:
                    bbox = dict(facecolor='none', edgecolor='red')
                elif self.grid[u]==4:
                    bbox = dict(facecolor='none', edgecolor='green')
                else:
                    bbox = None

                self.plot_handles.append(self.h.text(x, y, "%.3f" % U[u],verticalalignment='center', horizontalalignment='center', fontsize=16, bbox=bbox))
        elif Q is not None:
            for u in range(len(Q)):
                y = np.floor(u / self.W) + 0.5
                x = u % self.W + 0.5

                if self.grid[u]==1:

                    ps = Q[u,:]
                    ps = np.exp((ps - np.min(ps))*gamma)

                    ps = ps/np.sum(ps)
                    for j in range(len(ps)):
                        if j == 0:
                            x2 = 0
                            y2 = 0.5
                        elif j == 1:
                            x2 = 0.5
                            y2 = 0
                        elif j == 2:
                            x2 = 0
                            y2 = -0.5
                        else:
                            x2 = -0.5
                            y2 = 0

                        x2 *= ps[j]*0.6
                        y2 *= ps[j]*0.6
                        self.plot_handles.append(self.h.arrow(x, y, x2, y2, head_width=0.05, head_length=0.1, fc='k', ec='k'))
                elif self.grid[u] > 1:
                    if self.grid[u] == 2:
                        bbox = dict(facecolor='none', edgecolor='red')
                    elif self.grid[u] == 4:
                        bbox = dict(facecolor='none', edgecolor='green')
                    else:
                        bbox = None

                    self.plot_handles.append(self.h.text(x, y, "%.3f" % self.R[u],verticalalignment='center', horizontalalignment='center', fontsize=16, bbox=bbox))

        plt.pause(0.01)
        time.sleep(0.01)