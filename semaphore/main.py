import cv2
import argparse
from time import sleep
from typing import List
from threading import Thread

from sem_interface import SemaphoreInterface
from models import Element, Street, Cross, Action, PriorityActionQueue, SemState
from camera import Camera
from cv import Cv

to_quit = False

def btn_check_routine(sem_i: SemaphoreInterface):
	global to_quit

	while not to_quit:
		sem_i.check_btns()
		sleep(0.5)

def draw_elm_zone(frame, elm:Element, actions: List[Action], count:int):
	x1, y1, x2, y2 = elm.frame_xyxy
	color = (0, 255, 0) if elm.state == SemState.GREEN else (0, 0, 255) if elm.state == SemState.RED else (0, 255, 255)
	cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
	# add background to 
	
	priority = max(a.priority for a in actions if elm in a.elements)

	info = f"[{elm.id}]: c: {elm.count} p: {priority}"
	(text_width, text_height), baseline = cv2.getTextSize(info, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
	cv2.rectangle(frame, (x2-text_width, y2 - text_height - baseline), (x2, y2), (255, 0, 0), -1)
	cv2.putText(frame, info, (x2-text_width, y2-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
	return frame

def update_streets(streets: List[Street], actions: List[Action], camera: Camera, cv: Cv, display=False):
	global to_quit

	frame = camera.get_frame()
	print("FRAME!!!")

	if frame is None:
		to_quit = True
		return
	results = cv.inference(frame, ids=[0], threshold=0.7)
	if display:
		frame_draw = cv.draw(frame, results)

	for street in streets:
		filtered_result = [r for r in results if street.is_inside(r)]
		street.update_priority(len(filtered_result))

		# draw street zone
		if display:
			frame_draw = draw_elm_zone(frame_draw, street, actions, len(filtered_result))
		# results = results - filtered_result

	if display and not camera.show_frame(frame_draw):
		to_quit = True

#### MODE 1 ####

def sem1_routine(streets, actions, camera_src=None, model="best.pt", ncnn=False):
	"""
	Mode 1: Classic Semaphore
	"""
	global to_quit
	queue = PriorityActionQueue()

	try:
		camera = Camera(camera_src)
		cv = Cv(model, ncnn)

		camera.start()

		old = None

		while not to_quit:
			print("---CICLO---")
			for a in actions:
				queue.enqueue(a)

			while not queue.empty():
				print("---step---")
				# Giallo old
				if old:
					old.update(SemState.YELLOW)
					sleep(1)

				# Aggiorna dati numeri di veicoli
				update_streets(streets, actions, camera, cv, display=True)

				# Rosso old
				if old:
					old.update(SemState.RED)

				# Nuova azione
				new = queue.dequeue()
				if new == old and not queue.empty(): # impedisco di fare due volte la stessa azione
					temp_new = queue.dequeue()
					queue.enqueue(new)
					new = temp_new

				# Verde
				new.update(SemState.GREEN)

				old = new
				# print(f"Crosses: {[str(c) for c in cross]}")
				# print(f"Street: {[str(l) for l in streets]}")
				# print(f"Current action: {new}")
				print("Green time:", new.green_time)
				sleep(new.best_green_time)

	except KeyboardInterrupt:
		print("Programma interrotto manualmente.")
	finally:
		to_quit = True
		camera.stop()

#### MODE 2 ####

def update_streets_routine(streets: List[Street], actions: List[Action],
						   camera_src:str=None, model:str="best.pt",
						   ncnn:bool=False):
	global to_quit
	camera = Camera(camera_src)
	cv = Cv(model, ncnn)

	while not to_quit:
		update_streets(streets, actions, camera, cv, display=True)

	camera.stop()

def sem2_routine(actions: List[Action], elements: List[Element]):
	global to_quit
	old:Action = None
	STEP_TIME = 1
	YELLOW_TIME = 3.5

	# create queue
	queue = PriorityActionQueue()
	for a in actions:
		queue.enqueue(a)

	try:
		while not to_quit and not queue.empty():
			new:Action = queue.head()

			if new == old:
				green_time = STEP_TIME
			else:
				if old:
					old.update(SemState.YELLOW)
					sleep(YELLOW_TIME)
					old.update(SemState.RED)

				new.update(SemState.GREEN)
				green_time = new.green_time

			# update wait time
			for e in elements:
				e.update_wait_time(green_time)

			old = new

			sleep(green_time)
	except KeyboardInterrupt:
		print("Programma interrotto manualmente.")
	finally:
		to_quit = True


def main():
	# setup argparser
	parser = argparse.ArgumentParser(description="Semaphore controller")
	parser.add_argument("--mode", "-m", type=int, default=2, help="Mode of operation")
	parser.add_argument("--camera", "-c", type=str, default=None, help="Camera source")
	parser.add_argument("--model", "-md", type=str, default="best.pt", help="Model file")
	parser.add_argument("--ncnn", type=bool, default=False, help="Yolo ncnn export")
	args = parser.parse_args()

	# List of streets
	streets = [Street(2, pin_green=26, pin_yellow=23, pin_red=22, frame_xyxy=[0,270,580,420], min_green_time=5),
			   Street(3, pin_green=33, pin_yellow=32, pin_red=29, frame_xyxy=[817,128,1167,295], min_green_time=5),
			   Street(4, pin_green=40, pin_yellow=37, pin_red=36, frame_xyxy=[630,0,770,153], min_green_time=7),
			   Street(1, pin_green=11, pin_yellow=8, pin_red=3, frame_xyxy=[600,471,840,717], min_green_time=7)]

	# List of cross
	cross = [Cross(5, pin_green=19, pin_red=15, pin_btn1=-1, pin_btn2=-1)]

	# Semaphore interface
	sem = SemaphoreInterface(streets, cross)
	sem.setup()

	# Possible actions (ids influence the priority)
	actions = [
		Action(0, [streets[0], streets[1]], sem_i=sem),
		Action(1, [streets[2], cross[0]], sem_i=sem),
		Action(2, [streets[3], cross[0]], sem_i=sem)
	]

	# Thread for checking cross buttons
	btn_check = Thread(target=btn_check_routine, args=(sem,))
	btn_check.start()

	if args.mode == 1:
		print("Mode 1")
		sem1_routine(streets, actions, camera_src=args.camera, model=args.model, ncnn=args.ncnn)
	elif args.mode == 2:
		print("Mode 2")
		sem_thread = Thread(target=sem2_routine, args=(actions, streets+cross))
		sem_thread.start()

		update_streets_routine(streets, actions, camera_src=args.camera, model=args.model, ncnn=args.ncnn)

		sem_thread.join()
	btn_check.join()
	sem.cleanup_gpio()


if __name__ == "__main__":
	main()
