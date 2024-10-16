from enum import Enum


class SemState(Enum):
	RED = 0
	YELLOW = 1
	GREEN = 2


class Element:

	def __init__(self, e_id, *, pin_green, pin_red):
		self.id = e_id
		self.priority:int = 0
		self.pin_green = pin_green
		self.pin_red = pin_red
		self.pin_yellow = None

	def update_priority(self, count, priority=1):
		pass

	def reset_priority(self):
		self.priority = 0

	@property
	def green_time(self):
		pass

	def __str__(self):
		return f"{self.__class__.__name__} [{self.id}]: {self.priority}"
	
	def __repr__(self):
		return self.__str__()


class Street(Element):

	def __init__(self, e_id, *, pin_green, pin_yellow, pin_red):
		super().__init__(e_id, pin_green=pin_green, pin_red=pin_red)
		self.min_green_time = 5
		self.max_green_time = 20
		self.seconds_per_elm = 1
		self.count = 0
		self.pin_yellow = pin_yellow

	def update_priority(self, count, priority=1):
		self.count = count
		self.priority += priority * count

	@property
	def green_time(self):
		return max(self.min_green_time,
				min(self.max_green_time, self.count * self.seconds_per_elm))


class Cross(Element):

	def __init__(self, e_id, *, pin_green, pin_red, pin_btn1, pin_btn2):
		super().__init__(e_id, pin_green=pin_green, pin_red=pin_red)
		self.btn_1:bool = False
		self.btn_2:bool = False
		self.pin_btn1 = pin_btn1
		self.pin_btn2 = pin_btn2

	@property
	def green_time(self):
		return 5

	def update_priority(self, btn_nbr, priority=2):
		self.btn_1 |= (btn_nbr == 0)
		self.btn_2 |= (btn_nbr == 1)
		self.priority = priority * (int(self.btn_1) + int(self.btn_2))
		print("Priority:", self.priority)


class Action:

	def __init__(self, a_id, elements, sem_i):
		self.id = a_id
		self.elements = elements
		self.sem_i = sem_i

	@property
	def priority(self):
		return sum([e.priority for e in self.elements])

	@property
	def green_time(self):
		return max([e.green_time for e in self.elements])

	def update(self, state):
		for element in self.elements:
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
