

import os, sys, json, subprocess, tempfile, hashlib
from PIL import Image
from _m3ec.util import *


try:
	import PySimpleGUI as sg
except ImportError:
	input("Python module \"PySimpleGUI\" not installed. Please install it with \"python -m pip install PySimpleGUI --user\"\n\
Press enter to exit.")
	exit()

sg.theme("BrownBlue")
WIN_WIDTH = 500
EDITOR_BUTTON_SIZE = (18,1)
EDITOR_BUTTON_SIZE_THIN = (10,1)
EDITOR_BUTTON_SIZE_WIDE = (36,1)
PLACEHOLDER_IMAGE_FILE = os.path.join(os.path.dirname(__file__), "data", "wizard", "images", "placeholder.png")
if not os.path.exists(PLACEHOLDER_IMAGE_FILE):
	PLACEHOLDER_IMAGE_FILE = None

# try:
	# import PIL
# except ImportError:
	# input("Python module \"PIL\" not installed. Please install it with \"pip install pillow --user\"\n\
# Press enter to exit.")
	# exit()

# def pick_file(wintitle, kinds=[], path=None, multiselect=False, dirselect=False):
	# files_list = []
	# dir_prelist = [".. (parent directory)"]
	# if multiselect:
		# dir_prelist = ["Done Selecting"]+dir_prelist
	# if path is None:
		# path = os.path.dirname(__file__)
	# while True:
		# dir_list = list(os.listdir(path))
		# if multiselect:
			# choices_list = []
			# for item in dir_list:
				# if item in files_list:
					# choices_list.append("[@] "+item)
				# else:
					# choices_list.append("[ ] "+item)
				# if os.path.isdir(os.path.join(path, item)):
					# choices_list[-1] += "/"
		# else:
			# choices_list = dir_list

		# choice = easygui.choicebox(title=wintitle, msg=path, choices=dir_prelist+choices_list)
		# if choice is None:
			# return None
		# if multiselect:
			# c = choice[4:]
		# else:
			# c = choice
		# if choice.startswith(".."):
			# path = os.path.dirname(path)
		# elif choice == "Done Selecting":
			# return files_list
		# elif os.path.isdir(os.path.join(path, c)):
			# path = os.path.join(path, c)
		# else:
			# base, ext = os.path.splitext(c)
			# if len(kinds) > 0 and ext.lower().lstrip(".") not in kinds:
				# if not easygui.ynbox(title=wintitle, msg="Are you sure? This file is not a "+"/".join(kinds)+" file"):
					# continue
			# if multiselect:
				# if c in files_list:
					# files_list.remove(c)
				# else:
					# files_list.append(c)
			# else:
				# return os.path.join(path, choice)



def ContentSelectWindow(manifest_dict, content_type, skip=0, count=16):
	while True:
		e = _ContentSelectWindow(manifest_dict, content_type, skip, count)
		if type(e) is str:
			if e == "Prev":
				if skip > count:
					skip -= count
				else:
					skip = 0
			elif e == "Next":
				if skip+count < len(manifest_dict[f"mod.registry.{content_type}.names"]):
					skip += count
			else:
				return e
		elif not e or e is None:
			return None

def _ContentSelectWindow(manifest_dict, content_type, skip, count):
	# global WIN_WIDTH, EDITOR_BUTTON_SIZE, EDITOR_BUTTON_SIZE_WIDE
	if type(content_type) is not list:
		content_types = [content_type]
		ctstr = content_type
		manifest_dict[f"mod.registry.{content_type}.names"].sort()
		for cid in manifest_dict[f"mod.registry.{content_type}.names"]:
			contentnames.append((content_type, cid))
	else:
		contentnames = []
		content_types = content_type
		ctstr = "/".join(content_types)
		for ct in content_types:
			manifest_dict[f"mod.registry.{ct}.names"].sort()
			for cid in manifest_dict[f"mod.registry.{ct}.names"]:
				contentnames.append((ct, cid))
	layout = [
		[sg.Sizer(WIN_WIDTH, 0)],
		[sg.Button(f"Previous {count} {ctstr}s", key="Prev", size=EDITOR_BUTTON_SIZE)] if skip>0 else [],
		([sgScaledImage(os.path.join(manifest_dict["project_path"], manifest_dict["mod.textures"]), manifest_dict[f"mod.{ct}.{name}.texture"]),
			sg.Button(name, key=f"select_{name}", size=EDITOR_BUTTON_SIZE_WIDE),
		] for ct,name in contentnames[skip:skip+min(len(contentnames)-skip, count)]),
		[sg.Button(f"Next {count} {ctstr}s", key="Next", size=EDITOR_BUTTON_SIZE)] if skip+count<len(contentnames) else [],
		[sg.Button("Go Back", key="Back", size=EDITOR_BUTTON_SIZE)],
	]
	window = sg.Window(f"Mod {ctstr} List", layout)
	while True:
		event, values = window.read()
		if event in ('Back', sg.WIN_CLOSED):
			break
		elif event in ('Next', 'Prev'):
			window.close()
			return event
		elif event.startswith("select_"):
			window.close()
			# print(event)
			return event.split("_", maxsplit=1)[1]
	window.close()
	return False
	


def CreateRecipe(mfd):
	pass

def CreateBlock(mfd):
	layout = [
		[sg.Text("Block Name"), sg.Input(key="title")],
		[sg.Sizer(WIN_WIDTH, 20)],
		[sg.Text("Block Hardness"), sg.Input(key="hardness")],
		[sg.Text("Block Resistance"), sg.Input(key="resistance")],
		[sg.Text("(Note: you can input existing block names to copy)")],
		[sg.Sizer(WIN_WIDTH, 20)],
		[sg.Text("Tool type required to mine"),
			sg.Radio("None", "tooltype", k="tooltypenone", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Axe", "tooltype", k="tooltypeaxe", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Hoe", "tooltype", k="tooltypehoe", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Pickaxe", "tooltype", k="tooltypepickaxe", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Shovel", "tooltype", k="tooltypeshovel", size=EDITOR_BUTTON_SIZE_THIN),
		],
		[sg.Text("Tool level required to mine"),
			sg.Radio("Stone", "toollevel", k="toollevelstone", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Iron", "toollevel", k="toolleveliron", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Diamond", "toollevel", k="toolleveldiamond", size=EDITOR_BUTTON_SIZE_THIN),
		],
		[sg.Text("(Ignored if tool type is set to None)")],
		[sg.Sizer(WIN_WIDTH, 20)],
		[sg.Text("Block Drop Type")],
		[sg.Radio("None", "droptype", k="dropnone", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Drops Self", "droptype", k="dropnone", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Fixed Drops", "droptype", k="dropnone", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Fortunable", "droptype", k="dropnone", size=EDITOR_BUTTON_SIZE_THIN),
		],
		[sg.Button("Item to Drop", k="selectdropitem", size=EDITOR_BUTTON_SIZE_WIDE), sg.Text(k="dropitem")],
		[sg.Sizer(WIN_WIDTH, 20)],
		[sg.Text("Block Texture Layout")],
		[sg.Radio("Single (Like dirt blocks)", "style", k="single", default=True, size=EDITOR_BUTTON_SIZE)],
		[sg.Radio("Pillar (Like logs)", "style", k="pillar", size=EDITOR_BUTTON_SIZE)],
		[sg.Radio("Ground (Like grass blocks)", "style", k="ground", size=EDITOR_BUTTON_SIZE)],
		[sg.Radio("Rotatable (Like furnaces)", "style", k="rotatable", size=EDITOR_BUTTON_SIZE)],
		[sg.Text("Auto-generate")],
		[sg.Checkbox("All", k="genall", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Checkbox("Button", k="genbutton", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Checkbox("Fence", k="genfence", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Checkbox("Fence Gate", k="genfencegate", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Checkbox("Pressure Plate", k="genplate", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Checkbox("Slab", k="genslab", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Checkbox("Stairs", k="genstairs", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Checkbox("Wall", k="genwall", size=EDITOR_BUTTON_SIZE_THIN)
		],
		[sg.Sizer(WIN_WIDTH, 20)],
		[sg.Text("Main/Top Texture"), sg.Input(),
			sg.FileBrowse(key="imgfilemain", file_types=(("PNG Files", "*.png"), ("All Files", "*.* *")), initial_folder=os.path.join(mfd["project_path"], mfd["mod.textures"]))
		],
		[sg.Text("Side Texture"), sg.Input(),
			sg.FileBrowse(key="imgfileside", file_types=(("PNG Files", "*.png"), ("All Files", "*.* *")), initial_folder=os.path.join(mfd["project_path"], mfd["mod.textures"]))
		],
		[sg.Text("Bottom Texture"), sg.Input(),
			sg.FileBrowse(key="imgfilebottom", file_types=(("PNG Files", "*.png"), ("All Files", "*.* *")), initial_folder=os.path.join(mfd["project_path"], mfd["mod.textures"]))
		],
		[sg.Text("Front Texture"), sg.Input(),
			sg.FileBrowse(key="imgfilefront", file_types=(("PNG Files", "*.png"), ("All Files", "*.* *")), initial_folder=os.path.join(mfd["project_path"], mfd["mod.textures"]))
		],
		[sg.Sizer(WIN_WIDTH, 20)],
		[sg.Ok(size=EDITOR_BUTTON_SIZE_WIDE)],
	]
	window = sg.Window("Create New Block", layout)
	while True:
		event, values = window.read()
		if event in ('Cancel',):
			window.close()
		if event in (sg.WINDOW_CLOSED, 'Cancel'):
			return None
		elif event in ('selectdropitem',):
			item = ContentSelectWindow(mfd, ["block", "item"])
			if item is None:
				continue
			window["dropitem"].update(item)
		elif event in ('Ok',):
			cid = values["title"]
			if not len(cid):
				ErrorWindow("Block name must be defined.", parent=window)
				continue
			title, name, upper = ParseContentTitle(values["title"])
			fname = os.path.join(mfd["project_path"], "blocks", name+".m3ec")
			if os.path.exists(fname):
				d = readDictFile(fname)
			else:
				d = {}
			d["@"] = "block"
			d["block"] = "SimpleBlock"
			d["contentid"] = name
			d["title"] = title
			if name in mfd["mod.registry.block.names"] or name in mfd["mod.registry.item.names"]:
				ErrorWindow(f"Block/Item {name} already exists.", parent=window)
				continue
			if values["single"]:
				imgmain = values["imgfilemain"]
				if not len(imgmain):
					ErrorWindow("Main texture must be defined.", parent=window)
					continue
				imgmain = GetImageAsPNG(imgmain)
				if imgmain is None:
					continue
				d["texture"] = imgmain
			elif values["pillar"]:
				imgtop = values["imgfilemain"]
				if not len(imgtop):
					ErrorWindow("Top texture must be defined for pillar blocks.", parent=window)
					continue
				imgtop = GetImageAsPNG(imgtop)
				if imgtop is None:
					continue
				imgside = values["imgfileside"]
				if not len(imgside):
					ErrorWindow("Side texture must be defined for pillar blocks.", parent=window)
					continue
				imgside = GetImageAsPNG(imgside)
				if imgside is None:
					continue
				d["texture_top"] = imgmain
				d["texture_side"] = imgside
			elif values["ground"]:
				imgtop = values["imgfilemain"]
				if not len(imgtop):
					ErrorWindow("Top texture must be defined for ground-like blocks.", parent=window)
					continue
				imgtop = GetImageAsPNG(imgtop)
				if imgtop is None:
					continue
				imgbottom = values["imgfilebottom"]
				if not len(imgbottom):
					ErrorWindow("Bottom texture must be defined for ground-like blocks.", parent=window)
					continue
				imgbottom = GetImageAsPNG(imgbottom)
				if imgbottom is None:
					continue
				imgside = values["imgfileside"]
				if not len(imgside):
					ErrorWindow("Side texture must be defined for ground-like blocks.", parent=window)
					continue
				imgside = GetImageAsPNG(imgside)
				if imgside is None:
					continue
				d["texture_bottom"] = imgbottom
				d["texture_side"] = imgside
				d["texture_top"] = imgtop
			elif values["rotatable"]:
				imgtop = values["imgfilemain"]
				if not len(imgtop):
					ErrorWindow("Top texture must be defined for ground-like blocks.", parent=window)
					continue
				imgtop = GetImageAsPNG(imgtop)
				if imgtop is None:
					continue
				imgside = values["imgfileside"]
				if not len(imgside):
					ErrorWindow("Side texture must be defined for rotatable blocks.", parent=window)
					continue
				imgside = GetImageAsPNG(imgside)
				if imgside is None:
					continue
				imgbottom = values["imgfilebottom"]
				if not len(imgbottom):
					ErrorWindow("Bottom texture must be defined for ground-like blocks.", parent=window)
					continue
				imgbottom = GetImageAsPNG(imgbottom)
				if imgbottom is None:
					continue
				imgfront = values["imgfilefront"]
				if not len(imgfront):
					ErrorWindow("Front texture must be defined for ground-like blocks.", parent=window)
					continue
				imgfront = GetImageAsPNG(imgfront)
				if imgfront is None:
					continue
				d["texture_bottom"] = imgbottom
				d["texture_front"] = imgfront
				d["texture_side"] = imgside
				d["texture_top"] = imgtop
			else:
				continue
			hardness = values["hardness"]
			resistance = values["resistance"]
			if not len(hardness):
				hardness = "1.0f"
			else:
				if not hardness.isnumeric():
					hardness = str(mfd[f"mc.{hardness}.hardness"])
				if "." not in hardness:
					hardness = hardness+".0f"
				else:
					hardness = hardness+"f"
			if not len(resistance):
				resistance = "1.0f"
			else:
				if not resistance.isnumeric():
					resistance = str(mfd[f"mc.{resistance}.resistance"])
				if "." not in resistance:
					resistance = resistance+".0f"
				else:
					resistance = resistance+"f"
			d["hardness"] = mfd[f"mod.block.{name}.hardness"] = hardness
			d["resistance"] = mfd[f"mod.block.{name}.resistance"] = resistance
			if values["tooltypenone"]:
				d["requiresTool"] = "no"
			else:
				d["requiresTool"] = "yes"
				if values["tooltypeaxe"]:
					d["tooltype"] = "AXES"
				elif values["tooltypehoe"]:
					d["tooltype"] = "HOES"
				elif values["tooltypepickaxe"]:
					d["tooltype"] = "PICKAXES"
				elif values["tooltypeshovel"]:
					d["tooltype"] = "SHOVELS"
			if values["toollevelstone"]:
				d["toollevel"] = "STONE"
			elif values["toolleveliron"]:
				d["toollevel"] = "IRON"
			elif values["toolleveldiamond"]:
				d["toollevel"] = "DIAMOND"
			mfd["mod.files"][f"block.{name}"] = fname
			for tex in ["", "_top", "_side", "_bottom", "_front", "_back"]:
				if f"texture{tex}" in d.keys():
					# print(f"Original texture{tex} path:", d[f"texture{tex}"])
					d[f"texture{tex}"] = os.path.relpath(d[f"texture{tex}"], os.path.join(mfd["project_path"], mfd["mod.textures"]))
					# print(f"Relative texture{tex} path:", d[f"texture{tex}"])
			writeDictFile(fname, d)
			window.close()
			add_content(name, "block", d, mfd, fname)
			return d

def CreateItem(mfd):
	windowitems = [
		[sg.Text('Item Name'), sg.Input(key="itemname")],
		[sg.Text('Texture'), sg.Input(key="imgfile"),
			sg.FileBrowse(key="imgfile",file_types=(("PNG Files", "*.png"), ("All Files", "*.* *")), initial_folder=os.path.join(mfd["project_path"], mfd["mod.textures"]))
		],
		[sg.Ok(), sg.Cancel()],
	]
	window = sg.Window("Create New Item", windowitems)
	while True:
		event, values = window.read()
		if event in (sg.WINDOW_CLOSED, 'Cancel'):
			window.close()
			return None
		elif event in ('Ok',):
			itemtitle = values["itemname"]
			if not len(values["imgfile"]):
				ErrorWindow("Image file not specified.", parent=window)
				continue
			img = GetImageAsPNG(values["imgfile"])
			if img is None:
				continue
			itemtitle, itemname, itemupper = ParseContentTitle(itemtitle)
			if itemname in mfd["mod.registry.block.names"] or itemname in mfd["mod.registry.item.names"]:
				ErrorWindow(f"Block/Item {itemname} already exists.", parent=window)
				continue
			mfd["mod.registry.item.names"].append(itemname)
			mfd[f"mod.item.{itemname}.contentid"] = itemname
			mfd[f"mod.item.{itemname}.title"] = itemtitle
			mfd[f"mod.item.{itemname}.texture"] = texture = os.path.relpath(img, os.path.join(mfd["project_path"], mfd["mod.textures"]))
			fname = os.path.join(mfd["project_path"], "items", itemname+".m3ec")
			if os.path.exists(fname):
				d = readDictFile(fname)
			else:
				d = {}
			d["@"] = "item"
			d["item"] = "SimpleItem"
			d["contentid"] = itemname
			d["title"] = itemtitle
			d["texture"] = texture
			mfd["mod.files"][f"item.{itemname}"] = fname
			writeDictFile(fname, d)
			window.close()
			return d

def LoadProject(fname):
	content_types_list = ["item", "food", "fuel", "block", "ore", "recipe", "armor", "tool", "armormaterial", "toolmaterial", "enchantment"]

	if not os.path.exists(fname):
		ErrorWindow(f"Manifest file/directory \"{fname}\" not found!")
		return None

	if os.path.isdir(fname):
		project_path = fname
		manifest_file = os.path.join(fname, "manifest.m3ec")
		if not os.path.exists(manifest_file):
			manifest_file = os.path.join(fname, "manifest.txt")
			if not os.path.exists(manifest_file):
				ErrorWindow(f"Manifest file (manifest.m3ec/manifest.txt) not found in \"{fname}\". Aborting.")
	else:
		project_path = os.path.dirname(fname)
		manifest_file = fname

	manifest_dict = readDictFile(manifest_file)

	manifest_dict["manifest_file"] = manifest_file
	manifest_dict["project_path"] = project_path

	source_path = os.path.join(os.path.dirname(__file__), "data")
	fname = os.path.join(source_path, "mc", "blocks.json")
	if not os.path.exists(fname):
		print(f"Warning: data file \"{fname}\" not found!")
	else:
		with open(fname) as f:
			blocks = json.load(f)
		for block in blocks:
			blockid = block["name"]
			for key in block.keys():
				if key != blockid:
					manifest_dict[f"mc.{blockid}.{key}"] = block[key]

	if "mod.prefix" not in manifest_dict.keys():
		manifest_dict["mod.prefix"] = "com"
	if EnsureValueExistsWindow(manifest_dict, "mod.author", "Mod Author") is None:
		return None
	if EnsureValueExistsWindow(manifest_dict, "mod.title", "Mod Title") is None:
		return None
	if "mod.class" not in manifest_dict.keys():
		manifest_dict["mod.class"] = manifest_dict["mod.title"].title().replace(" ","")
	prefix, modauthor, modclass = (manifest_dict[k] for k in \
		("mod.prefix", "mod.author", "mod.class"))

	if "mod.mcpath" not in manifest_dict:
		manifest_dict["mod.mcpath"] = modclass.lower()

	manifest_dict["mod.package"] = f"{prefix}.{modauthor}.{modclass}".lower()
	manifest_dict["mod.maven_group"] = f"{prefix}.{modauthor}".lower()


	modpath = manifest_dict["mod.package"]
	modmcpath = manifest_dict["mod.mcpath"]
	modmcpathdir = 	manifest_dict["mod.packagedir"] = os.path.join(prefix, modauthor, modclass).lower()


	EnsureValueExistsWindow(manifest_dict, "mod.description", "Mod Description", default="")
	# EnsureValueExistsWindow(manifest_dict, "mod.credits", "Mod Credits")
	EnsureValueExistsWindow(manifest_dict, "mod.license", "Mod License", longtitle="You can find a list of common licenses at choosealicense.com", default="All Rights Reserved")

	manifest_dict["mod.content_types"] = content_types_list
	for content_type in content_types_list:
		manifest_dict[f"mod.registry.{content_type}.names"] = []

	if "mod.paths" not in manifest_dict.keys():
		manifest_dict["mod.paths"] = ["armor", "blocks", "items", "ores", "recipes", "tools"]

	manifest_dict[f"mod.files"] = {}
	manifest_dict["#comments"] = {}
	for path in manifest_dict["mod.paths"]:
		d = os.path.join(project_path, path)
		if os.path.exists(d):
			for fname in walk(os.path.normpath(d)):
				if fname.endswith(".txt") or fname.endswith(".m3ec"):
					d = readDictFile(fname)
					manifest_dict["#comments"][fname] = d["#comments"]
					if "@" in d.keys():
						content_type = d["@"]
						if content_type == "itemfactory":
							for cid in d["items"]:
								dictinst = {"item":d["type"], "title":" ".join([w.capitalize() for w in cid.split("_")]), "texture":cid+".png"}
								add_content(cid, "item", dictinst, manifest_dict, fname)
						elif content_type == "recipe":
							if "contentid" in d.keys():
								cid = d["contentid"]
							else:
								cid = os.path.splitext(os.path.basename(fname))[0]
							add_content(cid, content_type, d, manifest_dict, fname)
						elif "contentid" in d.keys():
							cid = d["contentid"]
							add_content(cid, content_type, d, manifest_dict, fname)
		else:
			os.mkdir(d)
	
	d = os.path.join(project_path, "textures")
	if not os.path.exists(d):
		os.mkdir(d)

	# for key in manifest_dict.keys():
		# print(f"{key}: {manifest_dict[key]}")

	source_path = manifest_dict["source_path"] = os.path.join(os.path.dirname(__file__), "data")
	path = project_path
	return manifest_dict

def SaveProject(fname, manifest_dict):
	if "mod.credits" not in manifest_dict.keys():
		manifest_dict["mod.credits"] = ""
	if "mod.paths" not in manifest_dict.keys():
		manifest_dict["mod.paths"] = []
	if "mod.textures" not in manifest_dict.keys():
		manifest_dict["mod.textures"] = "textures"
	if "mod.homepage" not in manifest_dict.keys():
		manifest_dict["mod.homepage"] = ""
	if "mod.sources" not in manifest_dict.keys():
		manifest_dict["mod.sources"] = ""

	d = readDictFile(fname)
	if d is None:
		d = {}
	for k in [
			"mod.package", "mod.prefix", "mod.author", "mod.class", "mod.title", "mod.credits", "mod.description",
			"mod.license", "mod.textures", "mod.paths", "mod.homepage", "mod.sources", "mod", "mod.iconItem",
			]:
		if k in manifest_dict.keys():
			d[k] = manifest_dict[k]

	writeDictFile(fname, d)

def GetImageAsPNG(img):
	if not img.endswith(".png"):
		try:
			i = Image.open(img)
		except:
			ErrorWindow(f"Failed to open image file \"{img}\".")
			return None
		img = os.path.splitext(img)[0]+".png"
		if os.path.exists(img):
			old = os.path.splitext(img)[0]+"_old.png"
			if os.path.exists(old):
				os.remove(old)
			os.rename(img, old)
		i.save(img)
	return img

def sgScaledImage(d, fname, size=(32, 32)):
	if type(fname) is not str or not len(fname) or fname == "None":
		fname = PLACEHOLDER_IMAGE_FILE
	else:
		fname = os.path.join(d, fname)
	if type(fname) is str:
		td = os.path.join(tempfile.gettempdir(), "m3ecWizard.ImageTemp")
		if os.path.exists(td) and not os.path.isdir(td):
			os.remove(td)
		if not os.path.exists(td):
			os.mkdir(td)
		if not fname.endswith(".png"):
			fname = fname+".png"
		if os.path.exists(fname):
			with open(fname, 'rb') as f:
				h = hashlib.sha1()
				h.update(f.read())
				h = h.hexdigest()
			tmp = os.path.join(td, h+".png")
			if not os.path.exists(tmp):
				Image.open(fname).resize(size, Image.NEAREST).save(tmp)
			return sg.Image(tmp)
	x, y = size
	return sg.Sizer(x, y)

def ContentEditWindow(manifest_dict, content_type, skip=0, count=15):
	while True:
		e = _ContentEditWindow(manifest_dict, content_type, skip, count)
		if e == "Prev":
			if skip > count:
				skip -= count
			else:
				skip = 0
		elif e == "Next":
			if skip+count < len(manifest_dict[f"mod.registry.{content_type}.names"]):
				skip += count
		elif not e:
			break

def _ContentEditWindow(manifest_dict, content_type, skip, count):
	# global WIN_WIDTH, EDITOR_BUTTON_SIZE, EDITOR_BUTTON_SIZE_WIDE
	contentnames = manifest_dict[f"mod.registry.{content_type}.names"]
	contentnames.sort()
	layout = [
		[sg.Sizer(WIN_WIDTH, 0)],
		[sg.Button(f"Previous {count} {content_type}s", key="Prev", size=EDITOR_BUTTON_SIZE)] if skip>0 else [],
		([sgScaledImage(os.path.join(manifest_dict["project_path"], manifest_dict["mod.textures"]), manifest_dict[f"mod.{content_type}.{name}.texture"]),
			sg.Button(name, key=f"rename_{name}", size=EDITOR_BUTTON_SIZE_WIDE),
			# sg.Button("edit", key=f"edit_{name}", size=EDITOR_BUTTON_SIZE),
			sg.Button("remove", key=f"remove_{name}", size=EDITOR_BUTTON_SIZE)
		] for name in contentnames[skip:skip+min(len(contentnames)-skip, count)]),
		[sg.Button(f"Next {count} {content_type}s", key="Next", size=EDITOR_BUTTON_SIZE)] if skip+count<len(contentnames) else [],
		[sg.Button("Go Back", key="Back", size=EDITOR_BUTTON_SIZE)],
	]
	window = sg.Window(f"Mod {content_type} List", layout)
	while True:
		event, values = window.read()
		if event in ('Back', sg.WIN_CLOSED):
			window.close()
			return False
		elif event in ('Next','Prev'):
			window.close()
			return event
		elif event.startswith("rename_"):
			old = event.split("_",maxsplit=1)[1]
			name = RenameValueWindow(old, valuetype=content_type)
			if name is None:
				continue
			manifest_dict[f"mod.registry.{content_type}.names"][manifest_dict[f"mod.registry.{content_type}.names"].index(old)] = name
			fname = manifest_dict["mod.files"][f"{content_type}.{old}"]
			newname = os.path.join(os.path.dirname(fname), name+os.path.splitext(fname)[1])
			if os.path.exists(fname):
				os.rename(fname, newname)
			del manifest_dict["mod.files"][f"{content_type}.{old}"]
			manifest_dict["mod.files"][f"{content_type}.{name}"] = newname
			d = {}
			for key in manifest_dict.keys():
				if f"{content_type}.{old}" in key:
					d[key.replace(f"{content_type}.{old}", f"{content_type}.{newname}")] = manifest_dict[key]
				else:
					d[key] = manifest_dict[key]
			del manifest_dict
			manifest_dict = d
			window.close()
			return True
		elif event.startswith("edit_"):
			event.split("_",maxsplit=1)[1]
		elif event.startswith("remove_"):
			name = event.split("_",maxsplit=1)[1]
			event, values = sg.Window("Are you sure?", [[sg.Text(f"{name} will be deleted.")],[sg.Yes(),sg.Cancel()]]).read(close=True)
			if event in ('Yes',):
				manifest_dict[f"mod.registry.{content_type}.names"].remove(name)
				fname = manifest_dict["mod.files"][f"{content_type}.{name}"]
				if os.path.exists(fname):
					os.remove(fname)
				del manifest_dict["mod.files"][f"{content_type}.{name}"]
				window.close()
				return True
	window.close()
	return False

def ModEditor(fname):
	manifest_dict = LoadProject(fname)
	if type(manifest_dict) is dict:
		while _ModEditor(manifest_dict, fname):
			pass

def _ModEditor(manifest_dict, fname):
	# global WIN_WIDTH, EDITOR_BUTTON_SIZE
	if "mod.iconItem" not in manifest_dict.keys():
		manifest_dict["mod.iconItem"] = None
	layout = [
		[sg.Sizer(WIN_WIDTH,0)],
		[sgScaledImage(os.path.join(manifest_dict["project_path"], manifest_dict["mod.textures"]), manifest_dict["mod.iconItem"]),
			sg.Button("Set Mod Icon", key="SetIcon", size=EDITOR_BUTTON_SIZE),
			sg.Button(manifest_dict["mod.title"], key="SetTitle", size=EDITOR_BUTTON_SIZE),
			sg.Button(manifest_dict["mod.mcpath"], key="SetName", size=EDITOR_BUTTON_SIZE),
		],
		[sg.Button("Build Project", key="Build", size=EDITOR_BUTTON_SIZE), sg.Button("Quit", key="Exit", size=EDITOR_BUTTON_SIZE)],
		[sg.Text("Import Texture"), sg.Input(key="TextureImport"),
			sg.FilesBrowse(key="TextureImport", file_types=(("PNG Files", "*.png"),("All Files","*.* *"))),
			sg.Button("Import", key="ImportTexture")
		],
		[sg.Sizer(WIN_WIDTH,20)],
		[sg.Text("Blocks")],
		[sg.Button("New Block", key="NewBlock", size=EDITOR_BUTTON_SIZE),
			sg.Button("Edit Existing Blocks", key="EditBlock", size=EDITOR_BUTTON_SIZE),
		],
		[sg.Sizer(WIN_WIDTH,20)],
		[sg.Text("Items")],
		[sg.Button("New Item", key="NewItem", size=EDITOR_BUTTON_SIZE),
			sg.Button("Edit Existing Items", key="EditItem", size=EDITOR_BUTTON_SIZE),
		],
		[sg.Sizer(WIN_WIDTH,20)],
		[sg.Text("Recipes")],
		[sg.Button("New Recipe", key="NewRecipe", size=EDITOR_BUTTON_SIZE),
			sg.Button("Edit Existing Recipes", key="EditRecipe", size=EDITOR_BUTTON_SIZE),
		],
	]
	window = sg.Window("M3EC Mod Editor", layout)
	while True:
		event, values = window.read()
		if event in ('Exit', sg.WIN_CLOSED):
			SaveProject(fname, manifest_dict)
			break
		elif event in ('Build',):
			BuildMod(manifest_dict)
		elif event in ('SetIcon',):
			item = ContentSelectWindow(manifest_dict, "item")
			if item is None:
				continue
			manifest_dict["mod.iconItem"] = manifest_dict[f"mod.item.{item}.texture"]
			# print(manifest_dict["mod.iconItem"])
			window.close()
			return True
		elif event in ('SetTitle',):
			title = RenameValueWindow(manifest_dict["mod.title"], "Mod Title")
			if title is None:
				continue
			modclass, name, upper = ParseContentTitle(title)
			manifest_dict["mod.title"] = title
			window["SetTitle"].update(title)
		elif event in ('SetName',):
			name = RenameValueWindow(manifest_dict["mod.mcpath"], "Mod Namespace")
			if name is None:
				continue
			modclass, name, upper = ParseContentTitle(name)
			manifest_dict["mod.mcpath"] = name
			manifest_dict["mod.class"] = modclass
			window["SetName"].update(name)
		elif event in ('NewItem',):
			CreateItem(manifest_dict)
		elif event in ('NewBlock',):
			CreateBlock(manifest_dict)
		elif event in ('NewRecipe',):
			CreateRecipe(manifest_dict)
		elif event in ('ImportTexture',):
			if "TextureImport" in values.keys():
				fnames = values["TextureImport"]
				if ";" in fnames:
					fnames = fnames.split(";")
				else:
					fnames = [fnames]
				for fname in fnames:
					imgname = os.path.join(manifest_dict["project_path"], manifest_dict["mod.textures"], os.path.splitext(os.path.basename(fname))[0]+".png")
					if not os.path.exists(fname):
						ErrorWindow(f"File \"{fname}\" does not exist.")
					else:
						if os.path.exists(imgname):
							os.remove(imgname)
						try:
							img = Image.open(fname)
						except:
							ErrorWindow(f"Failed to load image file \"{fname}\".")
							continue
						img.save(imgname)
		elif event.startswith('Edit'):
			ContentEditWindow(manifest_dict, event[4:].lower())
			
	window.close()
	return False

def BuildMod(d):
	global WIN_WIDTH, EDITOR_BUTTON_SIZE
	layout = [
		[sg.Text("Currently Fabric version 1.18 is broken and will not build ore generation.")],
		[sg.Sizer(WIN_WIDTH, 20)],
		[sg.Checkbox("Build mod JAR", k="buildjar", size=EDITOR_BUTTON_SIZE)],
		[sg.Sizer(WIN_WIDTH, 20)],
		[sg.Button("All supported modloaders and game versions", k="all")],
		[sg.Button("All supported Forge versions", k="forge")],
		[sg.Button("Forge 1.16.5", k="forge1.16.5", size=EDITOR_BUTTON_SIZE)],
		[sg.Button("All supported Fabric versions", k="fabric")],
		[sg.Button("Fabric 1.16.5", k="fabric1.16.5", size=EDITOR_BUTTON_SIZE)],
		[sg.Button("Fabric 1.17", k="fabric1.17", size=EDITOR_BUTTON_SIZE)],
		[sg.Button("Fabric 1.17.1", k="fabric1.17.1", size=EDITOR_BUTTON_SIZE)],
		[sg.Button("Fabric 1.18", k="fabric1.18", size=EDITOR_BUTTON_SIZE)],
		[sg.Button("Fabric 1.18.1", k="fabric1.18.1", size=EDITOR_BUTTON_SIZE)],
		[sg.Cancel()],
		[sg.Text("",k="building")]
	]
	window = sg.Window("Build Project", layout)
	event, values = window.read(close=True)
	if event not in ('Cancel', sg.WIN_CLOSED):
		window["building"].update("Building Project...")
		cmd = ["python", os.path.join(os.path.dirname(__file__), "m3ec.py"), d["project_path"], event]
		if values["buildjar"]:
			cmd.append("buildjar")
		subprocess.Popen(cmd).wait()

def MainMenuWindow():
	global WIN_WIDTH, EDITOR_BUTTON_SIZE
	windowitems = [
		[sg.Sizer(WIN_WIDTH,0)],
		[sg.Text("M3EC Mod Wizard")],
		[sg.Button("New Project", key="_new_", size=EDITOR_BUTTON_SIZE),
			sg.Button("Open Project", key="_open_", size=EDITOR_BUTTON_SIZE), sg.Quit(size=EDITOR_BUTTON_SIZE)],
		[sg.Text("Recent Projects")],
		([sg.Button(project, key=f"_open_{project}", size=EDITOR_BUTTON_SIZE), sg.Button("remove", key=f"_remove_{project}")] for project in sorted(saved_projects["titles"]))
	]
	window = sg.Window("M3EC Mod Creation Wizard", windowitems)
	while True:
		with open(os.path.join(os.path.dirname(__file__), "config", "projects.json"), "w") as f:
			json.dump(saved_projects, f)
		event, values = window.read()
		if event in ('Quit', sg.WIN_CLOSED):
			break
		elif event in ("_new_",):
			w = sg.Window("New Project", [
				[sg.Text("New Mod Project")],
				[sg.Text("Title"), sg.Input()],
				[sg.Text("Author"), sg.Input()],
				[sg.Text("License"), sg.Input(default_text="All Rights Reserved")],
				[sg.Text("Project Directory"), sg.Input(), sg.FolderBrowse()],
				[sg.Submit(), sg.Cancel()],
			])
			while True:
				event, values = w.read()
				if event in ('Cancel', sg.WIN_CLOSED):
					w.close()
					break
				elif event in ('Submit',):
					if not len(values[0]):
						ErrorWindow("Please specify a project title.")
					elif not len(values[1]):
						ErrorWindow("Please specify an author name.")
					elif not len(values[3]):
						ErrorWindow("Please specify a project directory.")
					else:
						data = "\n".join([
							"@: manifest",
							"mod:",
							f".title: {values[0]}",
							f".author: {values[1]}",
							f".license: {values[2]}",
							".textures: textures",
							"+.paths: blocks",
							"+.paths: items",
							"+.paths: recipes",
							"+.paths: ores",
							"+.paths: tools",
						])

						fname = os.path.join(values[3], "manifest.m3ec")
						with open(fname,'w') as f:
							f.write(data)

						if values[0] not in saved_projects["titles"]:
							saved_projects["titles"].append(values[0])
						saved_projects["dirs"][values[0]] = fname

						w.close()
						window.close()
						ModEditor(fname)
						return True
			
		elif event in ("_open_",):
			w = sg.Window("Open Project", [
				[sg.Text("Select M3EC project manifest file")],
				[sg.Input(), sg.FileBrowse(file_types=(("M3EC Manifest Files", "*.m3ec *.txt"), ("All Files", "*.* *")))],
				[sg.Submit(), sg.Cancel()]
			])
			manifest = None
			while True:
				event, values = w.read(close=True)
				if event in ('Quit', sg.WIN_CLOSED, 'Cancel'):
					break
				elif event in ('Submit',):
					manifest = values['Browse']
					data = readDictFile(manifest)
					if data is None:
						ErrorWindow(f"Failed to load file \"{manifest}\"")
						break

					EnsureValueExistsWindow(data, "mod.title", "Mod Title")

					title = data["mod.title"]
					if title not in saved_projects["titles"]:
						saved_projects["titles"].append(title)
					saved_projects["dirs"][title] = manifest

					window.close()
					ModEditor(saved_projects["dirs"][title])
					return True
			

		elif event.startswith("_open_"):
			window.close()
			ModEditor(saved_projects["dirs"][event[6:]])
			return True
		elif event.startswith("_remove_"):
			window.close()
			try:
				saved_projects["titles"].remove(event[8:])
			except:
				pass
			try:
				del saved_projects["dirs"][event[8:]]
			except KeyError:
				pass
			return True
	return False

def RenameValueWindow(old, valuetype="", parent=None):
	window = sg.Window(f"Rename {valuetype}", [[sg.Text(f"Rename {old} to"), sg.Input()],[sg.Ok(), sg.Cancel()]])
	while True:
		event, values = window.read()
		if event in ('Cancel', sg.WIN_CLOSED):
			window.close()
			return None
		elif event in ('Ok',):
			window.close()
			return values[0]

def ErrorWindow(text, title="Error", parent=None):
	return sg.Window(title, [[sg.Text(text)],[sg.Ok()]]).read(close=True)

def MissingValueWindow(title, longtitle="", default="", parent=None):
	return sg.Window("Missing Value", [[sg.Text(f"{title} is not yet defined. Please define it below.")],[sg.Text(longtitle)],[sg.Input(default_text=default)],[sg.Submit(),sg.Cancel()]]).read(close=True)

def EnsureValueExistsWindow(d, key, title, longtitle="", default="", parent=None):
	if key not in d.keys():
		event, values = MissingValueWindow(title, longtitle=longtitle, default=default, parent=parent)
		# print(event, values)
		if event not in ('Submit',):
			# print("Setting default value", default, "for key", key)
			d[key] = default
			return None
		# print("Setting value", values[0], "for key", key)
		d[key] = values[0]
	return d[key]

if __name__=='__main__':
	d = os.path.join(os.path.dirname(__file__), "config")
	if not os.path.exists(d):
		os.mkdir(d)
	fname = os.path.join(os.path.dirname(__file__), "config", "projects.json")
	if os.path.exists(fname):
		with open(fname) as f:
			saved_projects = json.load(f)
	else:
		saved_projects = {"titles":[], "dirs":{}}
	while MainMenuWindow():
		pass
