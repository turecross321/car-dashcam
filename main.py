import cv2 as cv
from datetime import datetime
from obd import OBDStatus
import obd
import pathlib

DEVICE = 0
WIDTH = 640
HEIGHT = 480
FPS = 30
SPEED_UNIT = "kph" # = "mph"
VIDEO_DIRECTORY = "videos//"

FONT_SIZE = 0.7
FONT = cv.FONT_HERSHEY_SIMPLEX
FONT_COLOR = (255, 255, 255)
FONT_THICKNESS = 2

speed = 0
rpm = 0

def new_speed(s):
    global speed
    speed = s.value.to(SPEED_UNIT)

def new_rpm(r):
    global rpm
    rpm = r.value

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
fourcc = cv.VideoWriter_fourcc(*'XVID')
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

    if connection.status == OBDStatus.CAR_CONNECTED:
        obd_text = f'{speed} {SPEED_UNIT}, {rpm} RPM'
        (obd_text_width, obd_text_height) = cv.getTextSize(obd_text, FONT, FONT_SIZE, FONT_THICKNESS)[0]
        cv.putText(frame, obd_text, (WIDTH - obd_text_width, HEIGHT), FONT, FONT_SIZE, outline_color, outline_thickness, cv.LINE_4)
        cv.putText(frame, obd_text, (WIDTH - obd_text_width, HEIGHT), FONT, FONT_SIZE, FONT_COLOR, FONT_THICKNESS, cv.LINE_4)

    out.write(frame)

cap.release()
out.release()