import pygame
import random
import cv2
import mediapipe as mp
import time
from scipy.interpolate import make_interp_spline
import numpy as np
import pyautogui
from pygame.locals import *


pygame.init()
pygame.display.set_caption("Rangolify with Hand gestures")
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1000,800))

cap = cv2.VideoCapture(0)

mphands = mp.solutions.hands
hands = mphands.Hands() 
mpDraw = mp.solutions.drawing_utils
pyautogui.FAILSAFE = False  # Disables the fail-safe feature
pyautogui.PAUSE = 0  # Sets the pause time between each action

points = []
smooth_points = []
prev_time = 0
curr_time = 0


# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# Create a list of random colors
colors = []
for i in range(3):
    r = 255
    g = 87
    b = 87
    colors.append((r, g, b))
for i in range(3):
    r = 126
    g = 217
    b = 87
    colors.append((r, g, b))
for i in range(3):
    r = 140
    g = 82
    b = 255
    colors.append((r, g, b))


def draw_smooth_lines():
    # Get the current color from the colors list
    color = colors[color_index]
    # Draw four lines with different symmetries using the same color
    pygame.draw.aalines(screen, color, False, smooth_points, blend=1)
    pygame.draw.aalines(screen, color,
                         False,
                         [(1000 - x, y) for x, y in smooth_points],
                         blend=1)
    pygame.draw.aalines(screen,
                         color,
                         False,
                         [(x, 800 - y) for x, y in smooth_points],
                         blend=1)
    pygame.draw.aalines(screen,
                         color,
                         False,
                         [(1000 - x, 800 - y) for x, y in smooth_points],
                         blend=1)


# Create a variable to store the current color index
color_index = random.randint(0, len(colors) - 1)
flag = 0
while flag == 0:
    while True:
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if id == 4:
                        p1 = (cx, cy)
                    if id == 8:
                        print(id, cx, cy)
                        points.append((cx, cy))
                        p2 = (cx, cy)
                        cv2.circle(img,(cx,cy), 7,(0,0,255),cv2.FILLED)
                        d = int(((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5)
                        print(d)
                        if d < 10:
                            screen = pygame.display.set_mode((1000,800))
                            pygame.display.update()
            # Smooth the points using a spline interpolation
            smooth_points = []
            x, y = zip(*points)
            if len(points) > 2:
                t = range(len(points))
                interp_spline = make_interp_spline(t, x, bc_type='natural')
                smooth_x = interp_spline(np.linspace(0, len(points) - 1, 20))
                interp_spline = make_interp_spline(t, y, bc_type='natural')
                smooth_y = interp_spline(np.linspace(0, len(points) - 1, 20))
                smooth_points = list(zip(smooth_x, smooth_y))

        # Draw smooth lines between the points with different colors and symmetries
        if len(smooth_points) > 1:
            draw_smooth_lines()

        # Increment the color index by one and wrap around if necessary
            # Increment the color index by one and wrap around if necessary
        color_index += 1
        if color_index >= len(colors)-1:
            color_index = random.randint(0, len(colors) - 1)

        # Smooth the points using interpolation
        if len(points) > 2:
            x_coords, y_coords = zip(*points)
            t = range(len(points))
            interp_t = np.linspace(0, len(points) - 1, 1000)
            spl_x = make_interp_spline(t, x_coords, k=3, bc_type='natural')
            spl_y = make_interp_spline(t, y_coords, k=3, bc_type='natural')
            smooth_x = spl_x(interp_t)
            smooth_y = spl_y(interp_t)

        # Draw the smoothed lines
            for i in range(len(smooth_x) - 1):
                x1, y1 = int(smooth_x[i]), int(smooth_y[i])
                x2, y2 = int(smooth_x[i + 1]), int(smooth_y[i + 1])
                color = colors[color_index]
                pygame.draw.line(screen, color, (x1, y1), (x2, y2), 3)
                pygame.draw.line(screen, color, (1000 - x1, y1), (1000 - x2, y2), 3)
                pygame.draw.line(screen, color, (x1, 800 - y1), (x2, 800 - y2), 3)
                pygame.draw.line(screen, color, (1000 - x1, 800 - y1), (1000 - x2, 800 - y2), 3)

            # Update the display and tick the clock
            pygame.display.update()
            clock.tick(60)

    # Check for events and quit if necessary
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                flag = -1
                pygame.quit()
                quit()
        