# THIS FILE IS COMPLETELY USELESS
# this is a legacy emitter created before the copy&paste
# method of importing rules, it generates a macro script
# that you then run to manually input all the data.
# it is very scuffed and possibly buggy.
# you can use it if you so choose, but it is objectively
# worse in every aspect than the copy&paste method.

import enum

class Keys(enum.Enum):
	CANCEL = "F12"
	NEXT   = "{Tab}"
	SELECT = "{Space}"
	UP     = "{Up}"
	DOWN   = "{Down}"
	LEFT   = "{Left}"
	RIGHT  = "{Right}"
	OK     = "{Escape}"
	DELETE = "{BackSpace}"
	PASTE  = "{Ctrl Down}v{Ctrl Up}"

# most of these functions follow a very "it just works" philosophy
# due to how pepega ow's keyboard navigation is. this means that
# there will be a lot of magic numbers. you have been warned
class AHKEmitter:
	def __init__(self, filename):
		self.file = open(filename, "w+")
		
		self.rules = 0
		self.total_actions = 0
		self.total_conditions = 0
		self.total_values = 0
		self.total_time = 0
		
		self.max_total_speed = 5
		self.max_menu_speed = 25
		self.min_speed = 75
		self.max_speed = self.max_total_speed
		self.speed = -1
		self.values_emitted = 0
		self.actions = 0
		self.conditions = 0
		self.flush = False
		self.input_buffer = ""
	
	def __enter__(self):
		self.emit("c(p){\n\tclipboard=\n\tclipboard:=p\n\tExitApp\n\treturn\n}\nprev:=ClipboardAll\nif WinExist(\"ahk_exe Overwatch.exe\") {\n\tWinActivate,ahk_exe Overwatch.exe", 0)
		self.emit_set_speed(self.max_speed)
		self.add_to_buffer(Keys.NEXT) # go to add rule button
		
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.emit("\tWinactivate,ahk_exe Overwatch.exe\n}\nSleep,800\nc(prev)\n" + Keys.CANCEL.value + "::\n\tc(prev)\n\treturn", 0)
		self.file.close()
	
	def add_to_buffer(self, text, n = 1):
		self.input_buffer += n * text.value
		self.total_time += 2 * n * self.speed * (3 if text == Keys.PASTE else 1)
	
	def emit(self, code, indent = 1):
		if self.flush:
			self.emit_input_buffer()
		self.file.write(indent * "\t" + code + "\n")
	
	def emit_input_buffer(self):
		self.flush = False
		if self.input_buffer:
			self.emit("ControlSend,," + self.input_buffer + ",ahk_exe Overwatch.exe")
			self.input_buffer = ""
	
	def emit_sleep(self, delay = 25):
		if delay:
			self.flush = True
			self.emit("Sleep," + str(delay))
			self.total_time += delay
	
	def emit_set_speed(self, speed):
		if self.speed != speed:
			self.speed = speed
			self.flush = True
			self.emit("SetKeyDelay " + str(speed) + "," + str(speed))
	
	def emit_select(self, delay = 25):
		self.add_to_buffer(Keys.SELECT)
		self.emit_sleep(delay)
	
	def emit_ok(self, delay = 25):
		self.add_to_buffer(Keys.OK)
		self.emit_sleep(delay)
	
	def emit_string(self, string, delay = 25):
		self.flush = True
		self.emit("clipboard:=\"" + string + "\"")
		
		if delay:
			self.emit_sleep(delay)
		self.add_to_buffer(Keys.PASTE)
		self.emit_input_buffer()
	
	def emit_enter_menu(self, options):
		self.emit_select(300)
		
		self.add_to_buffer(Keys.NEXT)
		self.add_to_buffer(Keys.UP, options)
		
		self.max_speed = self.max_menu_speed
	
	def emit_exit_menu(self):
		# wait until the menu is closed
		# for very long actions/conditions this takes
		# approximately a million years
		self.emit_ok(max(500 * (self.speed**2 // 1500), 100))
		
		self.max_speed = self.max_total_speed
		self.emit_set_speed(self.max_speed)
		
		self.total_values += self.values_emitted
		self.values_emitted = 0
	
	def emit_dropdown(self, value, slow = False):
		self.emit_select()
		if value.search:
			# the string list is so long that it lags the menu, so we
			# need to slow down A LOT if we open the string dropdown
			self.emit_string(value.string, 1000 if slow else 150)
		self.add_to_buffer(Keys.NEXT)
		self.add_to_buffer(Keys.DOWN, value.position)
		self.emit_select()
	
	def emit_text_field(self, value):
		self.input_buffer += "0"
		self.add_to_buffer(Keys.DELETE)
		self.emit_string(value.string)
		self.add_to_buffer(Keys.OK)
	
	def emit_lag_compensation(self):
		# dynamically slow down our inputs the more values a
		# menu has because the lag is actually fucking insane
		speed = min(max(25 * ((self.rules + self.actions + self.conditions + self.values_emitted) // 75), self.max_speed), self.min_speed)
		self.emit_set_speed(speed)
	
	# ESC exists menu as OK
	# ALWAYS minimize after finishing a rule
	
	# ADDRULE
	# 1..n-1: (MAXIMIZE, COPY, DOWN)
	# n: (EVENTTYPE, ADDACTION, REMOVE, UP, RENAME)
	# INFO
	# 1..n-1: (REMOVE, UP, RENAME)
	# n: (ADDCONDITION, MINIMIZE, REMOVE, COPY, UP, DOWN, RENAME)
	def emit_goto_next_event_type(self):
		# assume we start at add rule button
		# down key gives inconsistent behavior here for some reason
		self.add_to_buffer(Keys.NEXT, 1 + 3 * self.rules)
	
	def emit_goto_next_action(self):
		# assume we start at end of event type
		# self.add_to_buffer(Keys.NEXT)
		pass
	
	def emit_goto_next_condition(self):
		# assume we start at add action button
		# UP and DOWN are only traversed if theres more than one rule
		#self.emit_next(4 if self.rules == 0 else 5 + 3 * self.rules)
		self.add_to_buffer(Keys.LEFT)
	
	# options is the number of options event type has
	def emit_goto_next_minimize(self, options):
		# assume we start at add condition button
		self.add_to_buffer(Keys.UP, options + 1)
	
	def emit_goto_next_rename(self):
		# assume we start at minimize
		self.add_to_buffer(Keys.RIGHT)
	
	def emit_goto_add_rule(self):
		# assume we start at rename
		self.add_to_buffer(Keys.NEXT)
	
	def emit_goto_next_option(self, go_right = True):
		# assume we start at the end of the previous option
		self.add_to_buffer(Keys.DOWN)
		if go_right:
			# needed because vector fields have a second menu item before the dropdown
			self.add_to_buffer(Keys.LEFT)
			self.add_to_buffer(Keys.RIGHT)
	
	def emit_value(self, value, go_right = True, slow = False):
		# print(value.string)
		
		self.emit_lag_compensation()
		
		if value.dropdown:
			self.emit_dropdown(value, slow)
		else:
			self.emit_text_field(value)
		self.values_emitted += 1
		
		self.emit_goto_next_option(go_right)
		
		for i, arg in enumerate(value.args):
			slow = (value.string == "STRING" and i == 0)
			go_right &= value.string != "NUMBER"
			self.emit_value(arg, go_right, slow)
	
	def emit_action(self, action):
		self.emit_enter_menu(3)
		
		self.emit_value(action)
		self.emit_exit_menu()
		
		self.actions += 1
	
	def emit_condition(self, condition):
		self.emit_enter_menu(2)
		
		# hardcoded compare
		if condition.string == "COMPARE":
			for arg in condition.args:
				self.emit_value(arg)
		else:
			err = "Condition must start with compare statement"
			raise TypeError(err)
		self.emit_exit_menu()
		
		self.conditions += 1
	
	def emit_rule(self, rule):
		# print(rule.name)
		
		# always start at add rule button 
		self.emit_select(100)
		
		self.emit_goto_next_event_type()
		event_length = 1
		if rule.event is not None:
			event_length += len(rule.event.args)
			self.emit_value(rule.event, go_right=False)
		else:
			self.emit_goto_next_option(False)
		
		self.emit_goto_next_action()
		
		for action in rule.actions:
			self.emit_action(action)
		
		self.emit_goto_next_condition()
		for condition in rule.conditions:
			self.emit_condition(condition)
		
		self.emit_goto_next_minimize(event_length)
		self.emit_select()
		
		self.emit_goto_next_rename()
		self.emit_string(rule.name)
		
		self.emit_goto_add_rule()
		self.emit_sleep()
		
		self.rules += 1
		self.total_actions += self.actions
		self.total_conditions += self.conditions
		self.actions = 0
		self.conditions = 0
