
import os, shutil, json
from PIL import Image
from PIL import ImageChops
from .util import *

def execActions(actions, d, accumulator=None):
	for action in actions:
		if type(action) is not dict:
			continue

		ak = action.keys()

		if "action" not in ak:
			continue

		if "if" in ak and not checkActionConditions(action["if"], d):
			continue


		a = action["action"].lower()
		# print(a)
		if a == "var":
			if "source" in ak and "dest" in ak:
				d[readf(action["dest"], d)] = d[readf(action["source"], d)]
			elif "name" in ak and "value" in ak:
				v = action["value"]
				if type(v) is str:
					v = readf(v, d)
				d[readf(action["name"], d)] = v

		elif a in ("setdictkey", "appenddictkey"):
			# print(action)
			if "key" in ak:
				if "value" in ak:
					value = action["value"]
				else:
					value = accumulator
				if "iterate" in ak:
					l = action["iterate"]
					if type(l) is str:
						l = d[readf(l, d).lower()]
					for i in range(len(l)):
						d["%i"] = i
						d["%v"] = l[i]
						if type(value) is str:
							v = readf(value, d)
						else:
							v = value
						if "dict" in ak:
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
					if "dict" in ak:
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
			if "key" in ak:
				key = action["key"]
			else:
				key = accumulator
			if "iterate" in ak:
				accumulator = []
				l = action["iterate"]
				if type(l) is str:
					l = d[readf(l, d).lower()]
				for i in range(len(l)):
					d["%i"] = i
					d["%v"] = l[i]
					k = readf(key, d)
					if "dict" in ak:
						if k in action["dict"].keys():
							accumulator.append(action["dict"][k])
						elif "default" in ak:
							accumulator.append(action["default"])
						else:
							accumulator.append(None)
					elif k in d.keys():
						accumulator.append(d[k])
					elif "default" in ak:
						accumulator.append(action["default"])
					else:
						accumulator.append(None)
			else:
				k = readf(key, d)
				accumulator = None
				if "dict" in ak:
					if k in action["dict"].keys():
						accumulator = action["dict"][k]
					elif "default" in ak:
						accumulator = action["default"]
					else:
						accumulator = None
				elif k in d.keys():
					accumulator = d[k]
				elif "default" in ak:
					accumulator = action["default"]
				else:
					accumulator = None

			if "var" in ak:
				d[readf(action["var"], d)] = readf(accumulator, d)


		elif a == "if":
			if "condition" in ak and "actions" in ak:
				if checkActionConditions(action["condition"], d):
					execActions(action["actions"], d, accumulator)

		elif a == "doactions":
			cond = None
			if "while" in ak and "var" in ak:
				cond = action["var"]
			while True:
				execActions(action["actions"], d, accumulator)
				if cond is None:
					break
				if not d[cond]:
					break

		elif a == "execactions":
			if "actions" in ak:
				if "iterate" in ak:
					l = action["iterate"]
					if type(l) is str:
						l = d[readf(l, d).lower()]
					iterating = True
				else:
					l = [None]
					iterating = False
				for i in range(len(l)):
					if iterating:
						d["%i"] = i
						d["%v"] = l[i]
					execActions(action["actions"], d, accumulator)

			if "file" in ak:
				if "iterate" in ak:
					l = action["iterate"]
					if type(l) is str:
						l = d[readf(l, d).lower()]
					iterating = True
				else:
					l = [None]
					iterating = False
				for i in range(len(l)):
					if iterating:
						d["%i"] = i
						d["%v"] = l[i]
					fname = readf(action["file"], d)
					if os.path.exists(fname):
						with open(fname) as f:
							tmp = d["curdir"]
							d["curdir"] = os.path.dirname(fname)
							execActions(json.load(f), d, accumulator)
							d["curdir"] = tmp
					else:
						print(f"Failed to locate actions json file \"{fname}\"")

		elif a == "repeatactions":
			if "repeat" in ak:
				rep = int(action["repeat"])
				for i in range(rep):
					execActions(action["actions"], d, accumulator)

		elif a == "readf":
			if "file" in ak:
				d["$%f"] = action["file"]
				accumulator = readf_file(readf(action["file"], d), d)
			elif "data" in ak:
				accumulator = readf(action["data"], d)

		elif a == "copy" or a == "move":
			if "source" in ak and "dest" in ak:
				fname = readf(action["source"], d)
				if os.path.exists(fname):
					dname = readf(action["dest"], d)
					if not os.path.isabs(dname):
						dname = os.path.join(d["curdir"], dname)
					if a == "copy":
						if os.path.isdir(fname):
							shutil.copytree(fname, dname)
						else:
							shutil.copy(fname, dname)
					elif a == "move":
						shutil.move(fname, dname)
					accumulator = fname
				else:
					accumulator = None
			else:
				if "file" in ak:
					fname = action["file"]
				elif "filevar" in ak:
					fname = d[action["filevar"]]
				else:
					fname = accumulator

				fname = readf(fname, d)
				if not os.path.isabs(fname):
					fname = os.path.join(d["curdir"], fname)
				if os.path.exists(fname):
					with open(fname) as f:
						accumulator = f.read()
				else:
					accumulator = None

		elif a == "delete" or a == "remove":
			if "source" in ak:
				fname = readf(action["source"], d)
				if fname.startswith(d["project_path"]):
					if os.path.exists(fname):
						if os.path.isdir(fname):
							shutil.rmtree(fname)
						else:
							os.remove(fname)
				else:
					print("Warning: action attempted to delete file outside of project directory. Ignoring.")

		elif a == "copyf":
			if "source" in ak and "dest" in ak:
				if "iterate" in ak:
					iterating = True
					l = action["iterate"]
					if type(l) is str:
						l = d[readf(l, d).lower()]
				else:
					iterating = False
					l = [action["source"]]
				for i in range(len(l)):
					if iterating:
						d["%i"] = i
						d["%v"] = l[i]
					fname = readf(action["source"], d)
					if not os.path.isabs(fname):
						fname = os.path.join(d["curdir"], fname)
					dname = readf(action["dest"], d)
					if not os.path.isabs(dname):
						dname = os.path.join(d["curdir"], dname)
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
				if "file" in ak:
					fname = action["file"]
				elif "filevar" in ak:
					fname = d[action["filevar"]]
				else:
					fname = accumulator

				fname = readf(fname, d)
				if not os.path.isabs(fname):
					fname = os.path.join(d["curdir"], fname)
				if os.path.exists(fname):
					with open(fname) as f:
						accumulator = f.read()
				else:
					accumulator = None

		elif a == "write":
			if "dest" in ak or "file" in ak:
				if "data" in ak:
					accumulator = action["data"]
				elif "var" in ak:
					if action["var"] in d.keys():
						accumulator = d[action["var"]]
					else:
						accumulator = None
				if "dest" in ak:
					fname = action["dest"]
				if "file" in ak:
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
					dname = readf(value, d)
					if not os.path.isabs(dname):
						dname = os.path.join(d["build_path"], dname)
					make_dir(dname)
			else:
				dname = readf(action["value"], d)
				if not os.path.isabs(dname):
					dname = os.path.join(d["build_path"], dname)
				make_dir(dname)
		
		elif a in ("print", "display", "error"):
			if "string" in ak:
				print(readf(action["string"], d),end=" ")
			if "var" in ak:
				if action["var"] in d.keys():
					print(readf(d[action["var"]], d), end=" ")
				else:
					print("None")
			if "value" in ak:
				print(readf(action["value"], d), end=" ")
			print()
			if a == "error":
				exit(1)

		elif a in ("makeimage", "maketexture"):
			if "source" in ak:
				fname = action["source"]
				if not os.path.isabs(fname):
					fname = os.path.join(d["curdir"], fname)
				try:
					srcimg = Image.open(fname).convert("RGBA")
				except FileNotFoundError:
					print(f"Warning: Image file \"{fname}\" does not exist.")
					continue
			elif "color" in ak and "width" in ak and "height" in ak:
				srcimg = Image.new("RGBA", (width, height), action["color"])
			else:
				print(f"Warning: action \"{a}\" without a \"source\" key must have a \"color\" key, \"width\" key, and \"height\" key.")
				continue

			if "operation" in ak:
				try:
					srcimg = ImageOperation(d, srcimg, action["operation"])
				except Exception as e:
					print(f"Warning: Image operation failed.\nOriginal error: {e}")
					continue
			elif "operations" in ak:
				for op in action["operation"]:
					try:
						srcimg = ImageOperation(srcimg, op)
					except Exception as e:
						print(f"Warning: Image operation failed.\nOriginal error: {e}")
						continue
			if "color" in ak:
				color = tuple(int(c) for c in readf(action["color"], d).strip("()").split(","))
				srcimg = ImageChops.multiply(Image.new("RGBA", srcimg.size, color), srcimg)

			if "dest" in ak:
				fname = readf(action["dest"], d)
				if not os.path.isabs(fname):
					fname = os.path.join(d["curdir"], fname)
				try:
					srcimg.save(fname)
				except Exception as e:
					print(f"Warning: Failed to save image \"{fname}\".\nOriginal error: {e}")
					continue
			else:
				accumulator = srcimg




