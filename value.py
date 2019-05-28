from string import ascii_uppercase

# setter for variables
def set(array, value):
	is_player_var = (array.string == "player variable")
	
	if is_player_var:
		return set_player_variable(array.args[0], array.args[1], value)
	else:
		return set_global_variable(array.args[0], value)

def modify(array, operation, value):
	is_player_var = (array.string == "player variable")
	
	if is_player_var:
		return modify_player_variable(array.args[0], array.args[1], operation, value)
	else:
		return modify_global_variable(array.args[0], operation, value)

# setter for arrays
def set_at_index(array, index, value):
	is_player_var = (array.string == "player variable")
	
	if is_player_var:
		return set_player_variable_at_index(array.args[0], array.args[1], index, value)
	else:
		return set_global_variable_at_index(array.args[0], index, value)

def modify_at_index(array, index, operation, value):
	is_player_var = (array.string == "player variable")
	
	if is_player_var:
		return modify_player_variable_at_index(array.args[0], array.args[1], index, operation, value)
	else:
		return modify_global_variable_at_index(array.args[0], index, operation, value)

# all values and actions are instances of this bad boy
# this class contains ALL the overloads humanly imaginable
class Value:
	def __init__(self, input_string, type = "any", args = None):
		self.string = input_string
		self.args   = args if args is not None else []
		self.type   = type
		
		# player variables
		if self.type == "player":
			for var in ascii_uppercase:
				setattr(self, var, Value("player variable", "base", [ self, var ]))
	
	# serialize
	def __str__(self):
		return self.string + ("(" + ", ".join([ str(arg) for arg in self.args ]) + ")" if len(self.args) > 0 else "")
	
	# comparison operations
	def __lt__(self, other):
		return compare(self, less_than, other)
	
	def __le__(self, other):
		return compare(self, less_or_equal, other)
	
	def __eq__(self, other):
		return compare(self, equal, other)
	
	def __ne__(self, other):
		return compare(self, not_equal, other)
	
	def __gt__(self, other):
		return compare(self, greater_than, other)
	
	def __ge__(self, other):
		return compare(self, greater_or_equal, other)
	
	# mathematical or bitwise operations
	def __abs__(self):
		return absolute_value(self)
	
	def __add__(self, other):
		return add(self, other)
	
	def __and__(self, other):
		return _and(self, other)
	
	def __floordiv__(self, other):
		return round_to_integer(divide(self, other), down)
	
	def __invert__(self):
		return _not(self)
	
	def __matmul__(self, other):
		return dot_product(self, other)
	
	def __mod__(self, other):
		return modulo(self, other)
	
	def __mul__(self, other):
		return multiply(self, other)
	
	def __neg__(self):
		return multiply(self, number(-1))
	
	def __or__(self, other):
		return _or(self, other)
	
	def __pos__(self):
		return absolute_value(self)
	
	def __pow__(self, other):
		return raise_to_power(self, other)
	
	def __sub__(self, other):
		return subtract(self, other)
	
	def __truediv__(self, other):
		return divide(self, other)
	
	def __xor__(self, other):
		return _and(_not(_and(self, other)), _or(self, other))
	
	# right hand side operations
	def __radd__(self, other):
		return add(other, self)
		
	def __rsub__(self, other):
		return subtract(other, self)
	
	def __rmatmul__(self, other):
		return dot_product(other, self)
	
	def __rmul__(self, other):
		return multiply(other, self)
	
	def __rtruediv__(self, other):
		return divide(other, self)
	
	def __floordiv__(self, other):
		return round_to_integer(divide(other, self), down)
	
	def __rmod__(self, other):
		return modulo(other, self)
	
	def __rpow__(self, other):
		return raise_to_power(other, self)
	
	def __rand__(self, other):
		return _and(other, self)
	
	def __rxor__(self, other):
		return _and(_not(_and(other, self)), _or(other, self))
	
	def __ror__(self, other):
		return _or(other, self)
	
	# array operations
	def __contains__(array, value):
		return array_contains(array, value)
	
	def countOf(array, value):
		return count_of(array, value)
	
	def __getitem__(array, index):
		if isinstance(index, slice):
			return array_slice(array, index.start, index.stop)
		else:
			return value_in_array(array, index)
	
	def indexOf(array, value):
		return index_of_array_value(array, value)
