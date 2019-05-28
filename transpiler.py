import io
import re
import uuid
import tokenize
from helper import casify

# captures specific tokens
class Captor:
	def __init__(self, output_func, start_tok, end_tok, remove_start = True, remove_end = False):
		self.start_tok = start_tok
		self.end_tok = end_tok
		self.output_func = output_func
		self.remove_start = remove_start
		self.remove_end = remove_end
		
		self.capturing = False
		self.toks = []
	
	def check_tok(self, check_tok, tok):
		if check_tok[0] == tokenize.INDENT or check_tok[0] == tokenize.DEDENT:
			return tok.type == check_tok[0]
		else:
			return tok.type == check_tok[0] and tok.string == check_tok[1]
	
	def __call__(self, tok):
		if self.capturing:
			if self.check_tok(self.end_tok, tok):
				out = self.output_func(self.toks)
				
				self.toks = []
				self.capturing = False
				
				return self.remove_end, out
			else:
				self.toks.append(tok[:2])
				return True, None
		elif self.check_tok(self.start_tok, tok):
			self.capturing = True
			return self.remove_start, None
		else:
			return False, None

# watches until a specific token and then captures
class PassthroughCaptor:
	def __init__(self, output_func, start_tok, start_capture_tok, end_capture_tok, remove_end = False):
		self.start_tok = start_tok
		self.captor = Captor(output_func, start_capture_tok, end_capture_tok, False, remove_end)
		
		self.watching = False
	
	def __call__(self, tok):
		if self.watching:
			cont, out = self.captor(tok)
			
			if out is not None:
				self.watching = False
			
			return cont, out
		elif self.captor.check_tok(self.start_tok, tok):
			self.watching = True
		
		return False, None

# struct for building switches
class Switch:
	def __init__(self):
		self.reset()
	
	def reset(self):
		self.name = None
		self.prev_func = None
		self.is_first = True

def transpile(code, case):
	# returns tokens from a string
	def to_tokens(string):
		return tokenize.tokenize(io.BytesIO(string.encode("utf-8")).readline)
	
	# returns a string from tokens
	def to_string(toks):
		return tokenize.untokenize(toks)
	
	# returns a legal identifier from a string
	def to_identifier(string):
		return re.sub(r"[^A-Za-z0-9_]", "", re.sub(r"(\s|-|=)+", "_", string)).replace("_", " ").strip().replace(" ", "_")
	
	result = []
	indent = 0
	switch_indent = -1
	
	# data for the current switch
	curr_switch = Switch()
	
	# token generators
	def rule_keyword(rule_name):
		arguments = [ casify(arg, case) for arg in [ "set event", "add condition", "add action" ] ]
		identifier = "_" + to_identifier(to_string(rule_name)) + "_" + uuid.uuid4().hex
		
		return [
			( tokenize.OP, "@" ),
			( tokenize.NAME, "Rule" ),
			( tokenize.OP, "(" ),
		] + rule_name + [
			( tokenize.OP, ")" ),
			( tokenize.NEWLINE, "\n" ),
			( tokenize.NAME, "def" ),
			( tokenize.NAME, identifier ),
			( tokenize.OP, "(" ),
			( tokenize.NAME, arguments[0] ),
			( tokenize.OP, "," ),
			( tokenize.NAME, arguments[1] ),
			( tokenize.OP, ",", ),
			( tokenize.NAME, arguments[2] ),
			( tokenize.OP, ")")
		]
	
	def switch_name(name):
		curr_switch.name = name
		
		return []
		[
			( tokenize.NAME, "def" ),
		] + name + [
			( tokenize.OP, "(" ),
			( tokenize.OP, ")")
		]
	
	def case_condition(condition):
		identifier = "_if_" + uuid.uuid4().hex
		
		function_id = None if curr_switch.is_first else curr_switch.prev_func
		cond = condition if condition else [ ( tokenize.NAME, "None" ) ]
		
		curr_switch.prev_func = identifier
		curr_switch.is_first = False
		
		return [
			( tokenize.DEDENT, "" ),
			( tokenize.OP, "@" ),
			( tokenize.NAME, "If" ),
			( tokenize.OP, "(" ),
		] + cond + [
			( tokenize.OP, "," ),
			( tokenize.NAME, str(function_id) ),
			( tokenize.OP, ")" ),
			( tokenize.NEWLINE, "\n" ),
			( tokenize.NAME, "def" ),
			( tokenize.NAME, identifier ),
			( tokenize.OP, "(" ),
			( tokenize.OP, ")" ),
			( tokenize.INDENT, (indent - 1) * "\t" ),
		]
	
	def case_body(body):
		b = []
		for tok in body:
			if tok[0] == tokenize.NEWLINE:
				b.append(( tokenize.OP, "," ))
			b.append(tok)
		
		return [
			( tokenize.INDENT, indent * "\t" ),
			( tokenize.NAME, "return" ),
			( tokenize.OP, "[" ),
			( tokenize.NEWLINE, "\n" ),
			( tokenize.INDENT, (indent + 1) * "\t" )
		] + b + [
			( tokenize.DEDENT, "" ),
			( tokenize.OP, "]" ),
			( tokenize.DEDENT, "" ),
			( tokenize.NEWLINE, "\n" )
		]
	
	rule_name_captor = Captor(rule_keyword, (tokenize.NAME, "rule"), (tokenize.OP, ":"))
	switch_name_captor = Captor(switch_name, (tokenize.NAME, "switch"), (tokenize.OP, ":"), remove_end=True)
	case_condition_captor = Captor(case_condition, (tokenize.NAME, "case"), (tokenize.OP, ":"))
	case_body_captor = PassthroughCaptor(case_body, (tokenize.NAME, "case"), (tokenize.INDENT, ""), (tokenize.DEDENT, ""))
	
	captors = [ rule_name_captor, switch_name_captor, case_condition_captor, case_body_captor ]
	
	def run_captors(captors, tok):
		cont = False
		out = []
		
		for captor in captors:
			c, o = captor(tok)
			
			cont |= c
			if o is not None:
				out.extend(o)
		
		return cont, out
	
	for tok in to_tokens(code):
		if tok.type == tokenize.ENCODING:
			encoding = tok.string
		
		if tok.type == tokenize.INDENT:
			indent += 1
		if tok.type == tokenize.DEDENT:
			indent -= 1
		
		if tok.type == tokenize.NAME and tok.string == "switch":
			switch_indent = indent
		if tok.type == tokenize.DEDENT and indent == switch_indent:
			switch_indent = -1
			result.extend(curr_switch.name + [
				( tokenize.OP, "=" ),
				( tokenize.NAME, curr_switch.prev_func ),
				( tokenize.OP, "(" ),
				( tokenize.OP, ")" ),
				( tokenize.NEWLINE, "\n" )
			])
			curr_switch.reset()
		
		cont, out = run_captors(captors, tok)
		if out is not None:
			result.extend(out)
		if cont:
			continue
		
		
		result.append(tok[:2])
	
	return to_string(result).decode(encoding)