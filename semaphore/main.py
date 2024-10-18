import cv2
import random
from time import sleep
from typing import List
from threading import Thread

from sem_interface import SemaphoreInterface
from models import Street, Cross, Action, PriorityActionQueue, SemState
from camera import Camera
from cv import Cv

to_quit = False

def btn_check_routine(sem_i: SemaphoreInterface):
	global to_quit
	while to_quit == False:
		sem_i.check_btns()
		sleep(0.5)

"""
Mode 1: Classic Semaphore
"""

def draw_elm_zone(frame, elm):
	x1, y1, x2, y2 = elm.frame_xyxy
	cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
	
	return frame

def update_streets(streets: List[Street], camera: Camera, cv: Cv):
	frame = camera.get_frame()
	results = cv.inference(frame, ids=[0])
	frame = cv.draw(frame, results)

	for street in streets:
		filtered_result = [r for r in results if street.is_in_zone(r)]
		street.update_priority(len(filtered_result))

		# results = results - filtered_result

		# draw street zone
		frame = draw_elm_zone(frame, street)

	camera.show_frame(frame)


def sem_routine(streets, cross, sem):
	global to_quit
	queue = PriorityActionQueue()

	actions = [
		Action(0, [streets[0], cross[2]], sem_i=sem),
		Action(1, [streets[2], cross[0]], sem_i=sem),
		Action(2, [streets[3], cross[1]], sem_i=sem)
	]

	camera = Camera()
	cv = Cv(cncc=True)

	camera.start()

	old = None
	try:
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
				sleep(new.green_time)

	except KeyboardInterrupt:
		print("Programma interrotto manualmente.")
	finally:
		to_quit = True
		camera.stop()

"""
Mode 2: TODO
"""

def update_streets_routine(streets: List[Street]):
	for street in streets:
		street.update_priority(random.randint(0, 10))


def main():
	streets = [Street(1, pin_green=17, pin_yellow=18, pin_red=27, frame_xyxy=[1,2,3,4]),
			   Street(2, pin_green=5, pin_yellow=19, pin_red=6, frame_xyxy=[1,2,3,4]),
			   Street(3, pin_green=16, pin_yellow=20, pin_red=26, frame_xyxy=[1,2,3,4]),
			   Street(4, pin_green=39, pin_yellow=38, pin_red=40, frame_xyxy=[1,2,3,4])]

	cross = [Cross(5, pin_green=12, pin_red=18, pin_btn1=24, pin_btn2=25),
			 Cross(6, pin_green=7, pin_red=8, pin_btn1=10, pin_btn2=9),
			 Cross(7, pin_green=11, pin_red=4, pin_btn1=14, pin_btn2=15)]

	sem = SemaphoreInterface(streets, cross)
	sem.setup()

	btn_check = Thread(target=btn_check_routine, args=(sem,))
	btn_check.start()

	sem_thread = Thread(target=sem_routine, args=(streets, cross, sem))
	sem_thread.start()

	sem_thread.join()
	btn_check.join()

if __name__ == "__main__":
	main()
