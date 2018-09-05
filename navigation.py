import numpy as np
import cv2
import aSearch
import math
import threading
import communicator

# finals
class navigator:

    def __init__(self):
        self.my_font = cv2.FONT_HERSHEY_SIMPLEX
        self.capture = cv2.VideoCapture(0)
        self.client = None
        self.conversion = 3.65
        # codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        # out1 = cv2.VideoWriter('/Users/james/Desktop/robot_vid_raw.avi', codec, 20, (960, 540))
        # out2 = cv2.VideoWriter('/Users/james/Desktop/robot_vid_warped.avi', codec, 20, (960, 540))
        self.out1 = None
        self.out2 = None

        self.lower_hueR = np.array([75, 0, 0])
        self.upper_hueR = np.array([255, 50, 50])

        self.lower_hueG = np.array([30, 65, 30])
        self.upper_hueG = np.array([60, 100, 60])

        self.lower_hueB = np.array([0, 0, 55])
        self.upper_hueB = np.array([60, 140, 200])

        self.black = np.array([0, 0, 0])

        np.set_printoptions(threshold=np.nan)
        self.kernelOpen = np.ones((5, 5))
        self.kernelClose = np.ones((20, 20))
        self.watcher_loop = True


    def warp_me(self, feed):
        top_left = [379, 0]
        top_right = [954, 116]
        bottom_left = [379, 540]
        bottom_right = [954, 442]
        points = np.array([bottom_left, bottom_right, top_right, top_left])
        dest_top_left = [0, 0]
        dest_top_right = [960, 0]
        dest_bottom_left = [0, 540]
        dest_bottom_right = [960, 540]
        dest_points = np.array([dest_bottom_left, dest_bottom_right, dest_top_right, dest_top_left])
        pts = np.float32(points.tolist())
        dest_pts = np.float32(dest_points.tolist())

        perspective = cv2.getPerspectiveTransform(pts, dest_pts)
        image_size = (feed.shape[1], feed.shape[0])
        warped_frame = cv2.warpPerspective(feed, perspective, dsize=image_size, flags=cv2.INTER_LINEAR)
        return warped_frame


    def watcher(self):
        while(self.watcher_loop):
            r, f = self.capture.read()
            f = cv2.resize(f, (0, 0), None, .5, .5)
            if r:
                self.out1.write(f)
            f = self.warp_me(f)
            if r:
                self.out2.write(f)


    def section_dict(self, original):
        grid = {}
        for i in range(5):
            for j in range(3):
                x_min = 192 * i
                y_min = 180 * j
                grid[str(i) + str(j)] = original[y_min:y_min + 180, x_min:x_min + 192]
        return grid


    def threshold(self, rgb_frame, colour):
        if colour == 'Red':
            masked = cv2.inRange(rgb_frame, self.lower_hueR, self.upper_hueR)
        elif colour == 'Black':
            masked = cv2.inRange(rgb_frame, self.black, self.black)
        else:
            masked = cv2.inRange(rgb_frame, self.lower_hueB, self.upper_hueB)


        # further editing, remove noise in feed
        mask_open = cv2.morphologyEx(masked, cv2.MORPH_OPEN, self.kernelOpen)
        mask_close = cv2.morphologyEx(mask_open, cv2.MORPH_CLOSE, self.kernelClose)

        return mask_close


    def find_relevant_contours(self, raw_contours):
        relevent_contours = []

        for c in raw_contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            # 4 stands for 4 points to object.
            if len(approx) == 4:
                relevent_contours.append(approx)

        return relevent_contours


    def draw_all(self, rgb_frame, robot_lines, wall_lines):
        cv2.drawContours(rgb_frame, robot_lines, -1, (0, 255, 0), 3)
        if len(wall_lines) > 0:
            cv2.drawContours(rgb_frame, wall_lines, -1, (255, 0, 0), 3)

        return


    def find_robot(self, grid):
        robot_locales = {}
        mask2 = self.threshold(list(grid.values())[0], 'Black')

        for key, value in grid.items():
            mask1 = self.threshold(value, 'Red')

            if np.any(mask1 != mask2):
                robot_locales[key] = grid[key]

        return robot_locales


    def find_walls(self, grid):
        wall_locales = {}
        mask2 = self.threshold(list(grid.values())[0], 'Black')

        for key, value in grid.items():
            mask1 = self.threshold(value, 'Blue')

            if np.any(mask1 != mask2):
                wall_locales[key] = grid[key]

        return wall_locales


    def build_actions(self, grid, wall_locales, target):
        robot_locales = self.find_robot(grid)

        robot_key = list(robot_locales.keys())[0]
        goal_key = target
        if robot_key == goal_key:
            return []

        state_moves = aSearch.find_path(grid, wall_locales, goal_key, robot_key)
        if state_moves is None:
            return None

        commands = self.convert(state_moves)
        print ('----------------')
        print(robot_key, ', ', goal_key)
        print(commands)

        return commands


    def convert(self, state_moves):
        commands = []
        start = state_moves[0]
        direction = 'e'
        change = str(int(start[0]) + 1) + start[1]

        states = state_moves[1:]
        for state in states:
            x_dif = int(state[0]) - int(start[0])
            y_dif = int(state[1]) - int(start[1])

            if x_dif == -1 and direction == 'e':
                commands.append('rt 340')
                commands.append('t 1')
            elif change != state:
                if direction == 's' or direction == 'w':
                    turn = (x_dif+y_dif) * 170 * -1
                    commands.append('rt ' + str(turn))
                    commands.append('t 1')
                else:
                    turn = (x_dif + y_dif) * 170
                    commands.append('rt ' + str(turn))
                    commands.append('t 1')
            commands.append('m start')

            start = state
            if x_dif > 0:
                direction = 'e'
                change = str(int(start[0]) + 1) + start[1]
            elif x_dif < 0:
                direction = 'w'
                change = str(int(start[0]) - 1) + start[1]
            elif y_dif > 0:
                direction = 's'
                change = start[0] + str(int(start[1]) + 1)
            else:
                direction = 'n'
                change = start[0] + str(int(start[1]) - 1)
        #commands.append('st start')
        return commands


    def normalise(self, x, y):
        n =  math.sqrt((x**2) + (y**2))
        return n


    def get_angle_difference(self, x1, y1, x2, y2, xo, yo):
        plane_normal = np.array([0, 0, 1])

        x1_vector = xo - x1
        y1_vector = yo - y1
        x2_vector = xo - x2
        y2_vector = yo - y2

        n1 = self.normalise(x1_vector, y1_vector)
        n2 = self.normalise(x2_vector, y2_vector)
        x1n_vector = x1_vector / n1
        y1n_vector = y1_vector / n1
        x2n_vector = x2_vector / n2
        y2n_vector = y2_vector / n2

        output = ((y2n_vector*y1n_vector) + (x2n_vector*x1n_vector))

        v1 = np.array([x1_vector, y1_vector])
        v2 = np.array([x2_vector, y2_vector])
        crossp = np.cross(v1, v2)
        dotp = np.dot(crossp, plane_normal)

        angle_diff = math.degrees(math.acos(output))
        if dotp[2] < 0:
            angle_diff *= -1

        return angle_diff


    def get_robot_centre(self, colour):
        masked = self.threshold(colour, 'Red')
        z, robot_hats, z = cv2.findContours(masked.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        x_coords = []
        y_coords = []
        front_hat = 0
        length = 9999
        for index, contour in enumerate(robot_hats):
            # print(len(contour))
            moments = cv2.moments(contour)
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            if index == 0:
                cv2.circle(colour, (cx, cy), 7, (255, 255, 255), -1)
            else:
                cv2.circle(colour, (cx, cy), 7, (0, 255, 255), -1)
            cv2.drawContours(colour, robot_hats, -1, (255, 0, 0), 3)
            x_coords.append(cx)
            y_coords.append(cy)
            if len(contour) < length:
                front_hat = index
                length = len(contour)

        robot_central_x = int(max(x_coords) - ((max(x_coords) - min(x_coords)) / 2))
        robot_central_y = int(max(y_coords) - ((max(y_coords) - min(y_coords)) / 2))
        return x_coords, y_coords, robot_central_x, robot_central_y, front_hat


    def get_details(self):
        rete, framez = self.capture.read()
        framez = cv2.resize(framez, (0, 0), None, .5, .5)
        # cv2.imshow('testing123', framez)
        framez = self.warp_me(framez)
        colour = cv2.cvtColor(framez, cv2.COLOR_BGR2RGB)
        x_coords, y_coords, robot_central_x, robot_central_y, front_hat = self.get_robot_centre(colour)

        return colour, x_coords, y_coords, robot_central_x, robot_central_y, front_hat


    def calculated_turn(self, current_x, current_y, destination_x, destination_y, origin_x, origin_y):
        turn_degrees = self.get_angle_difference(current_x, current_y, destination_x, destination_y, origin_x, origin_y)
        turn_angle = int(turn_degrees * 1.9)

        self.client.command('rt ' + str(turn_angle))#, receive_client)

        return


    def re_align(self, colour, grid):
        robot_locales = self.find_robot(grid)
        x_coords, y_coords, robot_central_x, robot_central_y, front_hat = self.get_robot_centre(colour)

        closest_x = None
        closest_y = None
        smallest_distance = 9999
        for key, section in robot_locales.items():
            central_x = int((192 * int(key[0])) + (192/2))
            central_y = int((180 * int(key[1])) + (180/2))
            x_distance = abs(robot_central_x - central_x)
            y_distance = abs(robot_central_y - central_y)
            distance = x_distance + y_distance

            if distance < smallest_distance:
                closest_x = central_x
                closest_y = central_y
                smallest_distance = distance

        self.calculated_turn(x_coords[front_hat], y_coords[front_hat], closest_x,
                        closest_y, robot_central_x, robot_central_y)

        # cv2.circle(colour, (robot_central_x, robot_central_y), 7, (255, 0, 0), -1)
        # cv2.circle(colour, (closest_x, closest_y), 7, (0, 255, 0), -1)
        # cv2.imshow('Does the math add up? v1', colour)

        colour, x_coords, y_coords, robot_central_x, robot_central_y, front_hat = self.get_details()
        x_distance = abs(robot_central_x - closest_x)
        y_distance = abs(robot_central_y - closest_y)
        distance = x_distance + y_distance

        self.client.command('md ' + str(int(distance * self.conversion)))#, receive_client)
        i = 0
        while i < 2:
            if self.client.action_complete:
                colour, x_coords, y_coords, robot_central_x, robot_central_y, front_hat = self.get_details()
                east_point_x = robot_central_x + 80
                east_point_y = robot_central_y
                self.calculated_turn(x_coords[front_hat], y_coords[front_hat], east_point_x,
                                east_point_y, robot_central_x, robot_central_y)
                i += 1

        return


    def pre_re_align(self):
        rete, framez = self.capture.read()
        framez = cv2.resize(framez, (0, 0), None, .5, .5)
        framez = self.warp_me(framez)
        colour = cv2.cvtColor(framez, cv2.COLOR_BGR2RGB)
        grid = self.section_dict(colour)
        self.re_align(colour, grid)


    def get_turn(self, command):
        colour, x_coords, y_coords, robot_central_x, robot_central_y, front_hat = self.get_details()
        x_diff = x_coords[front_hat] - robot_central_x
        y_diff = y_coords[front_hat] - robot_central_y

        dest_x = 0
        dest_y = 0
        rcx = robot_central_x
        if abs(x_diff) > abs(y_diff):
            dest_y = robot_central_y
            dest_x = robot_central_x + int((x_diff * 1.5))
        else:
            # cv2.imshow('Does the math add up? v1' + str(dest_y + 99), colour)
            # cv2.circle(colour, (robot_central_x, robot_central_y), 7, (255, 0, 0), -1)
            # cv2.circle(colour, (dest_x, dest_y), 7, (0, 255, 0), -1)
            # cv2.imshow('Does the math add up? v1' + str(dest_x), colour)
            dest_x = robot_central_x
            dest_y = robot_central_y + int((y_diff * 1.5))



        angle_diff = self.get_angle_difference(x_coords[front_hat], y_coords[front_hat], dest_x, dest_y, rcx,
                             robot_central_y)
        angle = angle_diff * 1.9
        #if command[0] == 't':
            #return 't ' + str(int(angle))
        #else:
        return 'rt ' + str(int(angle))


    def get_move(self, command, robot_key):
        colour, x_coords, y_coords, robot_central_x, robot_central_y, front_hat = self.get_details()

        x_diff = x_coords[front_hat] - robot_central_x
        y_diff = y_coords[front_hat] - robot_central_y
        #x = 192,  y = 180
        print("=====\n", robot_key)
        if abs(x_diff) > abs(y_diff):
            if x_coords[front_hat] > robot_central_x:
                #pointing towards 4n
                next_key = str(int(robot_key[0]) + 1) + robot_key[1]
                print('here 1: ', next_key, "\n=====")
                next_x = int(next_key[0]) * 192 + (192/2)
                distance = (next_x - robot_central_x) * 3.9
            else:
                #pointing towards 0n
                next_key = str(int(robot_key[0]) - 1) + robot_key[1]
                print('here 2: ', next_key, "\n=====")
                next_x = int(next_key[0]) * 192 + (192 / 2)
                distance = (robot_central_x - next_x) * 3.9
        else:
            if y_coords[front_hat] > robot_central_y:
                #pointing towards n3
                next_key = robot_key[0] + str(int(robot_key[1]) + 1)
                print('here 2: ', next_key, "\n=====")
                next_y = int(next_key[1]) * 180 + (180 / 2)
                distance = (next_y - robot_central_y) * 3.9
            else:
                #pointing towards n0
                next_key = robot_key[0] + str(int(robot_key[1]) - 1)
                print('here 3: ', next_key, "\n=====")
                next_y = int(next_key[1]) * 180 + (180 / 2)
                distance = (robot_central_y - next_y) * 3.9

        com = "md " + str(int(distance))
        return com



    def command_brain(self, commands, robot_locales, command_count):
        count = command_count
        looper = True
        robot_key = list(robot_locales.keys())[0]
        if count < len(commands) and self.client.action_complete:
            com = commands[count]
            if commands[count][0:1] == 't':
                com = self.get_turn(commands[count])
            elif commands[count][0:1] == 'm':
                com = self.get_move(commands[count], robot_key)
            print (com)
            t1 = threading.Thread(target = self.client.command, args = [com])
            t1.start()
            print('command sent')
            count += 1

        if count >= len(commands) and self.client.action_complete:
            print (list(robot_locales.keys()))
            print('----------------')
            # print('Terminating Connection')
            # t1 = threading.Thread(target=client.quit)
            # t1.start()
            looper = False
            cv2.destroyAllWindows()
        return count, looper


    def self_navigate(self, comms, reset_point):
        #robot_placed = input('Please place robot, enter anything to continue when done')
        # threading.Thread(target = watcher).start()
        self.client = comms

        self.pre_re_align()

        # watcher_loop = False
        # sleep(1)

        ret, frame = self.capture.read()
        frame = cv2.resize(frame, (0, 0), None, .5, .5)
        # cv2.imwrite('/Users/james/Desktop/frame.png', frame)
        frame = self.warp_me(frame)

        color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mask = self.threshold(color, 'Blue')
        h0, contours, h1 = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        wall_contours = contours
        sections = self.section_dict(color)
        wall_sections = self.find_walls(sections)

        actions = self.build_actions(sections, list(wall_sections.keys()), reset_point)
        if actions is None:
            print('no possible path, change walls or give more movement')
            return None
        elif len(actions) == 0:
            return 1

        action_count = 0
        loop = True
        while loop:
            # capture frame by frame.
            ret2, frame = self.capture.read()
            frame = cv2.resize(frame, (0, 0), None, .5, .5)
            # if ret2:
            #     out1.write(frame)
            frame = self.warp_me(frame)
            # if ret2:
            #     out2.write(frame)

            color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            current_sections = self.section_dict(color)

            robot_sections = self.find_robot(current_sections)
            if len(robot_sections) > 0:
                cv2.imshow('robot_locale: ' + list(robot_sections.keys())[0], list(robot_sections.values())[0])
                # cv2.imwrite('/Users/james/Desktop/section.png', list(robot_sections.values())[0])

            mask = self.threshold(color, 'Red')
            h2, contours, h3 = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            self.draw_all(frame, contours, wall_contours)

            action_count, loop = self.command_brain(actions, robot_sections, action_count)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        #capture.release()
        # out1.release()
        # out2.release()
        out1 = None
        out2 = None
        cv2.destroyAllWindows()
        return 1