
import os, shutil, json, re
from .util import *

def UpdateJsons(path, fileregex, key=None, value=None, append=True):
	if type(key) is list or type(key) is tuple:
		if len(key) < 1:
			print(f"Key path must not be empty if it is a list/tuple.")
			exit(1)
	freg = re.compile(fileregex)
	for fname in walk(path):
		if freg.match(fname):
			print(fname)
			with open(fname) as f:
				data = json.load(f)
			if key is not None:
				if type(key) is list or type(key) is tuple:
					if len(key) > 1:
						d = data
						for k in key[:-1]:
							if k in d.keys():
								d = d[k]
							else:
								print(f"Key path {key} not found in json file {fname}.")
								exit(1)
					else:
						d = data[key[0]]
					
				else:
					if key in data.keys():
						if append and (type(data[key]) is list or type(data[key]) is tuple):
							data[key].append(value)

			with open(fname, "w") as f:
				json.dump(data, f, indent=2)


