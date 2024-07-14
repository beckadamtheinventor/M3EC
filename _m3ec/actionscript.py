
from .util import readf

def execScriptFile(fname, d):
	with open(fname) as f:
		print(f"------------------------------------")
		print(f"| Executing script file {fname}... |")
		value = execScript(f.read(), d)
		print(f"| Done.                            |")
		print(f"------------------------------------")

def execScript(data, d):
	if type(data) is str:
		ld = lexScript(data, d)
		if ld is not None:
			return execActions(ld, d)
		else:
			print("Lexing of script failed. Skipping.")
	elif type(data) is list:
		return execActions(data, d)
	elif type(data) is dict:
		return execActions([data], d)
	else:
		return None

def lexWord(data, i):
	j = i
	while True:
		i += 1
		if i >= len(data):
			break
		if data[i].lower() not in "abcdefghijklmnopqrstuvwxyz_.":
			break
	return data[j:i], i

def lexScript(data, d):
	ld = []
	value, i = _lexScript(data, d, ld=ld)
	return ld

ACTION_WORDS = {
	"setkey": "setdictkey",
	"appendkey": "appenddictkey",
	"getkey": "getkey",
	"do": "doactions",
	"repeat": "repeatactions",
	"exec": "execactions",
}

def _lexScript(data, d, i=0, ld=[], depth=0, lno=1):
	while i < len(data):
		i = nextNonWhiteSpace(data, i)
		word, i = lexWord(data, i)
		if word == "\n":
			lno += 1
			continue
		elif word == " " or word == "\t":
			continue
		elif word == "}":
			if depth <= 0:
				print(f"Warning: Unmatched \"}\" on line {lno}")
			break
		elif word == "{":
			value, i = _lexScript(data, d, i, ld, depth+1, lno)
		elif word == "$":
			word2, i = lexWord(data, i)
			word3, i = lexWord(data, i)
			if word2 == "{":
				word4 = ""
				args = "${"
				while word4 != "}":
					word4, i = lexWord(data, i)
					args += word4
				value = readf(args, d)
			elif word2 == "%":
				value = d["$%"+word3]
			else:
				print(f"Warning: Syntax error on line {lno}")
		elif word in ACTION_WORDS.keys():
			pass

	return value, i

def nextNonWhiteSpace(data, i):
	while i < len(data):
		if data[i] not in " \t\n":
			return i
		i += 1
	return i

