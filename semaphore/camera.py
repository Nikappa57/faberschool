import os
import cv2


class Camera:

	def __init__(self, camera=0) -> None:
		
		self.out = None
		self.quit = False

		try:
			camera = int(camera if camera is not None else 0)
			self.from_rec = False
		except ValueError:
			self.from_rec = True
		self.camera = camera

		if self.from_rec:
			if not os.path.exists(self.camera):
				raise FileNotFoundError(f"File {self.camera} not found")
		
		self.cap = cv2.VideoCapture(self.camera)

		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
		self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

	def start(self, record=False, filename='output.mp4'):
		if not self.cap.isOpened():
			self.cap.open(self.camera)
		if not self.cap.isOpened():
			return False
		if record:
			if not os.path.exists('recs'):
				os.makedirs('recs')	
			# formato: mp4
			self.out = cv2.VideoWriter(f"recs/{filename}", cv2.VideoWriter_fourcc(*'mp4v'), 30, (1280, 720))

		# start thread

		return True

	def get_frame(self):
		# skip first
		self.cap.read()
		ret, frame = self.cap.read()
		if not ret:
			return None
		return frame

	def stop(self):
		if self.out:
			self.out.release()
			self.out = None
		if self.cap.isOpened():
			self.cap.release()
		cv2.destroyAllWindows()
		

	def show_frame(self, frame):
		cv2.imshow("RGB", frame)
		if self.out:
			self.out.write(frame)
		return (cv2.waitKey(1) & 0xFF != ord("q"))


if __name__ == "__main__":
	import sys
	cam = Camera(sys.argv[1] if len(sys.argv) > 1 else 0)

	cam.start()
	while True:
		frame = cam.get_frame()
		if frame is None:
			break
		if not cam.show_frame(frame):
			break
		if cam.out:
			cam.out.write(frame)
	cam.stop()
