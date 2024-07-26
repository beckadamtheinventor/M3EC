
import os, shutil, json
from PIL import Image
from PIL import ImageChops
from .util import *

def actionWarning(s, d={}):
	if "$%f" in d.keys():
		f = str(d["$%f"])+" "
	else:
		f = ""
	print(f"Warning: action {f}"+str(s)+".\nIgnoring.")

def actionAccessWarning(fname, d):
	actionWarning(f"attempted to access file outside of project directory and source directory.\n\
Path: \"{fname}\"\nProject Path: \"{d['project_path']}\"\nSource Path: \"{d['source_path']}\"", d)
	raise Exception

def try_load_image(fname, d):
	if not fname.startswith(d["project_path"]) and not fname.startswith(d["source_path"]):
		if os.path.isabs(fname):
			actionAccessWarning(fname, d)
			return None
		fname = os.path.join(d["project_path"], fname)
	try:
		return Image.open(fname).convert("RGBA")
	except FileNotFoundError:
		actionWarning(f"Warning: Image file \"{fname}\" does not exist.", d)
		return None

def execActions(actions, d):
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

		elif a in ("setdictkey", "appenddictkey", "setkey", "appendkey"):
			# print(action)
			if "key" in ak:
				if "value" in ak:
					value = action["value"]
				else:
					value = d["%a"]
				if "iterate" in ak:
					l = action["iterate"]
					if type(l) is str:
						l = readf(l, d).lower()
						if l not in d.keys():
							continue
						l = d[l]
					for i in range(len(l)):
						d["%i"] = i
						d["%v"] = l[i]
						if type(value) is str:
							v = readf(value, d)
						else:
							v = value
						if "dict" in ak:
							d["%a"] = action["dict"]
						else:
							d["%a"] = d

						k = readf(action["key"], d)
						if "append" in a:
							if k in d["%a"].keys():
								if type(d["%a"][k]) is not list:
									d["%a"][k] = list()
								d["%a"][k].append(v)
							else:
								d["%a"][k] = [v]
						else:
							d["%a"][k] = v
				else:
					if type(value) is str:
						v = readf(value, d)
					else:
						v = value
					if "dict" in ak:
						d["%a"] = action["dict"]
						if type(d["%a"]) is str:
							s = readf(d["%a"], d)
							if s in d.keys():
								d["%a"] = d[s]
							else:
								d["%a"] = {}
					else:
						d["%a"] = d
					k = readf(action["key"], d)
					if "append" in a:
						if k in d["%a"].keys():
							if type(d["%a"][k]) is not list:
								d["%a"][k] = list()
							d["%a"][k].append(v)
						else:
							d["%a"][k] = [v]
					else:
						d["%a"][k] = v

		elif a in ("getdictkey", "getkey"):
			if "key" in ak:
				key = action["key"]
			else:
				key = d["%a"]
			if "iterate" in ak:
				d["%a"] = []
				l = action["iterate"]
				if type(l) is str:
					l = readf(l, d).lower()
					if l not in d.keys():
						continue
					l = d[l]
				for i in range(len(l)):
					d["%i"] = i
					d["%v"] = l[i]
					k = readf(key, d)
					if "dict" in ak:
						d2 = action["dict"]
						if type(d2) is str:
							d2 = readf(d2, d)
							if d2 in d.keys():
								d2 = d[d2]
							else:
								d2 = {}
						if k in d2.keys():
							d["%a"].append(d2[k])
						elif "default" in ak:
							d["%a"].append(action["default"])
						else:
							d["%a"].append(None)
					elif k in d.keys():
						d["%a"].append(d[k])
					elif "default" in ak:
						d["%a"].append(action["default"])
					else:
						d["%a"].append(None)
			else:
				k = readf(key, d)
				d["%a"] = None
				if "dict" in ak:
					d2 = action["dict"]
					if type(d2) is str:
						d2 = readf(d2, d)
						if d2 in d.keys():
							d2 = d[d2]
						else:
							d2 = {}
					if k in d2.keys():
						d["%a"] = d2[k]
					elif "default" in ak:
						d["%a"] = action["default"]
					else:
						d["%a"] = None
				elif k in d.keys():
					d["%a"] = d[k]
				elif "default" in ak:
					d["%a"] = action["default"]
				else:
					d["%a"] = None

			if "var" in ak:
				d[readf(action["var"], d)] = readf(d["%a"], d)


		elif a == "if":
			if "condition" in ak and "actions" in ak:
				if checkActionConditions(action["condition"], d):
					execActions(action["actions"], d)

		elif a == "doactions":
			rep = 0
			while True:
				d["%i"] = rep
				rep += 1
				shouldexit = True
				if "while" in ak:
					shouldexit = not checkActionConditions(action["while"], d)
				if shouldexit:
					break
				execActions(action["actions"], d)
				if "until" in ak:
					if checkActionConditions(action["until"], d):
						break

		elif a == "execactions":
			if "actions" in ak:
				if "iterate" in ak:
					l = action["iterate"]
					if type(l) is str:
						l = readf(l, d).lower()
						if l not in d.keys():
							continue
						l = d[l]
					iterating = True
				else:
					l = [None]
					iterating = False
				for i in range(len(l)):
					if iterating:
						d["%i"] = i
						d["%v"] = l[i]
					execActions(action["actions"], d)

			if "file" in ak:
				if "iterate" in ak:
					l = action["iterate"]
					if type(l) is str:
						l = readf(l, d).lower()
						if l not in d.keys():
							continue
						l = d[l]
					iterating = True
				else:
					l = [None]
					iterating = False
				for i in range(len(l)):
					if iterating:
						d["%i"] = i
						d["%v"] = l[i]
					fname = readf(action["file"], d)
					if not fname.startswith(d["project_path"]) and not fname.startswith(d["source_path"]):
						if os.path.isabs(fname):
							actionAccessWarning(fname, d)
							continue
						fname = os.path.join(d["project_path"], fname)
					if os.path.exists(fname):
						with open(fname) as f:
							tmp = d["curdir"]
							d["curdir"] = os.path.dirname(fname)
							execActions(json.load(f), d)
							d["curdir"] = tmp
					else:
						print(f"Failed to locate actions json file \"{fname}\"")

		elif a == "repeatactions":
			if "repeat" in ak:
				rep = int(action["repeat"])
				for i in range(rep):
					d["%i"] = i
					execActions(action["actions"], d)

		elif a == "readf":
			if "dict" in ak:
				d2 = action["dict"]
			else:
				d2 = d

			if "file" in ak:
				d["$%f"] = action["file"]
				d["%a"] = readf_file(readf(action["file"], d), d2)
			elif "data" in ak:
				d["%a"] = readf(action["data"], d2)

			if "key" in ak:
				d[readf(action["key"], d)] = d["%a"]
			elif "var" in ak:
				d[readf(action["key"], d)] = d["%a"]

		elif a == "copy" or a == "move":
			if "source" in ak and "dest" in ak:
				fname = readf(action["source"], d)
				if os.path.exists(fname):
					dname = readf(action["dest"], d)
					if not os.path.isabs(dname):
						dname = os.path.join(d["curdir"], dname)
					if (fname.startswith(d["project_path"]) or fname.startswith(d["source_path"])) and dname.startswith(d["project_path"]):
						if a == "copy":
							if os.path.isdir(fname):
								shutil.copytree(fname, dname)
							else:
								shutil.copy(fname, dname)
						elif a == "move":
							shutil.move(fname, dname)
						d["%a"] = fname
					else:
						actionWarning("attempted to copy/move to/from a file/directory outside of the project directory or tried to write a file in the source directory", d)
				else:
					d["%a"] = None
			else:
				if "file" in ak:
					fname = action["file"]
				elif "filevar" in ak:
					fname = d[action["filevar"]]
				else:
					fname = d["%a"]

				fname = readf(fname, d)
				if not os.path.isabs(fname):
					fname = os.path.join(d["curdir"], fname)
				if fname.startswith(d["project_path"]) or fname.startswith(d["source_path"]):
					if os.path.exists(fname):
						with open(fname) as f:
							d["%a"] = f.read()
					else:
						d["%a"] = None
				else:
					actionAccessWarning(fname, d)

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
					actionWarning("attempted to delete file outside of project directory", d)

		elif a in ("copyf", "movef"):
			if "source" in ak and "dest" in ak:
				if "iterate" in ak:
					iterating = True
					l = action["iterate"]
					if type(l) is str:
						l = readf(l, d).lower()
						if l not in d.keys():
							continue
						l = d[l]
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
					if (fname.startswith(d["project_path"]) or fname.startswith(d["source_path"])) and dname.startswith(d["project_path"]):
						if os.path.exists(fname):
							if os.path.isdir(fname):
								fnames = list(walk(fname))
							else:
								fnames = [fname]
							for fn in fnames:
								with open(fn) as f:
									d["%a"] = readf(f.read(), d)
								if os.path.isdir(fname):
									dn = os.path.join(dname, os.path.basename(fn))
								else:
									dn = dname
								try:
									with open(dn, 'w') as f:
										f.write(d["%a"])
									# WRITTEN_FILES_LIST.append(dname)
								except:
									pass
								if a == "movef":
									if fn.startswith(d["project_path"]):
										os.remove(fn)
										# if fn in WRITTEN_FILES_LIST:
											# WRITTEN_FILES_LIST.remove(WRITTEN_FILES_LIST.index(fn))
									else:
										actionWarning("attempted to delete (move) a file outside of the project directory", d)
						else:
							d["%a"] = None
					else:
						actionWarning("attempted to copy/move to/from a file/directory outside of the project directory or tried to write a file in the source directory", d)
			else:
				if "file" in ak:
					fname = action["file"]
				elif "filevar" in ak:
					fname = d[action["filevar"]]
				else:
					fname = d["%a"]

				fname = readf(fname, d)
				if not os.path.isabs(fname):
					fname = os.path.join(d["curdir"], fname)
				if fname.startswith(d["project_path"]) or fname.startswith(d["source_path"]):
					if os.path.exists(fname):
						with open(fname) as f:
							d["%a"] = f.read()
					else:
						d["%a"] = None
				else:
					actionAccessWarning(fname, d)

		elif a == "write":
			if "dest" in ak or "file" in ak:
				if "data" in ak:
					d["%a"] = action["data"]
				elif "var" in ak:
					if action["var"] in d.keys():
						d["%a"] = d[action["var"]]
					else:
						d["%a"] = None
				if "dest" in ak:
					fname = action["dest"]
				if "file" in ak:
					fname = action["file"]
				fname = readf(fname, d)
				if fname.startswith(d["project_path"]):
					with open(fname, 'w') as f:
						if type(d["%a"]) is dict:
							json.dump(d["%a"], f)
						elif d["%a"] is not None:
							f.write(str(d["%a"]))
						# WRITTEN_FILES_LIST.append(fname)
				else:
					actionWarning("attempted to write to a file outside of the project directory", d)

		elif a in ("makedir", "make_dir"):
			if type(action["value"]) is list:
				for value in action["value"]:
					dname = readf(value, d)
					if not os.path.isabs(dname):
						dname = os.path.join(d["build_path"], dname)
					if dname.startswith(d["project_path"]):
						make_dir(dname)
					else:
						actionWarning("attempted to create a directory outside of the project directory", d)
			else:
				dname = readf(action["value"], d)
				if not os.path.isabs(dname):
					dname = os.path.join(d["build_path"], dname)
				if dname.startswith(d["project_path"]):
					make_dir(dname)
				else:
					actionWarning("attempted to create a directory outside of the project directory", d)
		
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
		
		elif a == "exit":
			if "string" in ak:
				print(readf(action["string"], d))
			if "code" in ak:
				exit(action["code"])
			else:
				exit(1)

		elif a == "return":
			if "value" in ak:
				d["%a"] = readf(action["value"], d)
			break

		elif a in ("makeimage", "maketexture"):
			if "sources" in ak:
				fail = False
				srcimg = None
				if type(action["sources"]) is list:
					for fn in action["sources"]:
						if type(fn) is not dict:
							actionWarning(f"Warning: makeimage action key \"sources\" must be an array of objects.")
							fail = True
							break
						if "file" in fn.keys():
							img = try_load_image(readf(fn["file"], d), d)
							if img is None:
								continue
							if "operation" in fn.keys():
								try:
									img = ImageOperation(d, img, fn["operation"])
								except Exception as e:
									print(f"Warning: Image operation failed.\nOriginal error: {e}")
									continue
							elif "operations" in fn.keys():
								for op in fn["operations"]:
									try:
										img = ImageOperation(d, img, op)
									except Exception as e:
										print(f"Warning: Image operation failed.\nOriginal error: {e}")
										continue
							if srcimg is None:
								srcimg = img
							else:
								srcimg.alpha_composite(img)
				else:
					fail = True
				if fail:
					actionWarning(f"Warning: makeimage action key \"sources\" must be an array of objects.")
			elif "source" in ak:
				fname = readf(action["source"], d)
				if not os.path.isabs(fname):
					fname = os.path.join(d["curdir"], fname)
				srcimg = try_load_image(readf(fname, d), d)
				if srcimg is None:
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
				for op in action["operations"]:
					try:
						srcimg = ImageOperation(d, srcimg, op)
					except Exception as e:
						print(f"Warning: Image operation failed.\nOriginal error: {e}")
						continue
			if "color" in ak:
				if type(action["color"]) is str:
					color = tuple(int(c) for c in readf(action["color"], d).strip("()").split(","))
				elif type(action["color"]) is list:
					color = tuple(action["color"])
				elif type(action["color"]) is int:
					color = tuple([action["color"]]*3+[255])
				else:
					print(f"Warning: Wrong data type for color. Must be list, string, or integer.")
					continue
				srcimg = ImageChops.multiply(Image.new("RGBA", srcimg.size, color), srcimg)

			if "dest" in ak:
				fname = readf(action["dest"], d)
				if not os.path.isabs(fname):
					fname = os.path.join(d["curdir"], fname)
				if not fname.startswith(d["project_path"]):
					if os.path.isabs(fname):
						print(f"Warning: Failed to save image to \"{fname}\" because the path is outside the project directory")
						continue
					fname = os.path.join(d["project_path"], fname)
				if srcimg is None:
					print(f"Warning: Failed to create image for file \"{fname}\"")
					continue
				try:
					srcimg.save(fname)
				except Exception as e:
					print(f"Warning: Failed to save image \"{fname}\".\nOriginal error: {e}")
					continue
			else:
				d["%a"] = srcimg




