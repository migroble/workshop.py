import json
from string import ascii_uppercase
import keyword
import numbers

from helper import casify
import value
from value import *

# parsing definitions
def parse_definitions(case):
	# structs for creating definitions
	class Func:
		def __init__(self, alias, string, args, type):
			self.alias  = alias
			self.string = string
			self.args   = args
			self.type   = type

	class Override:
		def __init__(self, alias = None, args = None):
			self.alias = alias
			self.args  = args
	
	definitions = {}
	overrides = {
		"==": Override("equal"),
		"!=": Override("not equal"),
		"<":  Override("less than"),
		"<=": Override("less or equal"),
		">":  Override("greater than"),
		">=": Override("greater or equal"),
		
		"ONGOING - EACH PLAYER":     Override(args=[ "team", "player" ]),
		"PLAYER DEALT DAMAGE":       Override(args=[ "team", "player" ]),
		"PLAYER DEALT FINAL BLOW":   Override(args=[ "team", "player" ]),
		"PLAYER DIED":               Override(args=[ "team", "player" ]),
		"PLAYER EARNED ELIMINATION": Override(args=[ "team", "player" ]),
		"PLAYER TOOK DAMAGE":        Override(args=[ "team", "player" ]),
	}
	ignored_types = [
		"OPERATION", "TEAM CONSTANT", "EVENT PLAYER",
		"STRING CONSTANT", "NUMBER", "DIRECTION", "BOOLEAN",
		"POSITION", "BASE", "PLAYER", "TEAM", "HERO"
	]
	
	def get_string(string):
		if len(string) == 1:
			out = string.upper()
		else:
			out = string.lower()
		return out.replace(",", "")
	
	def get_alias(string):
		alias = casify(get_override(string, "alias", string), case)
		
		if len(alias) == 1:
			alias = alias.upper()
		if keyword.iskeyword(alias):
			alias = "_" + alias
		if not alias.isidentifier():
			print(alias + " is not a valid identifier")
		
		return alias
	
	def get_args(value):
		args = []
		if "args" in value:
			for arg in value["args"]:
				name    = arg["name"].lower()
				default = arg["default"].lower()
				type    = arg["type"].lower()
				
				args.append(name)
		
		if "name" in value:
			string = value["name"]
		else:
			string = value
		
		return get_override(string, "args", args)

	def get_override(string, type, default):
		value = default
		if string in overrides:
			override = getattr(overrides[string], type)
			
			if override is not None:
				value = override
		
		return value
	
	def add_definition(string, type, args = None):
		a = args if args is not None else []
		
		if string not in definitions:
			definitions[string] = Func(get_alias(string), string, a, type)
	
	# read and pull all the definitions from workshop.json
	with open("workshop.json", "r") as f:
		data = json.load(f)
		
		for value in data["values"] + data["actions"]:
			t = ""
			for type in data["types"]:
				if value["name"] in type["values"]:
					t = type["name"].lower()
			add_definition(get_string(value["name"]), t, get_args(value))
		
		for type in data["types"]:
			if type["name"] not in ignored_types:
				for value in type["values"]:
					add_definition(get_string(value), type["name"].lower(), get_args(value))
	
	return definitions

# creating functions/constants
def define(definition):
	def get_args(params):
		args = []
		for p in params:
			if isinstance(p, Value):
				arg = p
			else:
				p_str = str(p)
				
				if definition.string == "string":
					arg = Value("\"" + p_str + "\"", "string constant")
				elif isinstance(p, numbers.Number):
					arg = Value(p_str, "number")
				elif len(p_str) == 1 and p_str.isalpha():
					arg = Value(p_str, "variable")
				else:
					arg = Value(p_str)
			
			args.append(arg)
		return args
	
	def func(*params):
		if len(params) == len(definition.args):
			return Value(definition.string, definition.type, get_args(params))
		else:
			err = definition.alias + "(" + ", ".join(definition.args) + ") takes exactly " + str(len(definition.args)) + " arguments (" + str(len(params)) + " given)"
			raise TypeError(err)
	
	if len(definition.args) == 0:
		return func()
	else:
		return func

# injecting functions/constants
def inject_definitions(obj, case = "snake"):
	# workshop.json
	for key, definition in parse_definitions(case).items():
		setattr(obj, definition.alias, define(definition))
	
	# global variables
	for var in ascii_uppercase:
		global_var = Value("global variable", "base", [ var ])
		setattr(obj, casify("global ", case) + var, global_var)
	
	# variable setters
	setattr(obj, casify("set", case), set)
	setattr(obj, casify("modify", case), modify)
	setattr(obj, casify("set at index", case), set_at_index)
	setattr(obj, casify("modify at index", case), modify_at_index)

# value needs the definitions for the overloads
inject_definitions(value)
