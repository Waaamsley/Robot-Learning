import numpy as np
import cv2
import test
import ASearch
import random
import math
import threading
from time import sleep

# finals
my_font = cv2.FONT_HERSHEY_SIMPLEX
capture = cv2.VideoCapture(0)
client = test.client()
conversion = 3.65
# codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
# out1 = cv2.VideoWriter('/Users/james/Desktop/robot_vid_raw.avi', codec, 20, (960, 540))
# out2 = cv2.VideoWriter('/Users/james/Desktop/robot_vid_warped.avi', codec, 20, (960, 540))

lower_hueR = np.array([75, 0, 0])
upper_hueR = np.array([255, 50, 50])

lower_hueG = np.array([30, 65, 30])
upper_hueG = np.array([60, 100, 60])

lower_hueB = np.array([0, 0, 55])
upper_hueB = np.array([60, 105, 160])

black = np.array([0, 0, 0])

np.set_printoptions(threshold=np.nan)
kernelOpen = np.ones((5, 5))
kernelClose = np.ones((20, 20))
watcher_loop = True


def warp_me(feed):
    top_left = [164, 0]
    top_right = [960, 91]
    bottom_left = [164, 540]
    bottom_right = [960, 449]
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


def watcher():
    while(watcher_loop):
        r, f = capture.read()
        f = cv2.resize(f, (0, 0), None, .5, .5)
        if r:
            out1.write(f)
        f = warp_me(f)
        if r:
            out2.write(f)

def section_dict(original):
    grid = {}
    for i in range(6):
        for j in range(3):
            x_min = 160 * i
            y_min = 180 * j
            grid[str(i) + str(j)] = original[y_min:y_min + 180, x_min:x_min + 160]
    return grid


def draw_boxes(relevant_contours):
    for i in range(len(relevant_contours)):
        x, y, w, z = cv2.boundingRect(relevant_contours[i])
        cv2.rectangle(color, (x, y), (x + w, y + z), (0, 0, 255), 2)
        # print(str(x) + ' ' + str(y) + ' ' + str(x+w) + ' ' + str(y+h))
        cv2.putText(color, str(i + 1), (x, y + z), my_font, 1, (0, 255, 255), 1, 4)


def threshold(rgb_frame, colour):
    if colour == 'Red':
        masked = cv2.inRange(rgb_frame, lower_hueR, upper_hueR)
    elif colour == 'Black':
        masked = cv2.inRange(rgb_frame, black, black)
    else:
        masked = cv2.inRange(rgb_frame, lower_hueB, upper_hueB)


    # further editing, remove noise in feed
    mask_open = cv2.morphologyEx(masked, cv2.MORPH_OPEN, kernelOpen)
    mask_close = cv2.morphologyEx(mask_open, cv2.MORPH_CLOSE, kernelClose)


    return mask_close


def find_relevant_contours(raw_contours):
    relevent_contours = []

    for c in raw_contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # 4 stands for 4 points to object.
        if len(approx) == 4:
            relevent_contours.append(approx)

    return relevent_contours


def draw_all(rgb_frame, robot_lines, wall_lines):
    cv2.drawContours(rgb_frame, robot_lines, -1, (0, 255, 0), 3)
    if len(wall_contours) > 0:
        cv2.drawContours(rgb_frame, wall_lines, -1, (255, 0, 0), 3)

    return


def find_robot(grid):
    robot_locales = {}
    mask2 = threshold(list(grid.values())[0], 'Black')

    for key, value in grid.items():
        mask1 = threshold(value, 'Red')

        if np.any(mask1 != mask2):
            robot_locales[key] = grid[key]

    return robot_locales


def find_walls(grid):
    wall_locales = {}
    mask2 = threshold(list(grid.values())[0], 'Black')

    for key, value in grid.items():
        mask1 = threshold(value, 'Blue')

        if np.any(mask1 != mask2):
            wall_locales[key] = grid[key]

    return wall_locales


def build_actions(grid, wall_locales):
    robot_locales = find_robot(grid)

    robot_key = list(robot_locales.keys())[0]
    x_key = random.randint(0, 5)
    y_key = random.randint(0, 2)
    goal_key = str(x_key) + str(y_key)


    while robot_key == goal_key or goal_key in wall_locales:
        x_key = random.randint(0, 5)
        y_key = random.randint(0, 2)
        goal_key = str(x_key) + str(y_key)

    state_moves = ASearch.find_path(grid, wall_locales, goal_key, robot_key)
    if state_moves is None:
        return None
    commands = convert(state_moves)
    print ('----------------')
    print(robot_key, ', ', goal_key)
    print(commands)

    return commands


def convert(state_moves):
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
    commands.append('st start')
    return commands


def normalise(x, y):
    n =  math.sqrt((x**2) + (y**2))
    return n


def get_angle_difference(x1, y1, x2, y2, xo, yo):
    plane_normal = np.array([0, 0, 1])

    x1_vector = xo - x1
    y1_vector = yo - y1
    x2_vector = xo - x2
    y2_vector = yo - y2

    n1 = normalise(x1_vector, y1_vector)
    n2 = normalise(x2_vector, y2_vector)
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


def get_robot_centre(colour):
    masked = threshold(colour, 'Red')
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


def get_details():
    rete, framez = capture.read()
    framez = cv2.resize(framez, (0, 0), None, .5, .5)
    framez = warp_me(framez)
    colour = cv2.cvtColor(framez, cv2.COLOR_BGR2RGB)
    x_coords, y_coords, robot_central_x, robot_central_y, front_hat = get_robot_centre(colour)

    return colour, x_coords, y_coords, robot_central_x, robot_central_y, front_hat


def calculated_turn(current_x, current_y, destination_x, destination_y, origin_x, origin_y):
    turn_degrees = get_angle_difference(current_x, current_y, destination_x, destination_y, origin_x, origin_y)
    turn_angle = int(turn_degrees * 1.9)

    client.command('rt ' + str(turn_angle))

    return


def re_align(colour, grid):
    robot_locales = find_robot(grid)
    x_coords, y_coords, robot_central_x, robot_central_y, front_hat = get_robot_centre(colour)

    closest_x = None
    closest_y = None
    smallest_distance = 9999
    for key, section in robot_locales.items():
        central_x = int((160 * int(key[0])) + (160/2))
        central_y = int((180 * int(key[1])) + (180/2))
        x_distance = abs(robot_central_x - central_x)
        y_distance = abs(robot_central_y - central_y)
        distance = x_distance + y_distance

        if distance < smallest_distance:
            closest_x = central_x
            closest_y = central_y
            smallest_distance = distance

    calculated_turn(x_coords[front_hat], y_coords[front_hat], closest_x,
                    closest_y, robot_central_x, robot_central_y)

    # cv2.circle(colour, (robot_central_x, robot_central_y), 7, (255, 0, 0), -1)
    # cv2.circle(colour, (closest_x, closest_y), 7, (0, 255, 0), -1)
    # cv2.imshow('Does the math add up? v1', colour)

    colour, x_coords, y_coords, robot_central_x, robot_central_y, front_hat = get_details()
    x_distance = abs(robot_central_x - closest_x)
    y_distance = abs(robot_central_y - closest_y)
    distance = x_distance + y_distance

    client.command('md ' + str(int(distance * conversion)))
    i = 0
    while i < 2:
        if client.action_complete:
            colour, x_coords, y_coords, robot_central_x, robot_central_y, front_hat = get_details()
            east_point_x = robot_central_x + 80
            east_point_y = robot_central_y
            calculated_turn(x_coords[front_hat], y_coords[front_hat], east_point_x,
                            east_point_y, robot_central_x, robot_central_y)
            i += 1

    return

def pre_re_align():
    rete, framez = capture.read()
    framez = cv2.resize(framez, (0, 0), None, .5, .5)
    framez = warp_me(framez)
    colour = cv2.cvtColor(framez, cv2.COLOR_BGR2RGB)
    grid = section_dict(colour)
    re_align(colour, grid)

def something(command):
    colour, x_coords, y_coords, robot_central_x, robot_central_y, front_hat = get_details()
    x_diff = x_coords[front_hat] - robot_central_x
    y_diff = y_coords[front_hat] - robot_central_y
    sign = int(command[2:])

    dest_x = 0
    dest_y = 0

    if x_diff < 0 and abs(x_diff) > abs(y_diff):
        if sign > 0:
            dest_y = robot_central_y - 60
        else:
            dest_y = robot_central_y + 60
    elif x_diff > 0 and abs(x_diff) > abs(y_diff):
        if sign > 0:
            dest_y = robot_central_y + 60
        else:
            dest_y = robot_central_y - 60

    elif y_diff < 0 and abs(y_diff) > abs(x_diff):
        if sign > 0:
            dest_x = robot_central_x + 60
        else:
            dest_x = robot_central_x - 60
    else:
        if sign > 0:
            dest_x = robot_central_x - 60
        else:
            dest_x = robot_central_x + 60

    angle_diff = get_angle_difference(x_coords[front_hat], y_coords[front_hat], dest_x, dest_y, robot_central_x,
                         robot_central_y)
    angle = angle_diff * 1.9

    return 't ' + str(int(angle))



def command_brain(commands, robot_locales, command_count, transitioned, waiting):
    count = command_count
    transition = transitioned
    listening = waiting
    looper = True
    if count < len(commands) and client.action_complete:
        if listening:
            if count == 0 or commands[count][0] != 'm':
                com = commands[count]
                if commands[count][0] == 't':
                    com = something(commands[count])
                print(com)
                t1 = threading.Thread(target = client.command, args = [com, ])
                t1.start()
                print('command sent')
            if commands[count][0] == 't':
                count += 2
            else:
                count += 1
            transition = False
            listening = False
        if len(robot_locales) > 1 and not listening and not transition:
            transition = True
        elif len(robot_locales) == 1 and transition and not listening:
            listening = True

    if count >= len(commands) and client.action_complete:
        print (list(robot_locales.keys()))
        print('----------------')
        # print('Terminating Connection')
        # t1 = threading.Thread(target=client.quit)
        # t1.start()
        looper = False
        cv2.destroyAllWindows()
    return count, transition, listening, looper



robot_placed = input('Please place robot, enter anything to continue when done')
# threading.Thread(target = watcher).start()

while (True):
    pre_re_align()

    # watcher_loop = False
    # sleep(1)

    ret, frame = capture.read()
    frame = cv2.resize(frame, (0, 0), None, .5, .5)
    frame = warp_me(frame)
    # cv2.imwrite('/Users/james/Desktop/frame.png', frame)

    color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mask = threshold(color, 'Blue')
    h0, contours, h1 = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    wall_contours = contours
    sections = section_dict(color)
    wall_sections = find_walls(sections)

    actions = build_actions(sections, list(wall_sections.keys()))
    if actions is None:
        print('no possible path')

    action_count = 0
    moved = False
    ready = True
    loop = True
    while loop:
        # capture frame by frame.
        ret2, frame = capture.read()
        frame = cv2.resize(frame, (0, 0), None, .5, .5)
        # if ret2:
        #     out1.write(frame)
        frame = warp_me(frame)
        # if ret2:
        #     out2.write(frame)

        color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        current_sections = section_dict(color)

        robot_sections = find_robot(current_sections)
        if len(robot_sections) > 0:
            cv2.imshow('robot_locale: ' + list(robot_sections.keys())[0], list(robot_sections.values())[0])
            # cv2.imwrite('/Users/james/Desktop/section.png', list(robot_sections.values())[0])

        mask = threshold(color, 'Red')
        h2, contours, h3 = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        draw_all(frame, contours, wall_contours)

        # client.stop()
        # sleep(9)
        action_count, moved, ready, loop = command_brain(actions, robot_sections, action_count, moved, ready)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

print('here')
capture.release()
# out1.release()
# out2.release()
out1 = None
out2 = None
cv2.destroyAllWindows()
exit()
