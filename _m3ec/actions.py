
import os
from .util import *

def execActions(actions, versionbuilder, d):
	if "actionvars" in d.keys():
		d["actionvars"] = {"oldvars": d["actionvars"], "accumulator": None}
	else:
		d["actionvars"] = {"accumulator": None}
	_execActions(actions, versionbuilder, d)

def _execActions(actions, versionbuilder, d):
	for action in actions:
		a = action["action"]
		if a == "var":
			if "source" in action.keys() and "dest" in action.keys():
				d["actionvars"][action["dest"]] = d["actionvars"][action["source"]]
			elif "name" in action.keys() and "value" in action.keys():
				d["actionvars"][action["name"]] = action["value"]
		elif a == "doActions":
			cond = None
			if "while" in action.keys() and "var" in action.keys():
				cond = action["var"]
			while True:
				_execActions(action["actions"], versionbuilder, d)
				if cond is None:
					break
				if not d["actionvars"][cond]:
					break
		elif a == "repeatActions":
			rep = 1
			if "repeat" in action.keys():
				rep = int(action["repeat"])
			for i in range(rep):
				_execActions(action["actions"], versionbuilder, d)
		elif a == "makedir" or a == "make_dir":
			make_dir(os.path.join(d["build_path"], readf(action["value"], d)))
		elif a == "readf":
			if "file" in action.keys():
				d["$%f"] = action["file"]
				accumulator = readf_file(readf(action["file"], d), d)
			else:
				accumulator = readf(action["value"], d)
		elif a == "copy" or a == "move":
			if "source" in action.keys() and "dest" in action.keys():
				accumulator = readf(action["source"], d)
				if os.exists(accumulator):
					if a == "copy":
						shutil.copy(fname, readf(action["dest"], d))
					elif a == "move":
						shutil.move(fname, readf(action["dest"], d))
				else:
					accumulator = None
			elif "file" in action.keys():
				fname = readf(action["file"], d)
				if os.exists(fname):
					with open(fname) as f:
						accumulator = f.read()
				else:
					accumulator = None