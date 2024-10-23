import RPi.GPIO as GPIO
from typing import List

from models import Street, Cross, SemState


class SemaphoreInterface:
	def __init__(self, streets: List[Street], cross: List[Cross]) -> None:
		self.streets = streets
		self.cross = cross

	def setup(self):
		GPIO.setmode(GPIO.BOARD)
		for s in self.streets:
			print(s.pin_green, s.pin_yellow, s.pin_red)
			GPIO.setup(s.pin_green, GPIO.OUT)
			GPIO.setup(s.pin_red, GPIO.OUT)
			GPIO.setup(s.pin_yellow, GPIO.OUT)
		for c in self.cross:
			GPIO.setup(c.pin_green, GPIO.OUT)
			GPIO.setup(c.pin_red, GPIO.OUT)
			GPIO.setup(c.btn_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.setup(c.btn_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		
		for e in self.streets + self.cross:
			self.update(e, SemState.RED)

	def update(self, elem, status):
		print("Updating element", elem, "with status", status)
		if isinstance(elem, Cross):
			self._update_cross(elem, status)
		elif isinstance(elem, Street):
			self._update_street(elem, status)
		else:
			print("Unknown element type")

	def _update_street(self, elem, status):
		if status == SemState.RED:
			GPIO.output(elem.pin_green, GPIO.LOW)
			GPIO.output(elem.pin_yellow, GPIO.LOW)
			GPIO.output(elem.pin_red, GPIO.HIGH)
		elif status == SemState.YELLOW:
			GPIO.output(elem.pin_green, GPIO.LOW)
			GPIO.output(elem.pin_yellow, GPIO.HIGH)
			GPIO.output(elem.pin_red, GPIO.LOW)
		elif status == SemState.GREEN:
			GPIO.output(elem.pin_green, GPIO.HIGH)
			GPIO.output(elem.pin_yellow, GPIO.LOW)
			GPIO.output(elem.pin_red, GPIO.LOW)

	def _update_cross(self, elem, status):
		if status == SemState.RED or status == SemState.YELLOW:
			GPIO.output(elem.pin_green, GPIO.LOW)
			GPIO.output(elem.pin_red, GPIO.HIGH)
		elif status == SemState.GREEN:
			GPIO.output(elem.pin_green, GPIO.HIGH)
			GPIO.output(elem.pin_red, GPIO.LOW)
	
	def check_btns(self):
		for c in self.cross:
			if GPIO.input(c.pin_btn1):
				c.update_priority(0)
			if GPIO.input(c.pin_btn2):
				c.update_priority(1)

	def cleanup_gpio(self):
		# Pulisce la configurazione dei pin GPIO
		GPIO.cleanup()

