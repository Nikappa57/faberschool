import re
import random
from time import sleep
from typing import List
from threading import Thread
from sem_interface import SemaphoreInterface

from models import Street, Cross, Action, PriorityActionQueue, SemState


to_quit = False

# def update_cross(,crosses: List[Cross]):
# 	while comm.available():
# 		msg = comm.receive()
# 		if re.match(r"(\d+)\,(\d+)", msg):
# 			cross_id, btn_nbr = map(int, msg.split(","))
# 			print(f"Cross {cross_id} pressed button {btn_nbr}")
# 			crosses[cross_id].update_priority(btn_nbr)

def update_streets(streets: List[Street]):
	for street in streets:
		street.update_priority(random.randint(0, 10))

def btn_check_routine(sem_i: SemaphoreInterface):
	global to_quit
	while to_quit == False:
		sem_i.check_btns()
		sleep(0.5)

def sem_routine(streets, cross, sem):
	global to_quit
	queue = PriorityActionQueue()

	actions = [
		Action(0, [streets[0], cross[2]], sem_i=sem),
		Action(1, [streets[2], cross[0]], sem_i=sem),
		Action(2, [streets[3], cross[1]], sem_i=sem)
	]

	old = None
	try:
		while to_quit == False:
			print("---CICLO---")
			for a in actions:
				queue.enqueue(a)

			while not queue.empty():
				print("---step---")
				# Giallo old
				if old:
					old.update(SemState.YELLOW)
				
				# Aggiorna dati numeri di veicoli
				update_streets(streets)

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
		to_quit = True
		print("Programma interrotto manualmente.")

def main():
	streets = [Street(1, pin_green=17, pin_yellow=18, pin_red=27),
			   Street(2, pin_green=5, pin_yellow=19, pin_red=6),
			   Street(3, pin_green=16, pin_yellow=20, pin_red=26),
			   Street(4, pin_green=39, pin_yellow=38, pin_red=40)]

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
