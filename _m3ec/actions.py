
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
					iterating = True
					l = action["iterate"]
					if type(l) is str:
						l = d[l]
				else:
					iterating = False
					l = [action["source"]]
				for i in range(len(l)):
					if iterating:
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
							WRITTEN_FILES_LIST.append(dname)
						except:
							pass
						if a == "movef":
							os.remove(fname)
							if fname in WRITTEN_FILES_LIST:
								WRITTEN_FILES_LIST.remove(WRITTEN_FILES_LIST.index(fname))
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
				fname = readf(fname, d)
				with open(fname, 'w') as f:
					if type(accumulator) is dict:
						json.dump(accumulator, f)
					elif accumulator is not None:
						f.write(str(accumulator))
					WRITTEN_FILES_LIST.append(fname)

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


