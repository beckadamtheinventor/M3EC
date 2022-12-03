
import os, json

WRITTEN_FILES_LIST = []

def load_resource(path, file, method=json.load):
	with open(os.path.join(path, file)) as f:
		return method(f)

def dictDir(path, d={}):
	for root,dirs,files in os.walk(path):
		d[root] = {}
		for dname in dirs:
			dictDir(os.path.join(root, dname), d)
		for fname in files:
			d[fname] = None
		break

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

def listDir(path):
	for root,dirs,files in os.walk(path):
		for dname in dirs:
			yield os.path.join(root, dname)
		for fname in files:
			yield os.path.join(root, fname)
		break

def getDictVal(d, k, fname):
	if k in d.keys():
		return d[k]
	elif type(k) is str and k.lower() in d.keys():
		return d[k.lower()]
	else:
		print(f"Missing \"{k}\" in file \"{fname}\"!")

def readDictFile(fname, d=None, md=None):
	if d is None:
		d = {}
	try:
		# print("Reading Dictionary File: ", fname)
		with open(fname) as f:
			return readDictString(f.read(), d, fname, md)
	except FileNotFoundError:
		return None

def readDictString(data, d=None, f=None, md=None):
	if md is not None:
		isthisapplicable = True
		hasversionselector = False
		for line in data.splitlines():
			if len(line) and ":" in line and not line.startswith("#"):
				key, value = line.split(":", maxsplit=1)
				value = value.lstrip(" \t")
				key = key.lower().strip(" \t")
				if key == ("@gameversion", "@version"):
					hasversionselector = True
					if md["gameversion"] != value.lower():
						isthisapplicable = False
				elif key in ("@modloader", "@loader"):
					hasversionselector = True
					if md["modloader"] != value.lower():
						isthisapplicable = False

		if hasversionselector and not isthisapplicable:
			return False

	if d is None:
		d = {}
	ns = ""
	lineno = 1
	if f is not None:
		if "#data" not in d.keys():
			d["#data"] = {}
		d["#data"][f] = data
		# print(f, data)
	iteratorvalues = None
	if md is not None:
		if "%v" in md.keys():
			del md["%v"]
	for line in data.splitlines():
		if len(line) and not line.startswith("#"):
			if ":" in line:
				name, value = line.split(":", maxsplit=1)
				name = name.lower().strip(" \t")
				v = value.lstrip(" \t")
				if line.startswith("+.") or line.startswith(".+"):
					if len(name) > 2:
						k = f"{ns}.{name[2:]}"
						if k not in d.keys():
							d[f"{k}.list.0"] = v
							d[k] = [v]
						elif type(d[k]) is list:
							n = len(d[k])
							d[f"{k}.list.{n}"] = v
							d[k].append(v)
						else:
							d[f"{k}.list.{n}"] = v
							d[k] += v
					else:
						d[ns].append(v)
				elif line.startswith("+"):
					k = name[1:]
					if k not in d.keys():
						d[f"{k}.list.0"] = v
						d[k] = [v]
					elif type(d[k]) is list:
						n = len(d[k])
						d[f"{k}.list.{n}"] = v
						d[k].append(v)
					else:
						n = len(d[k])
						d[f"{k}.list.{n}"] = v
						d[k] += v
				elif line.startswith("."):
					d[ns+name] = v
				else:
					ns = name
					d[name] = v
			elif line.startswith("@include "):
				if readDictFile(line[9:], d) is None:
					print("Failed to read dictionary file:", line[9:])
					lineno += 1
			elif line.startswith("@iterate "):
				if line[9:] in d.keys():
					iteratorvalues = d[line[9:]]
				elif md is not None and line[9:] in md.keys():
					iteratorvalues = md[line[9:]]
				else:
					print("Warning: iterator key", line[9:], "is not defined.")
	if iteratorvalues is not None:
		values = []
		if md is None:
			md = d
		for value in iteratorvalues:
			md["%v"] = value
			values.append(readf(d, md))
		return {"@iterate": values}
	return d


def getDictVal(d, k, fname=None):
	try:
		return d[k]
	except KeyError:
		if fname is not None:
			print(f"Missing key \"{k}\" in file \"{fname}\"!")
		else:
			print(f"Missing key \"{k}\"")

def writeDictFile(fname, d):
	# print(fname)
	try:
		data = getDictString(d, fname)
		# print(data)
		# print("Writing Dictionary File: ", fname)
		with open(fname, "w") as f:
			f.write(data)
	except IOError:
		return False
	WRITTEN_FILES_LIST.append(fname)
	return True

def getDictString(d, f=None):
	o = []
	if "#data" in d.keys() and f in d["#data"].keys():
		# print(f"Updating existing dict file \"{f}\"")
		oldd = readDictString(d["#data"][f])
		ns = ""
		for line in d["#data"][f].split("\n"):
			if len(line) and not line.startswith("#"):
				if ":" in line:
					k, value = line.split(":", maxsplit=1)
					k = k.lower()
					value = value.lstrip(" \t")
					# print(k, value)
					if line.startswith("+.") or line.startswith(".+"):
						if ns in d.keys() and ns+'.'+k[2:] in d.keys():
							o.append(f"{k}: {d[ns+'.'+k[2:]].pop(0)}")
					elif line.startswith("+"):
						if k[1:] in d.keys():
							o.append(f"{k}: {d[k[1:]].pop(0)}")
					elif line.startswith("."):
						if ns in d.keys() and ns+'.'+k[1:] in d.keys():
							o.append(f"{k}: {d[ns+'.'+k[1:]]}")
					elif line.startswith("@include "):
						pass
					else:
						if k in d.keys():
							ns = k
							o.append(f"{k}: {d[k]}")
			else:
				o.append(line)
	else:
		oldd = {}

	for key in d.keys():
		if not key.startswith("#") and key not in oldd.keys():
			o.append("\n".join([s for s in _getDictString(d, key)]))

	return "\n".join(o)

def _getDictString(d, key, nest=None):
	if type(d[key]) is list:
		for item in d[key]:
			yield f"+{key}: {item}"
	elif type(d[key]) is dict:
		if not (key.endswith(".") and key in d.keys()):
			if nest is None:
				yield f"{key}:"
			else:
				yield f"{nest}.{key}:"
		for s in sorted(d[key].keys()):
			for val in _getDictString(d[key], s, nest=key):
				if nest is None:
					yield "."+val
				else:
					yield val
	else:
		yield f"{key}: {d[key]}"

def add_content(cid, content_type, d, manifest_dict, fname=None):
	# print(f"registering {content_type} {cid}.")
	if cid.lower() in manifest_dict[f"mod.registry.{content_type}.names"]:
		original = cid
		n = 2
		while cid.lower() in manifest_dict[f"mod.registry.{content_type}.names"]:
			cid = f"{original}_{n}"
			n += 1
		
	cidlow = cid.lower()
	manifest_dict[f"mod.registry.{content_type}.names"].append(cidlow)
	manifest_dict[f"mod.{content_type}.{cidlow}.keys"] = list(d.keys())
	for key in d.keys():
		# print(f"mod.{content_type}.{cid}.{key} = {d[key]}")
		v = d[key]
		if type(v) is str:
			v = readf(v, manifest_dict)
		manifest_dict[f"mod.{content_type}.{cidlow}.{key}"] = v
	# print(cid)
	manifest_dict[f"mod.{content_type}.{cidlow}.uppercased"] = cid.upper()
	manifest_dict[f"mod.{content_type}.{cidlow}"] = manifest_dict[f"mod.{content_type}.{cidlow}.mcpath"] = cidlow
	if "_" in cidlow:
		manifest_dict[f"mod.{content_type}.{cidlow}.class"] = "".join([word.capitalize() for word in cidlow.split("_")])
	else:
		manifest_dict[f"mod.{content_type}.{cidlow}.class"] = cid

	# if f"mod.{content_type}.{cidlow}.class" in manifest_dict.keys():
		# print(manifest_dict[f"mod.{content_type}.{cidlow}.class"])

	manifest_dict[f"mod.files"][f"{content_type}.{cidlow}"] = fname
	if content_type == "item" and "mod.iconitem" not in manifest_dict.keys():
		manifest_dict["mod.iconitem"] = cid
	if content_type == "recipe":
		manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = d["result"]
	else:
		if f"mod.{content_type}.{cidlow}.texture" not in manifest_dict.keys():
			if f"mod.{content_type}.{cidlow}.texture_top" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = manifest_dict[f"mod.{content_type}.{cidlow}.texture_top"]
			elif f"mod.{content_type}.{cidlow}.texture_side" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = manifest_dict[f"mod.{content_type}.{cidlow}.texture_side"]
			elif f"mod.{content_type}.{cidlow}.texture_bottom" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = manifest_dict[f"mod.{content_type}.{cidlow}.texture_bottom"]
			elif f"mod.{content_type}.{cidlow}.texture_front" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = manifest_dict[f"mod.{content_type}.{cidlow}.texture_front"]
			else:
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = None

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
	if key.lower() in d.keys():
		if type(d[key.lower()]) is str:
			if d[key].lower() in ["true", "yes", "1"]:
				return True
		else:
			return d[key]
	return False

def make_dir(path):
	try:
		os.mkdir(path)
		return True
	except FileExistsError:
		return True
	except FileNotFoundError:
		if make_dir(os.path.dirname(path)):
			os.mkdir(path)
			return True
		return False
	except:
		print(f"Warning: Failed to make directory \"{path}\"")
		return False


def copy_file(src, dest):
	try:
		with open(src, "rb") as f:
			with open(dest, "wb") as f2:
				f2.write(f.read())
		WRITTEN_FILES_LIST.append(dest)
	except FileNotFoundError:
		print(f"Failed to copy file \"{src}\" into \"{dest}\"")
		exit(1)


def readf_copyfile(source, dest, d):
	data = readf_file(source, d)
	if data is None:
		return False
	create_file(dest, data)
	WRITTEN_FILES_LIST.append(dest)
	return True


def create_file(fname, data):
	if data is None:
		print(f"Warning: Skipping creation of empty file \"{fname}\"")
	else:
		try:
			with open(fname, "w") as f:
				f.write(data)
			WRITTEN_FILES_LIST.append(fname)
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
	NUM_ITERATOR_NUMBERS = 10

	if type(data) is list:
		return [readf(i, d) for i in data]
	if type(data) is dict:
		return {k:readf(data[k], d) for k in data.keys()}
	if type(data) is not str:
		return data
	if "$%f" in d.keys():
		data = data.replace("$%f", d["$%f"])

	for itrn in range(NUM_ITERATOR_NUMBERS+1):
		if itrn < NUM_ITERATOR_NUMBERS:
			itr = f"---iter{itrn} "
			itrend = f"---{itrn}end"
		else:
			itr = "---iter "
			itrend = "---end"
		if itr in data:
			data2 = []
			j = 0
			while itr in data[j:]:
				i = data.find(itr, j)
				data2.append(data[j:i])
				n = data.find("\n", i+len(itr))
				key = data[i+len(itr):n].lower()
				if key in d.keys():
					l = d[key]
					j = data.find(itrend, n)
					block = data[n:j]
					j += len(itrend)
					if type(l) is list:
						for i in range(len(l)):
							data2.append(block.replace("$%v", l[i]).replace("$%i", str(i)))
				else:
					j = data.find(itrend, n)+len(itrend)
			data2.append(data[j:])
			data = "".join(data2)

	for lstrn in range(NUM_ITERATOR_NUMBERS+1):
		if lstrn < NUM_ITERATOR_NUMBERS:
			lstr = f"---list{lstrn} "
			lstrend = f"---{lstrn}end"
		else:
			lstr = "---list "
			lstrend = "---end"
		if lstr in data:
			data2 = []
			j = 0
			while lstr in data[j:]:
				i = data.find(lstr, j)
				data2.append(data[j:i])
				n = data.find("\n", i+len(lstr))
				key = data[i+len(lstr):n].lower()
				if key in d.keys():
					l = d[key]
					j = data.find(lstrend,n)
					block = data[n:j]
					j += len(lstrend)
					lst = []
					if type(l) is list:
						for i in range(len(l)):
							lst.append(block.replace("$%v", l[i]).replace("$%i", str(i)))
						data2.append(",".join(lst))
				else:
					j = data.find(lstrend, n) + len(lstrend)
			data2.append(data[j:])
			data = "".join(data2)

	for istrn in range(NUM_ITERATOR_NUMBERS+1):
		if istrn < NUM_ITERATOR_NUMBERS:
			istr = f"---if{istrn} "
			istrend = f"---{istrn}fi"
		else:
			istr = "---if "
			istrend = f"---fi"
		if istr in data:
			data2 = []
			j = 0
			while istr in data[j:]:
				i = data.find(istr, j)
				data2.append(data[j:i])
				n = data.find("\n", i+len(istr))
				if data[i+len(istr)] == '!':
					inverted = True
					key = data[i+len(istr)+1:n]
				else:
					inverted = False
					key = data[i+len(istr):n]
				if " " in key:
					key, tail = key.split(" ", maxsplit=1)
					tail = tail.lower().split(" ")
				else:
					tail = []
				condtrue = False
				key = readf(key.lower(), d).lower()
				# print(key, tail, "#contains" in tail, [w in key for w in tail[1:]])
				if "#contains" in tail:
					if len(tail):
						if all([w.lower() in key for w in tail[1:]]):
							condtrue = True
							for w in tail[1:]:
								key = key.replace(w.lower(), "")
					elif len(key):
						condtrue = True
				elif key in d.keys():
					condtrue = True
				if inverted:
					condtrue = not condtrue
				# print(f"Checking if {key} is defined. ",end="")
				j = data.find(istrend, n)
				if condtrue:
					# print("key found.")
					data2.append(data[n:j])
					# print(data2[-1])
				j += len(istrend)
			data2.append(data[j:])
			data = "".join(data2)


	# just use some arbitrary number of iterations until I figure out a better algorithm
	for j in range(8):
		# i = data.find("$@{")
		# while i != -1:
			# head, word = data[:i], data[i+3:]
			# rb = word.find("}{")
			# if rb == -1:
				# print("Error: Mismatched closing bracket of \"$@{}{}\" section declarator in data passed to readf!")
				# return None
			# word, tail = word[:rb], word[rb+2:]
			# bodyend = tail.find("}")
			# body, tail = tail[:bodyend], tail[bodyend+1:]
			
		i = data.find("${")
		while i != -1:
			head, word = data[:i], data[i+2:]
			rb = word.find("}")
			if rb == -1:
				# print(data)
				print("Error: Mismatched closing bracket of \"${}\" key accessor in data passed to readf!")
				return None
			word, tail = word[:rb], word[rb+1:]
			w = "${"+word+"}"
			if "^" in word:
				w = word.split("^", maxsplit=1)[0].lower()
				fns = word.split("^")[1:]
				if w in d.keys():
					w = d[w]
					if type(w) is str:
						for fn in fns:
							# if fn.startswith("("):
								# if fn.endswith(")"):
									# try:
										# w = w(args)
									# except:
										# print(f"Attempted to call non-function key: \"{w}\"")
								# else:
									# print(f"Malformed function key call: \"{fn}\"")
							if fn.lower() == "upper":
								w = w.upper()
							elif fn.lower() == "lower":
								w = w.lower()
							elif fn.lower() == "capital":
								w = w.capitalize()
							elif fn.lower() == "float":
								if type(w) is str:
									if not w.endswith("f"):
										w = w+"f"
								else:
									w = str(float(w))+"f"
							elif fn.lower() == "int":
								if type(w) is str:
									if w.endswith("f"):
										w = w[:-1]
									w = int(float(w))
								else:
									w = int(w)
			elif word.lower() in d.keys():
				w = d[word.lower()]
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
