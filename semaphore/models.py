from enum import Enum


class SemState(Enum):
	RED = 0
	YELLOW = 1
	GREEN = 2


class Element:

	def __init__(self, e_id, *, pin_green, pin_red, w_per_sec=1):
		self.id = e_id
		self._priority:int = 0
		self.pin_green = pin_green
		self.pin_red = pin_red
		self.pin_yellow = None
		self.w_per_sec = w_per_sec
		self.w_time = 0
		self.state = SemState.RED

	def update_priority(self, count, priority):
		self._priority += count * priority

	def update_wait_time(self, sec=1):
		if self._priority > 0:
			self.w_time += self.w_per_sec * sec
		else:
			self.w_time = 0

	def reset_priority(self):
		self._priority = 0
		self.w_time = 0

	@property
	def priority(self):
		return self._priority * (1 + self.w_time)

	@property
	def green_time(self):
		pass

	def __str__(self):
		return f"{self.__class__.__name__} [{self.id}]: {self.priority}"
	
	def __repr__(self):
		return self.__str__()


class Street(Element):

	def __init__(self, e_id, *, pin_green, pin_yellow, pin_red, frame_xyxy,
				min_green_time=5, max_green_time=20, seconds_per_elm=1):
		super().__init__(e_id, pin_green=pin_green, pin_red=pin_red)
		self.min_green_time = min_green_time
		self.max_green_time = max_green_time
		self.seconds_per_elm = seconds_per_elm
		self.count = 0
		self.pin_yellow = pin_yellow
		self.frame_xyxy = frame_xyxy

	def update_priority(self, count, priority=1):
		self.count = count
		self._priority += priority * count

	def is_inside(self, bb):
		x1, y1, x2, y2 = self.frame_xyxy
		return x1 <= bb[0] and y1 <= bb[1] and x2 >= bb[2] and y2 >= bb[3]

	@property
	def green_time(self):
		return max(self.min_green_time,
				min(self.max_green_time, self.count * self.seconds_per_elm))


class Cross(Element):

	def __init__(self, e_id, *, pin_green, pin_red, pin_btn1, pin_btn2, green_time=5):
		super().__init__(e_id, pin_green=pin_green, pin_red=pin_red)
		self.btn_1:bool = False
		self.btn_2:bool = False
		self.pin_btn1 = pin_btn1
		self.pin_btn2 = pin_btn2
		self._green_time = green_time

	@property
	def green_time(self):
		return self._green_time

	def update_priority(self, btn_nbr, priority=2):
		self.btn_1 |= (btn_nbr == 0)
		self.btn_2 |= (btn_nbr == 1)
		self._priority = priority * (int(self.btn_1) + int(self.btn_2))
		print("Priority:", self._priority)


class Action:

	def __init__(self, a_id, elements, sem_i, base_priority=0):
		self.id = a_id
		self.elements = elements
		self.sem_i = sem_i
		self.base_priority = base_priority

	@property
	def priority(self):
		return sum([e.priority for e in self.elements]) + self.base_priority

	@property
	def green_time(self):
		return max([e.green_time for e in self.elements])

	def update(self, state):
		for element in self.elements:
			# TODO: element.state = state
			self.sem_i.update(element, state)
			if state == SemState.GREEN:
				print(f"Green for {element}")
				element.reset_priority()

	def __str__(self):
		return f"Action [{self.id}] {self.priority}: {self.elements}"


class PriorityActionQueue:

	def __init__(self):
		self.queue = []

	def enqueue(self, action):
		self.queue.append(action)
		self.queue.sort(key=lambda x: x.priority, reverse=True)

	def dequeue(self):
		return self.queue.pop(0)

	def empty(self):
		return len(self.queue) == 0

	def head(self):
		return self.queue[0]
