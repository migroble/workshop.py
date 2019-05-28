from helper import flatten
from value import Value

rules = []

class Rule:
	def __init__(self, name):
		self.name       = name
		self.event      = None
		self.conditions = []
		self.actions    = []
	
	def __call__(self, rule):
		def validate(array):
			values = []
			
			for v in array:
				if callable(v):
					value = v()
				else:
					value = v
				
				if value is None:
					err = "Value in rule " + self.name + " is None\nMaybe you forgot to return a value from a function?"
					raise TypeError(err)
				
				if isinstance(value, Value):
					values.append(value)
			
			return values
		
		def set_event(event):
			self.event = event
		
		def add_condition(*conditions):
			flat_conditions  = list(flatten(conditions))
			self.conditions += validate(flat_conditions)
		
		def add_action(*actions):
			flat_actions  = list(flatten(actions))
			self.actions += validate(flat_actions)
		
		rule(set_event, add_condition, add_action)
		
		rules.append(self)

class If:
	def __init__(self, condition = None, if_func = None):
		self.condition = _not(condition) if condition is not None else condition
		self.if_func   = if_func
	
	def __call__(self, func):
		def wrapper(*args, post_actions = 0, **kwargs):
			actions = list(flatten(func(*args, **kwargs)))
			
			if self.condition is not None:
				if post_actions > 0:
					actions.append(skip(post_actions))
				actions.insert(0, skip_if(self.condition, len(actions)))
			
			pre_actions = []
			if self.if_func is not None:
				actions_to_skip = len(actions) + post_actions
				pre_actions = self.if_func(*args, post_actions=actions_to_skip, **kwargs)
			
			return list(pre_actions) + actions
		return wrapper	