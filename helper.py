import re

def flatten(thing):
	if isinstance(thing, (list, tuple, set, range)):
		for sub in thing:
			yield from flatten(sub)
	else:
		yield thing

def casify(string, case):
	def clean_string(string):
		return re.sub(r"(\.|,|:)", "", string)
	
	def remove_spaces(string):
		return re.sub(r"(\s|-)+", "", string)
	
	def to_snake_case(string):
		return re.sub(r"(\s|-)+", "_", string)
	
	def to_pascal_case(string):
		return remove_spaces(string.title())
	
	def to_camel_case(string):
		out = to_pascal_case(string)
		if len(out) > 1:
			out = out[0].lower() + out[1:]
		return out
	
	def to_bikini_bottom_case(string):
		out = ""
		for i, char in enumerate(remove_spaces(string)):
			if i % 2 == 0:
				out += char.lower()
			else:
				out += char.upper()
		return out
	
	clean = clean_string(string)
	if case == "pascal":
		cased_string = to_pascal_case(clean)
	elif case == "camel":
		cased_string = to_camel_case(clean)
	elif case == "bikini bottom":
		cased_string = to_bikini_bottom_case(clean)
	else:
		cased_string = to_snake_case(clean)
	
	return cased_string
