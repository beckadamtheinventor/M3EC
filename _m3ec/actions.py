
import os, shutil, json
from .util import *

def execActions(actions, d, accumulator=None):
	for action in actions:
		if type(action) is not dict:
			continue

		if "action" not in action.keys():
			continue

		if "if" in action.keys() and not checkActionConditions(action["if"], d):
			continue


		a = action["action"].lower()
		# print(a)
		if a == "var":
			if "source" in action.keys() and "dest" in action.keys():
				d[readf(action["dest"], d)] = d[readf(action["source"], d)]
			elif "name" in action.keys() and "value" in action.keys():
				v = action["value"]
				if type(v) is str:
					v = readf(v, d)
				d[readf(action["name"], d)] = v

		elif a in ("setdictkey", "appenddictkey"):
			# print(action)
			if "key" in action.keys():
				if "value" in action.keys():
					value = action["value"]
				else:
					value = accumulator
				if "iterate" in action.keys():
					l = action["iterate"]
					if type(l) is not list:
						l = d[l]
					for i in range(len(l)):
						d["%i"] = i
						d["%v"] = l[i]
						if type(value) is str:
							v = readf(value, d)
						else:
							v = value
						if "dict" in action.keys():
							accumulator = action["dict"]
						else:
							accumulator = d

						k = readf(action["key"], d)
						if a == "appenddictkey":
							if k in accumulator.keys():
								if type(accumulator[k]) is not list:
									accumulator[k] = list()
								accumulator[k].append(v)
							else:
								accumulator[k] = [v]
						else:
							accumulator[k] = v
				else:
					if type(value) is str:
						v = readf(value, d)
					else:
						v = value
					if "dict" in action.keys():
						accumulator = action["dict"]
					else:
						accumulator = d
					k = readf(action["key"], d)
					if a == "appenddictkey":
						if k in accumulator.keys():
							if type(accumulator[k]) is not list:
								accumulator[k] = list()
							accumulator[k].append(v)
						else:
							accumulator[k] = [v]
					else:
						accumulator[k] = v

		elif a == "getdictkey":
			if "key" in action.keys():
				key = action["key"]
			else:
				key = accumulator
			if "iterate" in action.keys():
				accumulator = []
				l = action["iterate"]
				if type(l) is not list:
					l = d[l]
				for i in range(len(l)):
					d["%i"] = i
					d["%v"] = l[i]
					k = readf(key, d)
					if "dict" in action.keys():
						if k in action["dict"].keys():
							accumulator.append(action["dict"][k])
						elif "default" in action.keys():
							accumulator.append(action["default"])
						else:
							accumulator.append(None)
					elif k in d.keys():
						accumulator.append(d[k])
					elif "default" in action.keys():
						accumulator.append(action["default"])
					else:
						accumulator.append(None)
			else:
				k = readf(key, d)
				accumulator = None
				if k in d.keys():
					k = d[k]
					if "dict" in action.keys():
						if k in action["dict"].keys():
							accumulator = action["dict"][k]
						elif "default" in action.keys():
							accumulator = action["default"]
					elif k in d.keys():
						accumulator = d[k]
					elif "default" in action.keys():
						accumulator = action["default"]

			if "var" in action.keys():
				d[readf(action["var"], d)] = readf(accumulator, d)


		elif a == "if":
			if "condition" in action.keys() and "actions" in action.keys():
				if checkActionConditions(action["condition"], d):
					execActions(action["actions"], d, accumulator)

		elif a == "doactions":
			cond = None
			if "while" in action.keys() and "var" in action.keys():
				cond = action["var"]
			while True:
				execActions(action["actions"], d, accumulator)
				if cond is None:
					break
				if not d[cond]:
					break

		elif a == "execactions":
			if "actions" in action.keys():
				if "iterate" in action.keys():
					l = action["iterate"]
					if type(l) is str:
						l = d[l]
				else:
					l = [None]
				for i in range(len(l)):
					d["%i"] = i
					d["%v"] = l[i]
					execActions(action["actions"], d, accumulator)

			if "file" in action.keys():
				if "iterate" in action.keys():
					l = action["iterate"]
					if type(l) is str:
						l = d[l]
				else:
					l = [None]
				for i in range(len(l)):
					d["%i"] = i
					d["%v"] = l[i]
					fname = readf(action["file"], d)
					if os.path.exists(fname):
						with open(fname) as f:
							execActions(json.load(f), d, accumulator)

		elif a == "repeatactions":
			if "repeat" in action.keys():
				rep = int(action["repeat"])
				for i in range(rep):
					execActions(action["actions"], d, accumulator)

		elif a == "readf":
			if "file" in action.keys():
				d["$%f"] = action["file"]
				accumulator = readf_file(readf(action["file"], d), d)
			elif "data" in action.keys():
				accumulator = readf(action["data"], d)

		elif a == "copy" or a == "move":
			if "source" in action.keys() and "dest" in action.keys():
				fname = readf(action["source"], d)
				if os.path.exists(fname):
					if a == "copy":
						shutil.copy(fname, readf(action["dest"], d))
					elif a == "move":
						shutil.move(fname, readf(action["dest"], d))
					accumulator = fname
				else:
					accumulator = None
			else:
				if "file" in action.keys():
					fname = action["file"]
				elif "filevar" in action.keys():
					fname = d[action["filevar"]]
				else:
					fname = accumulator

				fname = readf(fname, d)
				if os.path.exists(fname):
					with open(fname) as f:
						accumulator = f.read()
				else:
					accumulator = None

		elif a == "copyf":
			if "source" in action.keys() and "dest" in action.keys():
				if "iterate" in action.keys():
					l = action["iterate"]
					if type(l) is str:
						l = d[l]
				else:
					l = [action["source"]]
				for i in range(len(l)):
					d["%i"] = i
					d["%v"] = l[i]
					fname = readf(action["source"], d)
					dname = readf(action["dest"], d)
					# print("copyf", fname, "-->", dname)
					if os.path.exists(fname):
						with open(fname) as f:
							accumulator = readf(f.read(), d)
						try:
							with open(dname, 'w') as f:
								f.write(accumulator)
						except:
							pass
						if a == "movef":
							os.remove(fname)
					else:
						accumulator = None
			else:
				if "file" in action.keys():
					fname = action["file"]
				elif "filevar" in action.keys():
					fname = d[action["filevar"]]
				else:
					fname = accumulator

				fname = readf(fname, d)
				if os.path.exists(fname):
					with open(fname) as f:
						accumulator = f.read()
				else:
					accumulator = None

		elif a == "write":
			if "dest" in action.keys() or "file" in action.keys():
				if "data" in action.keys():
					accumulator = action["data"]
				elif "var" in action.keys():
					if action["var"] in d.keys():
						accumulator = d[action["var"]]
					else:
						accumulator = None
				if "dest" in action.keys():
					fname = action["dest"]
				if "file" in action.keys():
					fname = action["file"]
				with open(readf(fname, d), 'w') as f:
					if type(accumulator) is dict:
						json.dump(accumulator, f)
					elif accumulator is not None:
						f.write(str(accumulator))

		elif a in ("makedir", "make_dir"):
			if type(action["value"]) is list:
				for value in action["value"]:
					make_dir(os.path.join(d["build_path"], readf(value, d)))
			else:
				make_dir(os.path.join(d["build_path"], readf(action["value"], d)))
		
		elif a in ("print", "display", "error"):
			if "string" in action.keys():
				print(readf(action["string"], d),end=" ")
			if "var" in action.keys():
				if action["var"] in d.keys():
					print(readf(d[action["var"]], d), end=" ")
			if "value" in action.keys():
				print(readf(action["value"], d), end=" ")
			print()
			if a == "error":
				exit(1)


def checkConditionString(condition, d):
	if " " in condition:
		condition = condition.split(" ", maxsplit=2)
		val = readf(condition.pop(0), d)
		if val.startswith("!"):
			val = val[1:]
			inverted = True
		else:
			inverted = False
		if val in d.keys():
			val = d[val]
			if condition[0] == "#contains":
				if condition[1] in val:
					return not inverted
				return inverted
			elif condition[0] == "#typeis":
				if condition[1] == "int" and type(val) is int:
					return not inverted
				elif condition[1] == "float" and type(val) is float:
					return not inverted
				elif condition[1] == "str" and type(val) is str:
					return not inverted
				elif condition[1] == "list" and type(val) is list:
					return not inverted
				elif condition[1] == "tuple" and type(val) is tuple:
					return not inverted
				elif condition[1] == "dict" and type(val) is dict:
					return not inverted
				elif condition[1] == "number" and (type(val) is int or type(val) is float):
					return not inverted
				elif condition[1] == "iterable" and (type(val) is list or type(val) is tuple):
					return not inverted
			elif condition[0] == "#startswith":
				if type(val) is str:
					if val.startswith(condition[1]):
						return not inverted
			elif condition[0] == "#endswith":
				if type(val) is str:
					if val.endswith(condition[1]):
						return not inverted
			elif condition[0] == "#length":
				if type(val) is str or type(val) is list or type(val) is tuple:
					if condition[1] == "nonzero" and len(val) > 0:
						return not inverted
					elif condition[1] == "zero" and len(val) <= 0:
						return not inverted
		return inverted

	if condition in d.keys():
		c = d["condition"]
		if type(c) is str:
			if c.lower() in ("true", "yes"):
				return True
			elif c.isnumeric():
				if "." in c:
					return float(c)
				else:
					return int(c)
			else:
				return False
		elif type(c) is bool:
			return c
		else:
			return True
	return False

def checkTrue(condition, d):
	condition = readf(condition, d)
	if condition.startswith("?"):
		return checkConditionString(condition[1:], d)
	elif condition.startswith("!"):
		if condition[1:].startswith("keyexists "):
			return condition.split(" ", maxsplit=1)[1] not in d.keys()
		else:
			return not checkDictKeyTrue(d, condition[1:])
	else:
		if condition.startswith("keyexists "):
			return condition.split(" ", maxsplit=1)[1] in d.keys()
		else:
			return checkDictKeyTrue(d, condition)

def checkActionConditions(conditions, d):
	if type(conditions) is list:
		conditions = conditions[:]
		if len(conditions):
			if conditions[0] == "^AND":
				useand = True
				usexor = False
				usexnor = False
				conditions.pop(0)
			elif conditions[0] == "^OR":
				useand = False
				usexor = False
				usexnor = False
				conditions.pop(0)
			elif conditions[0] == "^OR":
				useand = False
				usexor = True
				usexnor = False
				conditions.pop(0)
			elif conditions[0] == "^XNOR":
				useand = False
				usexor = False
				usexnor = True
				conditions.pop(0)
			else:
				useand = True
				usexor = False
				usexnor = False

			if len(conditions):
				c = conditions.pop(0)
				if type(c) is str:
					val = checkTrue(c, d)
				elif type(c) is list:
					val = checkActionConditions(c, d)
				if len(conditions):
					for condition in conditions:
						if type(condition) is str:
							v = checkTrue(condition, d)
						elif type(condition) is list:
							v = checkActionConditions(condition, d)
						else:
							continue
						if useand:
							val = val and v
						elif usexor:
							val = (val and not v) or (v and not val)
						elif usexnor:
							val = (val and v) or not (val and v)
						else:
							val = val or v
				# print(val)
				return val
		return False
	elif type(conditions) is str:
		return checkTrue(conditions, d)
	elif type(conditions) is bool or type(conditions) is int or type(conditions) is float:
		return conditions
