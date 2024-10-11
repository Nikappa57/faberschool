import cv2
import cvzone
import numpy as np
import pandas as pd
from ultralytics import YOLO
from picamera2 import Picamera2


class Cv:
	def __init__(self):
		self.yolo = YOLO("yolov5s.pt")
		self.yolo.conf = 0.4

if __name__ == "__main__":
	while True:
		frame = picam2.capture_array()
		print(frame)
		cv2.imshow("RGB", frame)
		if cv2.waitKey(1) & 0xFF == ord("q"):
			break
