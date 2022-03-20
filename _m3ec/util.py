
import os

def walk(path):
	found_names = []
	for fname in _walk(path):
		fname = os.path.abspath(fname)
		if fname not in found_names:
			found_names.append(fname)
			yield fname

def _walk(path):
	for root,dirs,files in os.walk(path):
		for dname in dirs:
			for fname in walk(os.path.join(root, dname)):
				yield fname
		for fname in files:
			yield os.path.join(root, fname)

def getDictVal(d, k, fname):
	try:
		return d[k]
	except KeyError:
		print(f"Missing \"{k}\" in file \"{fname}\"!")

def readDictFile(fname, d=None):
	if d is None:
		d = {}
	try:
		# print("Reading Dictionary File: ", fname)
		with open(fname) as f:
			return readDictString(f.read(), d)
	except FileNotFoundError:
		return None

def readDictString(data, d=None):
	if d is None:
		d = {}
	ns = ""
	lineno = 1
	d["#comments"] = {}
	for line in data.splitlines():
		if len(line) and not line.startswith("#"):
			if ":" in line:
				name, value = line.split(":",maxsplit=1)
				v = value.lstrip(" \t")
				if line.startswith("+.") or line.startswith(".+"):
					if len(name)>2:
						k = f"{ns}.{name[2:]}"
						if k not in d.keys():
							d[f"{k}^list.0"] = v
							d[k] = [v]
						elif type(d[k]) is list:
							n = len(d[k])
							d[f"{k}^list.{n}"] = v
							d[k].append(v)
						else:
							d[f"{k}^list.{n}"] = v
							d[k] += v
					else:
						d[ns].append(v)
				elif line.startswith("+"):
					k = name[1:]
					if k not in d.keys():
						d[f"{k}^list.0"] = v
						d[k] = [v]
					elif type(d[k]) is list:
						n = len(d[k])
						d[f"{k}^list.{n}"] = v
						d[k].append(v)
					else:
						n = len(d[k])
						d[f"{k}^list.{n}"] = v
						d[k] += v
				elif line.startswith("."):
					d[ns+name] = v
				else:
					ns = name
					d[name] = v
		else:
			d["#comments"][lineno] = line
		lineno += 1
	return d


def getDictVal(d, k, fname):
	try:
		return d[k]
	except KeyError:
		print(f"Missing \"{k}\" in file \"{fname}\"!")

def writeDictFile(fname, d):
	try:
		# print("Writing Dictionary File: ", fname)
		with open(fname, "w") as f:
			f.write(getDictString(d))
	except OSError:
		return False
	return True

def getDictString(d):
	o = []
	if "#comments" in d.keys():
		comments = d["#comments"]
	else:
		comments = {}
	if "__Generated" not in d.keys():
		o.append("__Generated: by M3ECWizard")

	d2 = {}
	for key in d.keys():
		if "^list." not in key and "^keys" not in key:
			if "." in key:
				keys = key.split(".")
				for i in range(len(keys)-1):
					keys[i] = keys[i]+"."
				a = d2
				for k in keys[:-1]:
					if k not in a.keys():
						a[k] = {}
					a = a[k]
				a[keys[-1]] = d[key]
			else:
				d2[key] = d[key]

	line = 1
	for key in sorted(d2.keys()):
		for val in _getDictStrings(d2, key):
			if line in comments.keys():
				o.append(comments[line])
				del comments[line]
			elif key != "#comments":
				# print(val)
				o.append(val)
			line += 1
	return "\n".join(o)

def _getDictStrings(d, key, nest=None):
	if type(key) is str:
		k = key.rstrip(".")
	else:
		k = key
	if type(d[key]) is list:
		for item in d[key]:
			yield f"+{k}: {item}"
	elif type(d[key]) is dict:
		if not (key.endswith(".") and k in d.keys()):
			if nest is None:
				yield f"{k}:"
			else:
				yield f"{nest}.{k}:"
		for s in sorted(d[key].keys()):
			for val in _getDictStrings(d[key], s, nest=k):
				if nest is None:
					yield "."+val
				else:
					yield val
	else:
		yield f"{k}: {d[key]}"

def add_content(cid, content_type, d, manifest_dict, fname=None):
	# print(f"registering {content_type} {cid}.")
	if cid in manifest_dict[f"mod.registry.{content_type}.names"]:
		original = cid
		n = 2
		while cid in manifest_dict[f"mod.registry.{content_type}.names"]:
			cid = f"{original}_{n}"
			n += 1
			
	manifest_dict[f"mod.registry.{content_type}.names"].append(cid)
	manifest_dict[f"mod.{content_type}.{cid}.keys"] = list(d.keys())
	for key in d.keys():
		# print(f"mod.{content_type}.{cid}.{key} = {d[key]}")
		manifest_dict[f"mod.{content_type}.{cid}.{key}"] = d[key]
	manifest_dict[f"mod.{content_type}.{cid}.uppercased"] = cid.upper()
	manifest_dict[f"mod.{content_type}.{cid}"] = manifest_dict[f"mod.{content_type}.{cid}.mcpath"] = cid.lower()
	manifest_dict[f"mod.{content_type}.{cid}.class"] = "".join([word.capitalize() for word in cid.split("_")])
	manifest_dict[f"mod.files"][f"{content_type}.{cid}"] = fname
	if content_type == "item" and "mod.iconItem" not in manifest_dict.keys():
		manifest_dict["mod.iconItem"] = cid
	if content_type == "recipe":
		manifest_dict[f"mod.{content_type}.{cid}.texture"] = d["result"]
	else:
		if f"mod.{content_type}.{cid}.texture" not in manifest_dict.keys():
			if f"mod.{content_type}.{cid}.texture_top" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cid}.texture"] = manifest_dict[f"mod.{content_type}.{cid}.texture_top"]
			elif f"mod.{content_type}.{cid}.texture_side" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cid}.texture"] = manifest_dict[f"mod.{content_type}.{cid}.texture_side"]
			elif f"mod.{content_type}.{cid}.texture_bottom" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cid}.texture"] = manifest_dict[f"mod.{content_type}.{cid}.texture_bottom"]
			elif f"mod.{content_type}.{cid}.texture_front" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cid}.texture"] = manifest_dict[f"mod.{content_type}.{cid}.texture_front"]
			else:
				manifest_dict[f"mod.{content_type}.{cid}.texture"] = None

	return True

def VerifyMCName(name):
	return all([c in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in name])

def ParseContentTitle(title):
	if title.isupper():
		return title.replace("_"," ").capitalize(), title.lower(), title
	if " " not in title and title.islower():
		return title.replace("_", " ").capitalize(), title, title.upper()
	return title, title.replace(" ", "_").lower(), title.replace(" ", "_").upper()

def texture_pathify(d, tex, ct, cid):
	tex, ext = os.path.splitext(tex)
	if ":" not in tex:
		if ct in ["tool", "armor", "blockitem", "food", "fuel"]:
			ct = "item"
		mod = d["mod.mcpath"]
		return f"{mod}:{ct}s/{os.path.basename(tex)}"
	return tex

def checkDictKeyTrue(d, key):
	if key in d.keys():
		if type(d[key]) is str:
			if d[key].lower() in ["true", "yes", "1"]:
				return True
		else:
			return d[key]
	return False

def make_dir(path):
	try:
		os.mkdir(path)
	except FileExistsError:
		pass


def copy_file(src, dest):
	try:
		with open(src, "rb") as f:
			with open(dest, "wb") as f2:
				f2.write(f.read())
	except FileNotFoundError:
		print(f"Failed to copy file \"{src}\" into \"{dest}\"")
		exit(1)


def readf_copyfile(source, dest, d):
	data = readf_file(source, d)
	if data is None:
		return False
	create_file(dest, data)
	return True


def create_file(fname, data):
	if data is None:
		print(f"Warning: Skipping creation of empty file \"{fname}\"")
	else:
		try:
			with open(fname, "w") as f:
				f.write(data)
		except FileNotFoundError:
			print(f"Warning: Failed to create file \"{fname}\"")


def readf_file(path, d):
	# print(f"Calling readf on {path}")
	try:
		with open(path) as f:
			rv = readf(f.read(), d)
			if rv is None:
				print(f"Key Error in file: \"{path}\"")
				quit()
			return rv
	except FileNotFoundError:
		print(f"file \"{path}\" not found")
		return None

def readf(data, d):
	if "$%f" in d.keys():
		data = data.replace("$%f", d["$%f"])

	if "---iter " in data:
		data2 = []
		j = 0
		while "---iter " in data[j:]:
			i = data.find("---iter ", j)
			data2.append(data[j:i])
			n = data.find("\n", i+8)
			key = data[i+8:n]
			if key in d.keys():
				l = d[key]
				j = data.find("---end",n)
				block = data[n:j]
				j += 6
				if type(l) is list:
					for i in range(len(l)):
						data2.append(block.replace("$%v", l[i]).replace("$%i", str(i)))
			else:
				print(f"Critical error! {key} not found in dictionary passed to readf!")
				exit(1)
		data2.append(data[j:])
		data = "".join(data2)

	if "---list " in data:
		data2 = []
		j = 0
		while "---list " in data[j:]:
			i = data.find("---list ", j)
			data2.append(data[j:i])
			n = data.find("\n", i+8)
			key = data[i+8:n]
			if key in d.keys():
				l = d[key]
				j = data.find("---end",n)
				block = data[n:j]
				j += 6
				lst = []
				if type(l) is list:
					for i in range(len(l)):
						lst.append(block.replace("$%v", l[i]).replace("$%i", str(i)))
					data2.append(",".join(lst))
			else:
				print(f"Critical error! {key} not found in dictionary passed to readf!")
				return None
		data2.append(data[j:])
		data = "".join(data2)

	if "---if " in data:
		data2 = []
		j = 0
		while "---if " in data[j:]:
			i = data.find("---if ", j)
			data2.append(data[j:i])
			n = data.find("\n", i+6)
			if data[i+6] == '!':
				inverted = True
				key = data[i+7:n]
			else:
				inverted = False
				key = data[i+6:n]
			if " " in key:
				key, tail = key.split(" ", maxsplit=1)
			else:
				tail = []
			condtrue = False
			if "#contains" in tail:
				if len(tail):
					if all([w in key for w in tail[1:]]):
						condtrue = True
						for w in tail[1:]:
							key = key.replace(w, "")
				elif len(key):
					condtrue = True
			elif key in d.keys():
				condtrue = True
			if inverted:
				condtrue = not condtrue
			# print(f"Checking if {key} is defined. ",end="")
			j = data.find("---fi",n)
			if condtrue:
				# print("key found.")
				data2.append(data[n:j])
				# print(data2[-1])
			j += 5
		data2.append(data[j:])
		data = "".join(data2)

	# just use some arbitrary number of iterations until I figure out a better algorithm
	for j in range(8):
		i = data.find("${")
		while i != -1:
			head, word = data[:i], data[i+2:]
			rb = word.find("}")
			if rb == -1:
				# print(data)
				print("Critical Error: Mismatched open bracket in data passed to readf!")
				return None
			word, tail = word[:rb], word[rb+1:]
			w = "${"+word+"}"
			if "^" in word:
				w = word.split("^", maxsplit=1)[0]
				fns = word.split("^")[1:]
				if w in d.keys():
					w = d[w]
					if type(w) is str:
						for fn in fns:
							if fn.lower() == "upper":
								w = w.upper()
							elif fn.lower() == "lower":
								w = w.lower()
							elif fn.lower() == "capital":
								w = w.capitalize()
			elif word in d.keys():
				w = d[word]
			# if "mc." in word:
				# print(word, w)
			data = head + str(w) + tail
			i = data.find("${", i+2)

	# while any([any(["${"+key+M+"}" in data for M in ["","^CAPITAL","^UPPER","^LOWER"]]) for key in d.keys()]):
		# for key in d.keys():
			# data = data.replace("${"+key+"^CAPITAL}", str(d[key]).capitalize()).replace("${"+key+"^UPPER}", str(d[key]).upper()).replace("${"+key+"^LOWER}", str(d[key]).lower()).replace("${"+key+"}", str(d[key]))
	# data2 = []
	# i = 0
	# for match in r.finditer(data):
		# data2.append(data[i:match.start()])
		# i = match.end()
	# data2.append(data[i:])
	# return "".join(data2)
	# if "forge" in d["modloader"]:
		# for word in ["PICKAXES", "SHOVELS", "SWORDS", "HOES", "AXES"]:
			# data = data.replace(word, word[:-1])

	# if len(data) < 50:
		# print(data)
	
	
	return data
