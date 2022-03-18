

import os, sys, json, subprocess, tempfile, hashlib, shutil
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



def ContentSelectWindow(manifest_dict, content_type, skip=0, count=16, vanillabutton=True):
	while True:
		e = _ContentSelectWindow(manifest_dict, content_type, skip, count, vanillabutton)
		if type(e) is str:
			if e == "Prev":
				if skip > count:
					skip -= count
				else:
					skip = 0
			elif e == "Next":
				if content_type == "vanilla":
					if skip+count < len(manifest_dict["mc.names"]):
						skip += count
				else:
					if skip+count < len(manifest_dict[f"mod.registry.{content_type}.names"]):
						skip += count
			else:
				return e
		elif not e or e is None:
			return None

def _ContentSelectWindow(manifest_dict, content_type, skip, count, vanillabutton):
	# global WIN_WIDTH, EDITOR_BUTTON_SIZE, EDITOR_BUTTON_SIZE_WIDE
	contentnames = []
	if type(content_type) is not list:
		if content_type == "vanilla":
			content_types = ["block", "item"]
			ctstr = "block/item"
			contentnames = sorted([("",item) for item in manifest_dict["mc.names"]])
			content_types = [content_type]
		else:
			ctstr = content_type
			manifest_dict[f"mod.registry.{content_type}.names"].sort()
			for cid in manifest_dict[f"mod.registry.{content_type}.names"]:
				contentnames.append((content_type, cid))
	else:
		content_types = content_type
		ctstr = "/".join(content_types)
		for ct in content_types:
			manifest_dict[f"mod.registry.{ct}.names"].sort()
			for cid in manifest_dict[f"mod.registry.{ct}.names"]:
				contentnames.append((ct, cid))
	layout = [
		[sg.Sizer(WIN_WIDTH, 0)],
		[sg.Input(k="itemname"), sg.Button(f"{ctstr} name", k="submititemname")],
		[sg.Button(f"Vanilla {ctstr}s", key="Vanilla", size=EDITOR_BUTTON_SIZE)] if content_type != "vanilla" and vanillabutton else [],
		[sg.Button(f"Previous {count} {ctstr}s", key="Prev", size=EDITOR_BUTTON_SIZE)] if skip>0 else [],
		([sgScaledImage(os.path.join(manifest_dict["project_path"], manifest_dict["mod.textures"]), d=manifest_dict, k=f"mod.{ct}.{name}.texture"),
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
		elif event in ('Vanilla',):
			window.close()
			return ContentSelectWindow(manifest_dict, "vanilla")
		elif event in ('submititemname',):
			if len(values['itemname']):
				window.close()
				return values['itemname']
		elif event.startswith("select_"):
			window.close()
			# print(event)
			return event.split("_", maxsplit=1)[1]
	window.close()
	return False
	


def CreateRecipe(mfd):
	layout = [
		[sg.Sizer(WIN_WIDTH, 0)],
		[sg.Text("Recipe Type")],
		[sg.Button("Shaped", k="shaped", size=EDITOR_BUTTON_SIZE),
			sg.Button("Shapeless", k="shapeless", size=EDITOR_BUTTON_SIZE),
			sg.Button("Smelting", k="smelting", size=EDITOR_BUTTON_SIZE),
			sg.Button("Stonecutter", k="stonecutter", size=EDITOR_BUTTON_SIZE),
			sg.Button("Smithing", k="smithing", size=EDITOR_BUTTON_SIZE),
		],
		[sg.Cancel()],
	]
	event, values = sg.Window("Create New Recipe", layout).read(close=True)
	if event == "shaped":
		recipe = CreateShapedRecipe(mfd)
	elif event == "shapeless":
		recipe = CreateShapelessRecipe(mfd)
	elif event == "smelting":
		recipe = CreateSmeltingRecipe(mfd)
	elif event == "stonecutter":
		recipe = CreateStonecutterRecipe(mfd)
	elif event == "smithing":
		recipe = CreateSmithingRecipe(mfd)
	else:
		return None
	
	if type(recipe) is dict:
		n = 1
		cid = recipe["result"]
		while cid in mfd["mod.registry.recipe.names"]:
			n += 1
			cid = recipe["result"]+"_"+str(n)
		recipe["contentid"] = cid

		fname = os.path.join(mfd["project_path"], "recipes", cid+".m3ec")
		n = 1
		while os.path.exists(fname):
			n += 1
			fname = os.path.join(mfd["project_path"], "recipes", cid+"_"+str(n)+".m3ec")

		writeDictFile(fname, recipe)
		add_content(cid, "recipe", recipe, mfd, fname)
	return recipe

def CreateShapedRecipe(mfd):
	sx, sy = EDITOR_BUTTON_SIZE
	layout = [
		[sg.Sizer(WIN_WIDTH,0)],
		[sg.Button("empty", k="item1", size=EDITOR_BUTTON_SIZE),
			sg.Button("empty", k="item2", size=EDITOR_BUTTON_SIZE),
			sg.Button("empty", k="item3", size=EDITOR_BUTTON_SIZE),
		],
		[sg.Button("empty", k="item4", size=EDITOR_BUTTON_SIZE),
			sg.Button("empty", k="item5", size=EDITOR_BUTTON_SIZE),
			sg.Button("empty", k="item6", size=EDITOR_BUTTON_SIZE),
			sg.Sizer(sx, sy),
			sg.Button("result", k="itemresult", size=EDITOR_BUTTON_SIZE),
		],
		[sg.Button("empty", k="item7", size=EDITOR_BUTTON_SIZE),
			sg.Button("empty", k="item8", size=EDITOR_BUTTON_SIZE),
			sg.Button("empty", k="item9", size=EDITOR_BUTTON_SIZE),
			sg.Sizer(sx, sy),
			sg.Text("Count:"),
			sg.Input(size=EDITOR_BUTTON_SIZE, k="count"),
		],
		[sg.Sizer(0, 20)],
		[sg.Ok(size=EDITOR_BUTTON_SIZE), sg.Cancel(size=EDITOR_BUTTON_SIZE)],
	]
	window = sg.Window("Create Shaped Recipe", layout)
	recipe = {"@": "recipe", "recipe": "ShapedRecipe", "pattern": [], "items":[], "itemkeys":[], "result": "", "count": "1"}
	while True:
		event, values = window.read()
		if event in (sg.WINDOW_CLOSED, 'Cancel'):
			break
		elif event == "Ok":
			if not len(recipe["pattern"]):
				ErrorWindow("Recipe must contain at least one item.")
				continue
			if not len(recipe["result"]):
				ErrorWindow("Result must not be empty.")
				continue
			if len(values["count"]):
				if not values["count"].isalnum() or "." in values["count"] or int(values["count"]) < 1:
					ErrorWindow("Count must be a number greater than or equal to 1.")
					continue
				recipe["count"] = values["count"]
			for row in range(len(recipe["pattern"])):
				recipe["pattern"][row] = '"'+"".join(recipe["pattern"][row])+'"'
			window.close()
			return recipe
		elif event.startswith("item"):
			item = ContentSelectWindow(mfd, ["block", "item"])
			if event[4:] == "result":
				recipe["result"] = item
			else:
				num = int(event[4])
				row = num // 3
				col = num % 3
				while len(recipe["pattern"]) <= row:
					recipe["pattern"].append([])
				while len(recipe["pattern"][row]) <= col:
					recipe["pattern"][row].append(" ")
				if item in recipe["items"]:
					recipe["pattern"][row][col] = recipe["itemkeys"][recipe["items"].index(item)]
				else:
					c = chr(ord('A') + len(recipe["items"]))
					recipe["pattern"][row][col] = c
					recipe["itemkeys"].append(c)
					recipe["items"].append(item)
			if item is None:
				window[event].update("empty")
			else:
				window[event].update(item)
	window.close()

def CreateShapelessRecipe(mfd):
	pass

def CreateSmeltingRecipe(mfd):
	pass

def CreateStonecutterRecipe(mfd):
	pass

def CreateSmithingRecipe(mfd):
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
			sg.Radio("None", "tooltype", k="tooltypenone", size=EDITOR_BUTTON_SIZE_THIN, default=True),
			sg.Radio("Axe", "tooltype", k="tooltypeaxe", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Hoe", "tooltype", k="tooltypehoe", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Pickaxe", "tooltype", k="tooltypepickaxe", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Shovel", "tooltype", k="tooltypeshovel", size=EDITOR_BUTTON_SIZE_THIN),
		],
		[sg.Text("Tool level required to mine"),
			sg.Radio("Stone", "toollevel", k="toollevelstone", size=EDITOR_BUTTON_SIZE_THIN, default=True),
			sg.Radio("Iron", "toollevel", k="toolleveliron", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Diamond", "toollevel", k="toolleveldiamond", size=EDITOR_BUTTON_SIZE_THIN),
		],
		[sg.Text("(Ignored if tool type is set to None)")],
		[sg.Sizer(WIN_WIDTH, 20)],
		[sg.Text("Block Drop Type")],
		[sg.Radio("None", "droptype", k="dropnone", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Drops Self", "droptype", k="dropself", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Fixed Drops", "droptype", k="dropfixed", size=EDITOR_BUTTON_SIZE_THIN),
			sg.Radio("Fortunable", "droptype", k="dropfortunable", size=EDITOR_BUTTON_SIZE_THIN),
		],
		[sg.Button("Item to Drop", k="selectdropitem", size=EDITOR_BUTTON_SIZE_WIDE), sg.Text(k="dropitem"), sg.Text("Drop Count/Chances:"), sg.Input(k="dropcount")],
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
		[sg.Ok(size=EDITOR_BUTTON_SIZE_WIDE), sg.Cancel(size=EDITOR_BUTTON_SIZE_WIDE)],
	]
	window = sg.Window("Create New Block", layout)
	dropitem = None
	while True:
		event, values = window.read()
		if event in (sg.WINDOW_CLOSED, 'Cancel'):
			window.close()
			return None
		elif event in ('selectdropitem',):
			dropitem = ContentSelectWindow(mfd, ["block", "item"])
			if dropitem is None:
				continue
			window["dropitem"].update(dropitem)
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
				imgmain = GetImageAsPNG(imgmain, mfd)
				if imgmain is None:
					continue
				d["texture"] = imgmain
			elif values["pillar"]:
				imgtop = values["imgfilemain"]
				if not len(imgtop):
					ErrorWindow("Top texture must be defined for pillar blocks.", parent=window)
					continue
				imgtop = GetImageAsPNG(imgtop, mfd)
				if imgtop is None:
					continue
				imgside = values["imgfileside"]
				if not len(imgside):
					ErrorWindow("Side texture must be defined for pillar blocks.", parent=window)
					continue
				imgside = GetImageAsPNG(imgside, mfd)
				if imgside is None:
					continue
				d["texture_top"] = imgmain
				d["texture_side"] = imgside
			elif values["ground"]:
				imgtop = values["imgfilemain"]
				if not len(imgtop):
					ErrorWindow("Top texture must be defined for ground-like blocks.", parent=window)
					continue
				imgtop = GetImageAsPNG(imgtop, mfd)
				if imgtop is None:
					continue
				imgbottom = values["imgfilebottom"]
				if not len(imgbottom):
					ErrorWindow("Bottom texture must be defined for ground-like blocks.", parent=window)
					continue
				imgbottom = GetImageAsPNG(imgbottom, mfd)
				if imgbottom is None:
					continue
				imgside = values["imgfileside"]
				if not len(imgside):
					ErrorWindow("Side texture must be defined for ground-like blocks.", parent=window)
					continue
				imgside = GetImageAsPNG(imgside, mfd)
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
				imgtop = GetImageAsPNG(imgtop, mfd)
				if imgtop is None:
					continue
				imgside = values["imgfileside"]
				if not len(imgside):
					ErrorWindow("Side texture must be defined for rotatable blocks.", parent=window)
					continue
				imgside = GetImageAsPNG(imgside, mfd)
				if imgside is None:
					continue
				imgbottom = values["imgfilebottom"]
				if not len(imgbottom):
					ErrorWindow("Bottom texture must be defined for ground-like blocks.", parent=window)
					continue
				imgbottom = GetImageAsPNG(imgbottom, mfd)
				if imgbottom is None:
					continue
				imgfront = values["imgfilefront"]
				if not len(imgfront):
					ErrorWindow("Front texture must be defined for ground-like blocks.", parent=window)
					continue
				imgfront = GetImageAsPNG(imgfront, mfd)
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
				hardness = "1.0"
			else:
				if not hardness.isnumeric():
					_, hardness, _ = ParseContentTitle(hardness)
					if f"mc.{hardness}.hardness" in mfd.keys():
						hardness = str(mfd[f"mc.{hardness}.hardness"])
					else:
						hardness = "1.0"
				if "." not in hardness:
					hardness = hardness+".0"
			if not len(resistance):
				resistance = "1.0"
			else:
				if not resistance.isnumeric():
					_, resistance, _ = ParseContentTitle(resistance)
					if f"mc.{resistance}.resistance" in mfd.keys():
						resistance = str(mfd[f"mc.{resistance}.resistance"])
					else:
						resistance = "1.0"
				if "." not in resistance:
					resistance = resistance+".0"
			d["hardness"] = mfd[f"mod.block.{name}.hardness"] = hardness
			d["resistance"] = mfd[f"mod.block.{name}.resistance"] = resistance
			if values["tooltypenone"]:
				d["requiresTool"] = "no"
			else:
				d["requiresTool"] = "yes"
				if values["tooltypeaxe"]:
					d["toolclass"] = "AXES"
				elif values["tooltypehoe"]:
					d["toolclass"] = "HOES"
				elif values["tooltypepickaxe"]:
					d["toolclass"] = "PICKAXES"
				elif values["tooltypeshovel"]:
					d["toolclass"] = "SHOVELS"
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
			if not len(values["dropcount"]):
				values["dropcount"] = "1"
			if values["dropself"]:
				d["droptype"] = "Self"
			elif values["dropfixed"]:
				if not len(dropitem):
					ErrorWindow("Item name must not be blank for fixed drop type.")
					continue
				d["droptype"] = "Item"
				d["drops"] = dropitem
				d["dropcount"] = values["dropcount"]
			elif values["dropfortunable"]:
				if not len(dropitem):
					ErrorWindow("Item name must not be blank for fixed drop type.")
					continue
				d["droptype"] = "Fortunable"
				d["drops"] = dropitem
				d["dropchances"] = values["dropcount"]
			else:
				d["droptype"] = "None"

			window.close()
			writeDictFile(fname, d)
			add_content(name, "block", d, mfd, fname)
			return d

def CreateItem(mfd):
	windowitems = [
		[sg.Text('Item Name'), sg.Input(key="itemname")],
		[sg.Text('Texture'), sg.Input(key="imgfile"),
			sg.FileBrowse(key="imgfile", file_types=(("PNG Files", "*.png"), ("All Files", "*.* *")), initial_folder=os.path.join(mfd["project_path"], mfd["mod.textures"]))
		],
		[sg.Ok(size=EDITOR_BUTTON_SIZE_WIDE), sg.Cancel(size=EDITOR_BUTTON_SIZE_WIDE)],
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
			img = GetImageAsPNG(values["imgfile"], mfd)
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
		manifest_dict["mc.names"] = blocks["names"]
		for block in blocks["content"]:
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

	if "mod.iconItem" in manifest_dict.keys() and not VerifyMCName(manifest_dict["mod.iconItem"]):
		item = manifest_dict["mod.iconItem"]
		if VerifyMCName(os.path.basename(item)):
			manifest_dict["mod.iconItem"] = os.path.basename(item)
		else:
			manifest_dict["mod.iconItem"] = None

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

def GetImageAsPNG(img, d):
	if not os.path.exists(img):
		ErrorWindow(f"Image file \"{img}\" doesn't exist or couldn't be opened.")
		return None
	if not os.path.normpath(img).startswith(os.path.normpath(os.path.join(d["project_path"], d["mod.textures"]))):
		newimg = os.path.normpath(os.path.join(d["project_path"], d["mod.textures"], os.path.basename(img)))
		shutil.copy(os.path.normpath(img), newimg)
		img = newimg
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

def sgScaledImage(fdir, fname=None, d=None, k=None, size=(32, 32)):
	if type(d) is dict:
		if k in d.keys():
			fname = d[k]
		else:
			fname = PLACEHOLDER_IMAGE_FILE
	if type(fname) is not str or not len(fname) or fname == "None":
		fname = PLACEHOLDER_IMAGE_FILE
	else:
		fname = os.path.join(fdir, fname)
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
		([sgScaledImage(os.path.join(manifest_dict["project_path"], manifest_dict["mod.textures"]), d=manifest_dict, k=f"mod.{content_type}.{name}.texture"),
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
			title, name, upper = ParseContentTitle(name)
			manifest_dict[f"mod.registry.{content_type}.names"].remove(old)
			manifest_dict[f"mod.registry.{content_type}.names"].append(name)
			fname = manifest_dict["mod.files"][f"{content_type}.{old}"]
			newname = os.path.join(os.path.dirname(fname), name+os.path.splitext(fname)[1])
			if os.path.exists(fname):
				os.rename(fname, newname)
			del manifest_dict["mod.files"][f"{content_type}.{old}"]
			manifest_dict["mod.files"][f"{content_type}.{name}"] = newname
			for key in list(manifest_dict.keys()):
				if key.startswith(f"mod.{content_type}.{old}"):
					# print(key, '-->', key.replace(f"mod.{content_type}.{old}", f"mod.{content_type}.{name}"))
					manifest_dict[key.replace(f"mod.{content_type}.{old}", f"mod.{content_type}.{name}")] = manifest_dict[key]
					del manifest_dict[key]
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
		[sgScaledImage(os.path.join(manifest_dict["project_path"], manifest_dict["mod.textures"]), d=manifest_dict, k=f"mod.item.{manifest_dict['mod.iconItem']}.texture"),
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
			item = ContentSelectWindow(manifest_dict, "item", vanillabutton=False)
			if item is None:
				continue
			manifest_dict["mod.iconItem"] = item
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
