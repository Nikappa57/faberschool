import cv2

class Camera:
	def __init__(self) -> None:
		self.cap = cv2.VideoCapture(0)
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

	def start(self):
		if not self.cap.isOpened():
			self.cap.open(0)

	def get_frame(self):
		ret, frame = self.cap.read()
		if not ret:
			raise RuntimeError("Failed to capture image")
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

if __name__ == "__main__":
	cam = Camera()
	cam.start()
	while True:
		frame = cam.get_frame()
		if not cam.show_frame(frame):
			break
	cam.stop()
