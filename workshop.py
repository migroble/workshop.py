import re
import os
import glob
import argparse
import tempfile
import importlib.util

import transpiler
import definitions
import decorators
import emitter

parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="*")
parser.add_argument("-o", "--output-file")
args = parser.parse_args()
		
def inject_values(obj, case):
	definitions.inject_definitions(decorators)
	definitions.inject_definitions(obj, case)
	
	setattr(obj, "Rule", decorators.Rule)
	setattr(obj, "If",   decorators.If)

def dynamic_import(path, case):
	spec = importlib.util.spec_from_file_location("rules", path)
	mod  = importlib.util.module_from_spec(spec)
	
	# this has to be done before executing the module
	# otherwise it will complain about undefined values
	inject_values(mod, case)
	
	spec.loader.exec_module(mod)
	
	return mod

def process_file(file):
	# make tmp file and dump the translated code
	fd, path = tempfile.mkstemp(suffix=".py")
	script_code = file.read()
	
	# get case
	match = re.match(r"^#case(?:\s+)(snake|pascal|camel|bikini bottom)", script_code)
	if match is not None:
		case = match.group(1)
	else:
		case = "snake"
	
	python_code = transpiler.transpile(script_code, case)
	
	with open(path, "w") as tmp:
		tmp.write(python_code)
	
	dynamic_import(path, case)
	
	os.close(fd)
	os.remove(path)

def process_paths(paths):
	if os.path.isfile(path):
		with open(path) as f:
			process_file(f)

if __name__ == "__main__":
	e = emitter.Emitter()
	
	for p in args.path:
		paths = glob.glob(p)
		for path in paths:
			process_paths(paths)
	
	for r in decorators.rules:
		e.emit_rule(r)
	
	if args.output_file:
		with open(args.output_file, "w+") as f:
			f.write(e.string)
	
	print("Rules: {}\nActions: {}\nConditions: {}\n".format(e.rules, e.actions, e.conditions))
	
	try:
		pyperclip = __import__("pyperclip")
	except ImportError:
		print("Pyperclip not found, rules could not be copied to clipboard :(")
	else:
		pyperclip.copy(e.string)
		print("Rules copied to clipboard!")
	