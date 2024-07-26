
import os, json
from PIL import Image, ImageChops, ImageFilter
from PIL.Image import Transpose

WRITTEN_FILES_LIST = []

def ImageOperation(d, img, op):
	try:
		if type(op) is list:
			o = op[0]
			if o == "alpha_composite":
				img.alpha_composite(Image.open(os.path.join(d["project_path"], op[1])))
				return img
			elif o == "rotate":
				return img.rotate(int(op[1]))
			elif o == "blend":
				return img.blend(Image.open(os.path.join(d["project_path"], op[1])), float(op[2]))
			elif o == "composite":
				return img.composite(Image.open(os.path.join(d["project_path"], op[1])), Image.open(os.path.join(d["project_path"], op[2])))
			elif o == "crop":
				return img.crop(tuple(op[1]))
			elif o == "effect_spread":
				return img.effect_spread(float(op[1]))
			elif o == "filter":
				filters = ["BLUR","CONTOUR","DETAIL","EDGE_ENHANCE","EDGE_ENHANCE_MORE","EMBOSS","FIND_EDGES","SHARPEN","SMOOTH","SMOOTH_MORE"]
				if op[1].upper() in filters:
					return img.filter(getattr(ImageFilter, op[1])())
				print(f"Warning: undefined filter type \"{op[1]}\", ignoring.\nValid filters: {', '.join(filters)}\n")
				return img
			elif o == "transpose":
				filters = ["FLIP_LEFT_RIGHT", "FLIP_TOP_BOTTOM", "ROTATE_90", "ROTATE_180", "ROTATE_270", "TRANSPOSE", "TRANSVERSE"]
				if op[1].upper() in filters:
					return img.transpose(getattr(Transpose, op[1]))
				print(f"Warning: undefined filter type \"{op[1]}\", ignoring.\nValid filters: {', '.join(filters)}\n")
				return img
			elif o == "paste":
				if len(op) == 2:
					img.paste(Image.open(os.path.join(d["project_path"], op[1])))
				elif len(op) == 3:
					img.paste(Image.open(os.path.join(d["project_path"], op[1])), tuple(op[2]))
				elif len(op) >= 4:
					img.paste(Image.open(os.path.join(d["project_path"], op[1])), tuple(op[2]), Image.open(os.path.join(d["project_path"], op[3])))
				return img
			elif o == "multiply":
				if len(op) == 2:
					color = op[1]
					if len(color) < 4:
						color += [255] * (4 - len(color))
					return ImageChops.multiply(img.convert("RGBA"), Image.new("RGBA", img.size, tuple(color)))
				else:
					print(f"Warning: wrong number of arguments (expected 1, got {len(op)-1}) for image operation \"multiply\"")
					return
			print(f"Warning: undefined image operation: {o}, ignoring.")
			return img
		else:
			print(f"Warning: Image operations should be a list starting with the operation and following with arguments.")
			return img
	except Exception as e:
		print(f"Warning: failed to apply image operation {op}\nOriginal error: {str(e)}")
	return img


def try_load_resource(path, file, method=json.load, default=None):
	try:
		return load_resource(path, file, method)
	except:
		return default

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

def joinDicts(a, b):
	c = a.copy()
	for k in b.keys():
		c[k] = b[k]
	return c

def getDictKeyLen(d, key):
	if key.lower() in d.keys():
		if type(d[key.lower()]) is str:
			return len(d[key.lower()])
	return 0

def checkValueTrue(s):
	if type(s) is str:
		if s.lower() in ["true", "yes", "1"]:
			return True
		elif s.lower() in ["false", "no", "0"]:
			return False
	elif type(s) is list or type(s) is tuple:
		return len(s) > 0
	elif type(s) is dict:
		return len(s.keys()) > 0
	return s

def checkDictKeyTrue(d, key):
	key = key.lower()
	if key in d.keys():
		return checkValueTrue(d[key])
	return False

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
			val2 = None
			if len(condition) >= 2:
				val2 = readf(condition[1], d)
			# print(val, condition)
			if condition[0] == "#contains":
				if type(val) is str and val2 in val:
					return not inverted
			elif condition[0] == "#containskey":
				if type(val) is dict and val2 in val.keys():
					return not inverted
			elif condition[0] == "#typeis":
				if val2 == "int" and type(val) is int:
					return not inverted
				elif val2 == "float" and type(val) is float:
					return not inverted
				elif val2 == "str" and type(val) is str:
					return not inverted
				elif val2 == "list" and type(val) is list:
					return not inverted
				elif val2 == "tuple" and type(val) is tuple:
					return not inverted
				elif val2 == "dict" and type(val) is dict:
					return not inverted
				elif val2 == "number" and (type(val) is int or type(val) is float):
					return not inverted
				elif val2 == "iterable" and (type(val) is list or type(val) is tuple):
					return not inverted
				elif val2 == "none" and val is None:
					return not inverted
			elif condition[0] == "#startswith":
				if type(val) is str and val.startswith(val2):
					return not inverted
			elif condition[0] == "#equals":
				if val == val2:
					return not inverted
			elif condition[0] == "#endswith":
				if type(val) is str and val.endswith(val2):
					return not inverted
			elif condition[0] == "#length":
				if type(val) is str or type(val) is list or type(val) is tuple:
					if val2 == "nonzero" and len(val) > 0:
						return not inverted
					elif val2 == "zero" and len(val) <= 0:
						return not inverted
			elif condition[0] == ">":
				if toNumber(val, default=0) > toNumber(val2, default=0):
					return not inverted
			elif condition[0] == "<":
				if toNumber(val, default=0) < toNumber(val2, default=0):
					return not inverted
			elif condition[0] == ">=":
				if toNumber(val, default=0) >= toNumber(val2, default=0):
					return not inverted
			elif condition[0] == "<=":
				if toNumber(val, default=0) <= toNumber(val2, default=0):
					return not inverted
			elif condition[0] == "==":
				if toNumber(val, default=0) == toNumber(val2, default=0):
					return not inverted
			elif condition[0] == "!=":
				if toNumber(val, default=0) != toNumber(val2, default=0):
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
		elif type(c) is int or type(c) is float:
			return c > 0
	return False

def checkTrue(condition, d):
	condition = readf(condition, d)
	if condition.startswith("?"):
		return checkConditionString(condition[1:], d)
	elif condition.startswith("!"):
		if condition[1:].startswith("keyexists ") or condition[1:].startswith("exists "):
			return condition.split(" ", maxsplit=1)[1] not in d.keys()
		else:
			return not checkDictKeyTrue(d, condition[1:])
	else:
		if condition.startswith("keyexists ") or condition.startswith("exists "):
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
			elif conditions[0] == "^XOR":
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

def readDictFile(fname, d=None, md=None):
	if d is None:
		d = {}
	try:
		# print("Reading Dictionary File: \""+fname+"\"")
		with open(fname) as f:
			if md is not None:
				tmp = md["curdir"]
				md["curdir"] = os.path.dirname(fname)
			rv = readDictString(f.read(), d, fname, md)
			if md is not None:
				md["curdir"] = tmp
			return rv
	except FileNotFoundError:
		return None

def readDictString(data, d=None, f=None, md=None):
	# strip leading and trailing whitespace
	data = data.strip(" \t\n")
	# try to load as json if it looks like json
	if data.startswith("{") or data.startswith("["):
		try:
			return json.loads(data)
		except:
			pass

	if md is not None:
		isthisapplicable = True
		hasversionselector = False
		for line in data.splitlines():
			if line.startswith("@gameversion ") or line.startswith("@version "):
				hasversionselector = True
				gameversion = md["gameversion"].split(".")
				checkverstr = line.split(" ", maxsplit=1)[1]
				checkver = checkverstr.lstrip("<>= \t").split(".")
				deltaver = [int(checkver[i])-int(gameversion[i]) for i in range(min(len(gameversion), len(checkver)))]
				# print(gameversion, checkverstr, checkver, deltaver)
				if len(deltaver) < 3:
					deltaver += [0] * (3 - len(deltaver))
				if checkverstr.startswith(">="):
					isver = False
					if deltaver[0] > 0:
						isver = True
					elif deltaver[0] == 0:
						if deltaver[1] > 0:
							isver = True
						elif deltaver[1] == 0:
							if deltaver[2] >= 0:
								isver = True
				elif checkverstr.startswith(">"):
					isver = False
					if deltaver[0] > 0:
						isver = True
					elif deltaver[0] == 0:
						if deltaver[1] > 0:
							isver = True
						elif deltaver[1] == 0:
							if deltaver[2] > 0:
								isver = True
				elif checkverstr.startswith("<="):
					isver = False
					if deltaver[0] < 0:
						isver = True
					elif deltaver[0] == 0:
						if deltaver[1] < 0:
							isver = True
						elif deltaver[1] == 0:
							if deltaver[2] <= 0:
								isver = True
				elif checkverstr.startswith("<"):
					isver = False
					if deltaver[0] < 0:
						isver = True
					elif deltaver[0] == 0:
						if deltaver[1] < 0:
							isver = True
						elif deltaver[1] == 0:
							if deltaver[2] < 0:
								isver = True
				else:
					isver = all([v==0 for v in deltaver])
				if isver:
					isthisapplicable = False
			if line.startswith("@modloader ") or line.startswith("@loader "):
				hasversionselector = True
				if md["modloader"] != line.split(" ", maxsplit=1)[1].lower():
					isthisapplicable = False

		if hasversionselector and not isthisapplicable:
			return None

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

	should_process_lines = True
	should_process_lines_stack = []
	
	lines = data.splitlines()
	for lineno in range(len(lines)):
		line = lines[lineno]
		if not line.startswith("#"):
			if line.startswith("@endif"):
				if len(should_process_lines_stack):
					should_process_lines = should_process_lines_stack.pop(0)
				elif f is not None:
					print(f"Warning: \"@endif\" used without matching if statement on line {lineno} of file {f}")
				else:
					print(f"Warning: \"@endif\" used without matching if statement")
			elif line.startswith("@else"):
				should_process_lines = not should_process_lines
			if not should_process_lines:
				continue
			if line.startswith("@include "):
				# print("Including file " + line[9:])
				if readDictFile(line[9:], d, md) is None:
					print("Failed to read dictionary file:", line[9:])
					lineno += 1
			elif line.startswith("@iterate "):
				if line[9:] in d.keys():
					iteratorvalues = d[line[9:]]
				elif md is not None and line[9:] in md.keys():
					iteratorvalues = md[line[9:]]
				else:
					print("Warning: iterator key", line[9:], "is not defined.")
			elif line.startswith("@if "):
				should_process_lines_stack.append(should_process_lines)
				if line[4] == '{' or line[4] == '[':
					should_process_lines = checkActionConditions(json.loads(line[4:]), joinDicts(md, d))
				else:
					should_process_lines = checkConditionString(line[4:], joinDicts(md, d))
			elif ":" in line:
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
							n = len(d[k])
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

	if iteratorvalues is not None:
		values = []
		if md is None:
			md = d
		for value in iteratorvalues:
			md["%v"] = value
			values.append(readf(d, md))
		return {"@iterate": values}
	# print('--------------------------------\n', d)
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
	indices = {}
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
							if ns+'.'+k[2:] not in indices.keys():
								indices[ns+'.'+k[2:]] = 0
							o.append(f"{k}: {d[ns+'.'+k[2:]][indices[ns+'.'+k[2:]]]}")
							indices[ns+'.'+k[2:]] += 1
					elif line.startswith("+"):
						if k[1:] in d.keys():
							if k[1:] not in indices.keys():
								indices[k[1:]] = 0
							o.append(f"{k}: {d[k[1:]][indices[k[1:]]]}")
							indices[k[1:]] += 1
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

def _getDictString(d, key):
	if type(d[key]) is list:
		for item in d[key]:
			yield f"+{key}: {item}"
	elif type(d[key]) is dict:
		if not (key.endswith(".") and key in d[key].keys()):
			yield f"{key}:"
		for s in sorted(d[key].keys()):
			for val in _getDictString(d[key], s):
				if val.startswith("+"):
					yield f"+{key}.{val[1:]}"
				else:
					yield f"{key}.{val}"
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
	if content_type.lower() in ("toolmaterial", "armormaterial"):
		cidlow = cid
	manifest_dict[f"mod.registry.{content_type}.names"].append(cidlow)
	manifest_dict[f"mod.{content_type}.{cidlow}.keys"] = list(d.keys())
	for key in d.keys():
		# print(f"mod.{content_type}.{cid}.{key} = {d[key]}")
		v = d[key]
		if type(v) is str:
			v = readf(v, manifest_dict)
		manifest_dict[f"mod.{content_type}.{cidlow}.{key}"] = v
	# print(cid, cidlow)
	manifest_dict[f"mod.{content_type}.{cidlow}.uppercased"] = cid.upper()
	manifest_dict[f"mod.{content_type}.{cidlow}"] = manifest_dict[f"mod.{content_type}.{cidlow}.mcpath"] = cidlow
	if content_type.lower() in ("toolmaterial", "armormaterial"):
		manifest_dict[f"mod.{content_type}.{cidlow}.class"] = cid
	elif "class" not in d.keys():
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
		if "title" not in d.keys() or getDictKeyLen(d, "title") < 1:
			manifest_dict[f"mod.{content_type}.{cidlow}.title"] = " ".join([word.capitalize() for word in cidlow.split("_")])
		if "texture" not in d.keys() or getDictKeyLen(d, "texture") < 1:
			if f"mod.{content_type}.{cidlow}.texture_top" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = manifest_dict[f"mod.{content_type}.{cidlow}.texture_top"]
			elif f"mod.{content_type}.{cidlow}.texture_side" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = manifest_dict[f"mod.{content_type}.{cidlow}.texture_side"]
			elif f"mod.{content_type}.{cidlow}.texture_bottom" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = manifest_dict[f"mod.{content_type}.{cidlow}.texture_bottom"]
			elif f"mod.{content_type}.{cidlow}.texture_front" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = manifest_dict[f"mod.{content_type}.{cidlow}.texture_front"]
			else:
				manifest_dict[f"mod.{content_type}.{cidlow}.texture"] = cidlow

	return True

def VerifyMCName(name):
	return all([c in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in name])

def MCNameify(name):
	name = "".join([" "+c if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" else c for c in name])
	return name.strip(" ").replace(" ", "_").lower()

def Classify(name):
	return "".join([s.capitalize() for s in name.replace(" ", "_").split("_")])

def Titleify(name):
	return name.strip(" ").replace("_", " ").title()

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
		if d["version_past_1.19.3"]:
			return f"{mod}:{ct}/{os.path.basename(tex)}"
		else:
			return f"{mod}:{ct}s/{os.path.basename(tex)}"
	return tex

def splitPrefix(s, n=0, p=None):
	l = prefixLen(s, p)
	yield s[:l]
	n -= 1
	if n > 1:
		for v in splitPrefix(s[l:], n, p):
			yield v
	else:
		yield s[l:]

def prefixLen(s, p=None):
	if p == None:
		p = "".join([chr(c+0x41)+chr(c+0x61) for c in range(26)])
	for i in range(len(s)):
		if s[i] not in p:
			return i
	return len(s)

def toNumber(val, default=None):
	if type(val) is int or type(val) is float:
		return val
	elif type(val) is str:
		try:
			return int(val)
		except:
			pass
		try:
			return float(val)
		except:
			pass
	return default

def make_dirs(path):
	p = path.replace("\\", "/").split("/")
	for i in range(len(p)):
		if not os.path.exists("/".join(p[:i])):
			if not make_dir(path):
				return False
	return True

def make_dir(path):
	if os.path.exists(path) and os.path.isdir(path):
		return True
	elif os.path.exists(path):
		print(f"Warning: Failed to make directory \"{path}\" because a file of the same name exists")
		return False
	try:
		os.mkdir(path)
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
	NUM_ITERATOR_NUMBERS = 9

	# if type(data) is list:
		# return [readf(i, d) for i in data]
	# if type(data) is dict:
		# return {k:readf(data[k], d) for k in data.keys()}
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
				key = data[i+len(itr):n]
				l = None
				if key in d.keys():
					l = d[key]
				elif key.lower() in d.keys():
					l = d[key.lower()]
				if l != None:
					j = data.find(itrend, n)
					block = data[n:j]
					j += len(itrend)
					if type(l) is list:
						for i in range(len(l)):
							data2.append(block.replace("$%v", l[i]).replace("$%i", str(i)))
				else:
					j = data.find(itrend, n)+len(itrend)
					if data[j] == '\n':
						j += 1
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
				key = data[i+len(lstr):n]
				l = None
				if key in d.keys():
					l = d[key]
				elif key.lower() in d.keys():
					l = d[key.lower()]
				if l != None:
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
					if data[j] == '\n':
						j += 1
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
				if i > 0 and data[i-1] == '\n':
					data2.append(data[j:i-1])
				else:
					data2.append(data[j:i])
				n = data.find("\n", i+len(istr))
				# print(f"Checking if {key} is defined. ",end="")
				condtrue = checkTrue(data[i+len(istr):n], d)
				j = data.find(istrend, n)
				if condtrue:
					data2.append(data[n:j])
					# print(data2[-1])
				j += len(istrend)
				if data[j] == '\n':
					j += 1
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
				w = word.split("^", maxsplit=1)[0]
				fns = word.split("^")[1:]
				if w in d.keys():
					w = d[w]
				elif w.lower() in d.keys():
					w = d[w.lower()]
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
						elif fn.lower() == "title":
							w = w.title()
						elif fn.lower() == "class":
							w = "".join([s.capitalize() for s in w.replace("_", " ").split(" ")])
						elif fn.lower() == "bool":
							w = "true" if checkValueTrue(w) else "false"
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
						elif fn.lower().startswith("split(") and fn.endswith(")"):
							if type(w) is not str:
								w = str(w)
							try:
								args = [int(a) for a in fn.lower()[10:-1].split(",")]
							except:
								print("Error parsing integer argument in key function arguments ${"+word+"}")
								exit(1)
							if len(args) < 1 or len(args) > 2:
								print("Wrong number of arguments to key function ^split in ${"+word+"} (minimum 1, maximum 2 arguments)")
								exit(1)
							w = w.split(fn[6:9].strip("'\""), args[0])
							if len(args) == 2:
								if args[1] < len(w):
									w = w[args[1]]
								else:
									w = None
						elif fn.lower().startswith("substring(") and fn.endswith(")"):
							if type(w) is not str:
								w = str(w)
							try:
								args = [int(a) for a in fn.lower()[10:-1].split(",")]
							except:
								print("Error parsing integer argument in key function arguments ${"+word+"}")
								exit(1)
							if len(args) == 1:
								w = w[args[0]:]
							elif len(args) == 2:
								w = w[args[0]:args[1]]
							elif len(args) == 3:
								w = w[args[0]:args[1]:args[2]]
							else:
								print("Wrong number of arguments to key function ^substring in ${"+word+"} (minimum 1, maximum 3 arguments)")
								exit(1)
						elif fn.lower().startswith("replace(") and fn.endswith(")"):
							if type(w) is not str:
								w = str(w)
							args = fn.lower()[8:-1].split(",")
							if len(args) == 1:
								w = w.replace(args[0], "")
							elif len(args) == 2:
								w = w.replace(args[0], args[1])
							else:
								print("Wrong number of arguments to key function ^replace in ${"+word+"} (minimum 1, maximum 2 arguments)")
								exit(1)
			elif word in d.keys():
				w = d[word]
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
