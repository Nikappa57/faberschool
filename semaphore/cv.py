import os
import cv2
from ultralytics import YOLO


class Cv:

	def __init__(self, model, cncc=False):
		self.model = YOLO(model, task='detect')

		if cncc:
			# https://docs.ultralytics.com/guides/raspberry-pi/#inference-with-camera

			if not os.path.exists(model.replace(".pt", "_ncnn_model")):
				self.model.export(format="ncnn")

			self.model = YOLO(model.replace(".pt", "_ncnn_model"), task='detect')

	def inference(self, frame, threshold=0.10, ids=None):
		# Get original dimensions
		original_height, original_width = frame.shape[:2]

		# Resize the frame to the required size (e.g., 640x480)
		resized_frame = cv2.resize(frame, (640, 480))

		# Perform inference on the resized frame
		info = self.model(resized_frame, verbose=False)

		result = []
		for elm in info:
			boxes = elm.boxes
			for box in boxes:
				if box.conf > threshold and (ids is None or box.cls in ids):
					# Scale the bounding box coordinates back to the original frame size
					x1, y1, x2, y2 = map(int, box.xyxy[0])
					x1 = int(x1 * original_width / 640)
					y1 = int(y1 * original_height / 480)
					x2 = int(x2 * original_width / 640)
					y2 = int(y2 * original_height / 480)
					
					name = elm.names[int(box.cls)]
					conf = float(box.conf)
					result.append((x1, y1, x2, y2, name, conf))

		return result

	def draw(self, frame, results):
		for x1, y1, x2, y2, name, conf in results:
			cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
			label = f"{name} {conf:.2f}"
			(text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
			cv2.rectangle(frame, (x1, y1 - text_height - baseline), (x1 + text_width, y1), (0, 255, 0), -1)
			cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

		return frame

if __name__ == "__main__":
	from camera import Camera
	import sys

	cam = Camera(sys.argv[1] if len(sys.argv) > 1 else None)
	cv = Cv(model="best.pt")
	cam.start()
	cam.start_recording(f"output_{sys.argv[1].split("/")[-1] if len(sys.argv) > 1 else 'cam.mp4'}")
	try:
		while True:
			frame = cam.get_frame()
			if frame is None:
				break
			cam.out.write(frame)
			results = cv.inference(frame)
			frame = cv.draw(frame, results)
			if not cam.show_frame(frame):
				break
			cv2.waitKey(1)
	finally:
		cam.stop_recording()
		cam.stop()
