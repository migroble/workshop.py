class Emitter:
	def __init__(self):
		self.rules = 0
		self.actions = 0
		self.conditions = 0
		
		self.string = ""
	
	def emit(self, code, indent, new_line = True):
		self.string += indent * "\t" + code + ("\n" if new_line else "")
	
	def emit_rule(self, rule):
		# print(rule.name)
		self.emit("rule(\"" + rule.name + "\") {", 0)
		
		self.emit("event {", 1)
		if rule.event is not None:
			self.emit(rule.event.string + ";", 2)
			
			if rule.event.args:
				self.emit(rule.event.args[0].string + ";", 2)
				self.emit(rule.event.args[1].string + ";", 2)
		else:
			self.emit("ongoing - global;", 2)
		self.emit("}", 1)
		
		if rule.actions:
			self.emit("\n\tactions {", 1)
			for action in rule.actions:
				self.emit(str(action) + ";", 2)
				self.actions += 1
			self.emit("}", 1)
		
		if rule.conditions:
			self.emit("\n\tconditions {", 1)
			for condition in rule.conditions:
				# hardcoded compare
				if condition.string == "compare":
					self.emit(str(condition.args[0]) + " ", 2, False)
					self.emit(str(condition.args[1]) + " ", 0, False)
					self.emit(str(condition.args[2]) + ";", 0)
				else:
					err = "Condition must start with compare statement\nFound \"{}\" instead of compare while evaluating rule \"{}\"".format(condition.string, rule.name)
					raise TypeError(err)
				
				self.conditions += 1
			self.emit("}", 1)
		
		self.rules += 1
		self.emit("}\n", 0)
