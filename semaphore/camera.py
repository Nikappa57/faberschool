import os
import cv2
import asyncio
import websockets
import base64

class Camera:

	def __init__(self, camera=0, stream: str = None) -> None:
		self.out = None
		self.stream = stream

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
		print("Camera opened")

		if self.stream:
			self.websocket = None
			self.loop = asyncio.get_event_loop()
			self.loop.run_until_complete(self.connect_websocket())
			if self.websocket is None:
				raise ConnectionError("Failed to connect to WebSocket server")

	async def connect_websocket(self):
		self.websocket = await websockets.connect(f"ws://{self.stream}/ws/semaphore")

	async def send_frame(self, frame):
		_, buffer = cv2.imencode('.jpg', frame)
		jpg_as_text = base64.b64encode(buffer).decode('utf-8')
		await self.websocket.send(jpg_as_text)

	def get_frame(self):
		# Skip first frame
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
		if self.stream and self.websocket:
			self.loop.run_until_complete(self.websocket.close())

	def show_frame(self, frame):
		cv2.imshow("RGB", frame)
		if self.out:
			self.out.write(frame)
		if self.stream and self.websocket:
			asyncio.create_task(self.send_frame(frame))
		return (cv2.waitKey(1) & 0xFF != ord("q"))

if __name__ == "__main__":
	import sys
	import random
	cam = Camera(sys.argv[1] if len(sys.argv) > 1 else 0, stream="localhost")  # Replace with your WebSocket server IP

	cam.start(record=True, filename=f"rec_{random.randint(0, 1000)}.mp4")
	try:
		while True:
			frame = cam.get_frame()
			if frame is None:
				break
			if not cam.show_frame(frame):
				break
	finally:
		cam.stop()