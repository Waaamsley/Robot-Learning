import numpy as np
import cv2

# window output prep. - deprecated, could be useful later
# cv2.namedWindow('environment feed', cv2.WINDOW_NORMAL)
# cv2.resizeWindow('environment feed', 300, 300)

# font
my_font = cv2.FONT_HERSHEY_SIMPLEX

capture = cv2.VideoCapture(0)

# defining black limits:
#lower_hue = np.array([0, 128, 128])
#upper_hue = np.array([150, 128, 128])

lower_hue = np.array([0, 0, 0])
upper_hue = np.array([110, 110, 110])

while (True):
    # capture frame by frame.
    ret, frame = capture.read()

    # captures video, cvtColor param2 can get color modes.
    frame = cv2.resize(frame, (0, 0), None, .5, .5)
    #color = cv2.cvtColor(frame, cv2.COLOR_BGRa2RGB)  # BGR2YUV

    #calibration?
    color = cv2.cvtColor(frame, cv2.COLOR_BGRa2YUV) #BGR2YUV


    mask = cv2.inRange(color, lower_hue, upper_hue)

    # further editing, remove noise in feed
    kernelOpen = np.ones((5, 5))
    kernelClose = np.ones((20, 20))

    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)

    # finding all contours
    maskFinal = maskClose
    h, contours, h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]

    #limiting contour list to only relevant contours
    relevent_contours = []
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # 4 stands for 4 points to object.
        if len(approx) == 4:
            relevent_contours.append(approx)

    cv2.drawContours(color, relevent_contours, -1, (0, 255, 0), 3)
    #print("{}{}{}{}{}")
    for i in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        cv2.rectangle(color, (x, y), (x+w, y+h), (0, 0, 255), 2)
        #print(str(x) + ' ' + str(y) + ' ' + str(x+w) + ' ' + str(y+h))
        cv2.putText(color, str(i+1), (x, y+h), my_font, 1, (0, 255, 255), 1, 4)

    #diplsay these frames
    cv2.imshow('frame', color)
    cv2.imshow('mask', mask)
    cv2.imshow('maskOpen', maskOpen)
    cv2.imshow('maskClose', maskClose)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()