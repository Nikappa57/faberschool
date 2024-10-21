import os
import cv2


class Camera:

	def __init__(self, filename=None) -> None:
		
		self.out = None
		self.filename = filename

		if self.filename:
			print(f"Opening file: {self.filename}")
			self.cap = cv2.VideoCapture(self.filename)
		else:
			self.cap = cv2.VideoCapture(2)

			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

	def start(self):
		if not self.cap.isOpened():
			if self.filename:
				self.cap.open(self.filename)
			else:
				self.cap.open(0)
		if not self.cap.isOpened():
			raise RuntimeError("Failed to open camera")

	def get_frame(self):
		ret, frame = self.cap.read()
		if not ret:
			return None

		return frame

	def stop(self):
		if self.cap.isOpened():
			self.cap.release()
		cv2.destroyAllWindows()

	def show_frame(self, frame):
		cv2.imshow("RGB", frame)

		if cv2.waitKey(1) & 0xFF == ord("q"):
			return False
		return True
	
	def start_recording(self, filename='output.mp4'):
		if not os.path.exists('recs'):
			os.makedirs('recs')	
		# formato: mp4
		self.out = cv2.VideoWriter(f"recs/{filename}", cv2.VideoWriter_fourcc(*'mp4v'), 30, (1280, 720))

	def stop_recording(self):
		self.out.release()


if __name__ == "__main__":
	import sys
	cam = Camera()

	cam.start()
	cam.start_recording(sys.argv[1])
	while True:
		frame = cam.get_frame()
		if frame is None:
			break
		if not cam.show_frame(frame):
			break
		if cam.out:
			cam.out.write(frame)
	cam.stop_recording()
	cam.stop()
