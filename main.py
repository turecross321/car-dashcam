import cv2 as cv
from datetime import datetime
from obd import OBDStatus
import obd
import pathlib

DEVICE = 0
WIDTH = 640
HEIGHT = 480
FPS = 24
VIDEO_DIRECTORY = "videos//"

USE_OBD = True
USE_MPH = False

FONT_SIZE = 0.7
FONT = cv.FONT_HERSHEY_SIMPLEX
FONT_COLOR = (255, 255, 255)
FONT_THICKNESS = 2

speed = None
rpm = None

def new_speed(s):
    global speed
    speed = s

def new_rpm(r):
    global rpm
    rpm = r

print(f"Ensuring {VIDEO_DIRECTORY} exists...")
# Ensure video directory exists
pathlib.Path(VIDEO_DIRECTORY).mkdir(parents=True, exist_ok=True) 

print(f"Starting video capture...")
cap = cv.VideoCapture(DEVICE)

print(f"Connecting to OBD device...")
connection = obd.Async()
connection.watch(obd.commands.SPEED, callback=new_speed)
connection.watch(obd.commands.RPM, callback=new_rpm)
connection.start()

print(f"Starting recording...")
# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*'DIVX') 
now = datetime.now()
out = cv.VideoWriter(VIDEO_DIRECTORY + now.strftime("%Y-%m-%d_%H-%M-%S") + ".mkv", fourcc, FPS, (WIDTH,  HEIGHT))

while cap.isOpened():
    date = datetime.now()

    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    outline_color = (0, 0, 0)  # Black color for the outline
    outline_thickness = FONT_THICKNESS + 3  # Slightly thicker for the outline

    date_text = date.strftime("%Y/%m/%d %H:%M:%S")
    cv.putText(frame, date_text, (0, HEIGHT), FONT, FONT_SIZE, outline_color, outline_thickness, cv.LINE_4)
    cv.putText(frame, date_text, (0, HEIGHT), FONT, FONT_SIZE, FONT_COLOR, FONT_THICKNESS, cv.LINE_4)

    if USE_OBD:
        try:
            speed_unit = "mph" if USE_MPH else "km/h"
            speed_magnitude = round(speed.value.magnitude)
            if USE_MPH:
                speed_magnitude = round(speed.value.to("mph").magnitude)
            
            rpm_magnitude = round(rpm.value.magnitude)

            obd_text = f'{rpm_magnitude} RPM {speed_magnitude} {speed_unit}'
            (obd_text_width, obd_text_height) = cv.getTextSize(obd_text, FONT, FONT_SIZE, FONT_THICKNESS)[0]
            cv.putText(frame, obd_text, (WIDTH - obd_text_width, HEIGHT), FONT, FONT_SIZE, outline_color, outline_thickness, cv.LINE_4)
            cv.putText(frame, obd_text, (WIDTH - obd_text_width, HEIGHT), FONT, FONT_SIZE, FONT_COLOR, FONT_THICKNESS, cv.LINE_4)
        except:
            pass

    out.write(frame)

cap.release()
out.release()