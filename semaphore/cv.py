import os
import cv2
from ultralytics import YOLO


class Cv:

	def __init__(self, cncc=False):
		self.model = YOLO("yolo11n.pt", task='detect')

		if cncc:
			# https://docs.ultralytics.com/guides/raspberry-pi/#inference-with-camera

			if not os.path.exists("yolo11n_ncnn_model"):
				self.model.export(format="ncnn")

			self.model = YOLO("yolo11n_ncnn_model", task='detect')

	def inference(self, frame, threshold=0.50, ids=None):
		info = self.model(frame)

		result = []
		for elm in info:
			boxes = elm.boxes
			for box in boxes:
				if box.conf > threshold and (ids is None or box.cls in ids):
					x1, y1, x2, y2 = map(int, box.xyxy[0])
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

	cam = Camera()
	cv = Cv(cncc=True)
	cam.start()
	while True:
		frame = cam.get_frame()

		results = cv.inference(frame, ids=[0])
		frame = cv.draw(frame, results)
		if not cam.show_frame(frame):
			break

	cam.stop()
