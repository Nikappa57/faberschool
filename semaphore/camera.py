import cv2
from picamera2 import Picamera2

class Camera:
	def __init__(self) -> None:
		self.picam2 = Picamera2()
		self.picam2.preview_configuration.main.size = (640,480)
		self.picam2.preview_configuration.main.format = "RGB888"
		self.picam2.preview_configuration.align()
		self.picam2.configure("preview")
	
	def start(self):
		self.picam2.start()

	def get_frame(self):
		return self.picam2.capture_array()
	
	def stop(self):
		self.picam2.stop()

	def show_frame(self, frame):
		cv2.imshow("RGB", frame)
		if cv2.waitKey(1) & 0xFF == ord("q"):
			return False
		return True