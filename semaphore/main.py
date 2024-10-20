import cv2
import sys
import random
from time import sleep, time
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

def draw_elm_zone(frame, elm, count):
	x1, y1, x2, y2 = elm.frame_xyxy
	color = (0, 255, 0) if elm.state == SemState.GREEN else (0, 0, 255) if elm.state == SemState.RED else (0, 255, 255)
	cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
	# add background to text
	info = f"[{elm.id}]: c: {count} p: {elm.priority}"
	(text_width, text_height), baseline = cv2.getTextSize(info, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
	cv2.rectangle(frame, (x2-text_width, y2 - text_height - baseline), (x2, y2), (255, 0, 0), -1)
	cv2.putText(frame, info, (x2-text_width, y2-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
	return frame

def update_streets(streets: List[Street], camera: Camera, cv: Cv, display=False):
	global to_quit
	frame = camera.get_frame()
	if frame is None:
		to_quit = True
		return
	results = cv.inference(frame, ids=[0])
	if display:
		frame = cv.draw(frame, results)

	for street in streets:
		filtered_result = [r for r in results if street.is_inside(r)]
		street.update_priority(len(filtered_result))

		# draw street zone
		if display:
			frame = draw_elm_zone(frame, street, len(filtered_result))
		# results = results - filtered_result

	if display and not camera.show_frame(frame):
		to_quit = True


def sem1_routine(streets, actions):
	"""
	Mode 1: Classic Semaphore
	"""
	global to_quit
	queue = PriorityActionQueue()

	try:
		camera = Camera(sys.argv[1] if len(sys.argv) > 1 else None)
		cv = Cv("last.pt")

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

				# Aggiorna dati numeri di veicoli
				update_streets(streets, camera, cv)

				sleep(3)

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
				# print("Green time:", new.green_time)
				sleep(new.best_green_time)

	except KeyboardInterrupt:
		print("Programma interrotto manualmente.")
	finally:
		to_quit = True
		camera.stop()

#### MODE 2 ####

def update_streets_routine(streets: List[Street]):
	global to_quit
	camera = Camera(sys.argv[1] if len(sys.argv) > 1 else None)
	cv = Cv("best.pt")

	while not to_quit:
		update_streets(streets, camera, cv, display=True)

	camera.stop()

def sem2_routine(actions: List[Action], elements: List[Element]):
	global to_quit
	old:Action = None
	STEP_TIME = 1
	YELLOW_TIME = 1

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
	streets = [Street(1, pin_green=17, pin_yellow=18, pin_red=27, frame_xyxy=[0,350,690,660]),
			   Street(2, pin_green=5, pin_yellow=19, pin_red=6, frame_xyxy=[780,450,1280,720]),
			   Street(3, pin_green=16, pin_yellow=20, pin_red=26, frame_xyxy=[380,0,713,190]),
			   Street(4, pin_green=39, pin_yellow=38, pin_red=40, frame_xyxy=[776,80,1078,225])]

	cross = [Cross(5, pin_green=12, pin_red=18, pin_btn1=24, pin_btn2=25),
			 Cross(6, pin_green=7, pin_red=8, pin_btn1=10, pin_btn2=9),
			 Cross(7, pin_green=11, pin_red=4, pin_btn1=14, pin_btn2=15)]

	sem = SemaphoreInterface(streets, cross)
	sem.setup()

	actions = [
		Action(0, [streets[0], streets[3], cross[0]], sem_i=sem),
		Action(1, [streets[1], cross[0]], sem_i=sem),
		# Action(2, [streets[2], cross[1]], sem_i=sem),
		Action(3, [streets[3], cross[2]], sem_i=sem)
	]

	btn_check = Thread(target=btn_check_routine, args=(sem,))
	btn_check.start()
	
	# sem_thread = Thread(target=sem1_routine, args=(streets, actions))
	# sem_thread.start()

	sem_thread = Thread(target=sem2_routine, args=(actions, streets+cross))
	sem_thread.start()

	update_streets_routine(streets)

	# upd_street = Thread(target=update_streets_routine, args=(streets,))
	# upd_street.start()

	sem_thread.join()
	btn_check.join()
	# upd_street.join()


if __name__ == "__main__":
	main()
