
import os, sys, json, shutil

from _m3ec.actions import *
from _m3ec.gradle import *
from _m3ec.util import *

def interpret_args(argv):
	source_path = os.path.join(os.path.dirname(__file__), "data")
	if argv[0].lower() == "help":
		print("""Usage:
project_path all|fabric|forge[gameversion]|fabric[gameversion]
gen|generate manifest|item|food|fuel|block|fluid|sapling|ore|(shaped|shapeless|smelting|stonecutting|smithing)recipe|armor[material]|tool[material] [output_file]
""")
	elif len(argv) > 1:
		if argv[0].lower() in ("generate", "gen"):
			fname = os.path.join(source_path, "default_content_files", argv[1]+".m3ec")
			if os.path.exists(fname):
				with open(fname) as f:
					data = f.read()

				if len(argv) > 2:
					if "." in argv[2]:
						name = argv[2]
					else:
						name = argv[2]+".m3ec"
					if os.path.exists(name):
						if "n" in input("File exists. Replace? (y/n) ").lower():
							return
					cid = MCNameify(os.path.basename(name).rsplit(".", maxsplit=1)[0])
					data = data.replace("title:\n", f"title: {Titleify(cid)}\n").replace("texture:\n", f"texture: {cid}\n")
					if "material" in fname.lower():
						data = data.replace("contentid:\n", f"contentid: {Classify(cid)}\n")
					else:
						data = data.replace("contentid:\n", f"contentid: {cid}\n")
					try:
						with open(name, "w") as f:
							f.write(data)
					except IOError:
						print(f"Failed to write destination file: {argv[3]}")
				else:
					print(data)
		else:
			build(argv[0], argv[1:])

def build(project_path, modenv):
	if " " in modenv:
		modenv = modenv.split(" ")
	elif type(modenv) is not list:
		modenv = [modenv]
	source_path = os.path.join(os.path.dirname(__file__), "data")

	if not os.path.exists(project_path):
		print(f"\"{project_path}\" not found. Aborting.")
		return False

	manifest_file = os.path.join(project_path, "manifest.m3ec")
	if not os.path.exists(manifest_file):
		manifest_file = os.path.join(project_path, "manifest.txt")
		if not os.path.exists(manifest_file):
			print(f"Manifest file (manifest.m3ec/manifest.txt) not found in \"{project_path}\". Aborting.")
			return False

	if not os.path.isdir(project_path):
		project_path = os.path.dirname(project_path)

	mdc = readDictFile(manifest_file)
	mdc["manifest_file"] = manifest_file
	mdc["project_path"] = os.path.abspath(project_path)

	try:
		fname = os.path.join(source_path, "mc", "blocks.json")
		with open(fname) as f:
			blocks = json.load(f)
		for block in blocks["content"]:
			blockid = block["name"]
			for key in block.keys():
				if key != blockid:
					mdc[f"mc.{blockid}.{key}"] = block[key]
	except FileNotFoundError:
		print(f"Warning: data file \"{fname}\" not found!")

	prefix, modauthor, modclass = (getDictVal(mdc, k, manifest_file) for k in \
		["mod.prefix", "mod.author", "mod.class"])

	if "mod.package" not in mdc:
		mdc["mod.package"] = f"{prefix}.{modauthor}.{modclass}".lower()
	if "mod.mcpath" not in mdc:
		mdc["mod.mcpath"] = modclass.lower()

	mdc["mod.maven_group"] = f"{prefix}.{modauthor}".lower()


	modpath = mdc["mod.package"]
	modmcpath = mdc["mod.mcpath"]
	modmcpathdir = 	mdc["mod.packagedir"] = os.path.join(prefix, modauthor, modclass).lower()

	for k in ["credits", "description"]:
		if f"mod.{k}" not in mdc.keys():
			mdc[f"mod.{k}"] = ""

	if "mod.license" not in mdc.keys():
		print("--------------------WARNING---------------------\nMod license defaulting to \"All Rights Reserved\".\n\
Please specify your mod's license in its manifest file to avoid licensing confusion.\n\
Check the list of common licenses from https://choosealicense.com/ and choose the one that best fits your needs.\n\
------------------------------------------------\n")
		mdc["mod.license"] = "All Rights Reserved"

	if "mod.iconitem" not in mdc.keys():
		print("Warning: Icon item for custom creative tab unspecified. Defaulting to none.")

	mdc["default_source_path"] = source_path = os.path.join(os.path.dirname(__file__), "data")
	if "mod.sourcepath" in mdc.keys():
		source_path = mdc["mod.sourcepath"]

	mdc["source_path"] = source_path
	mdc["texture_templates"] = os.path.join(source_path, "common", "texture_templates")

	reserved_modenv_words = ["build", "buildjar", "runclient", "runserver"]

	mod_builds = {}
	for word in modenv:
		word = word.lower()
		if word not in reserved_modenv_words:
			try:
				loader, version = splitPrefix(word, 2)
			except:
				continue
			if len(loader) and len(version):
				mod_builds[word] = [loader, version]
			else:
				for s in try_load_resource(os.path.join(source_path, "versions"), word+".json", default=[]):
					try:
						loader, version = splitPrefix(s, 2)
					except:
						continue
					if len(loader) and len(version):
						mod_builds[str(loader)+str(version)] = [str(loader), str(version)]

	for loader, version in mod_builds.values():
		if os.path.isdir(os.path.join(source_path, loader+version)):
			build_mod(loader, version, modenv, mdc.copy())
		else:
			print(f"Failed to find build config for target \"{loader}\" version \"{version}\"")

	if not len(mod_builds.keys()):
		print("No valid build targets specified.")


def build_mod(modloader, version, modenv, mdc):
	content_types_list = ["item", "food", "fuel", "block", "fluid", "ore", "recipe", "armor", "tool",
		"armormaterial", "toolmaterial", "enchantment", "recipetype", "sapling"]
	print(f"\n\
\n\
-----------------------------------------------\n\
   Building {modloader} {version} mod project\n")

	mdc["modloader"] = modloader
	mdc["gameversion"] = gameversion = version
	try:
		_, mdc["gameversion.major"], mdc["gameversion.minor"] = (int(v) for v in version.split(".", maxsplit=2))
	except ValueError:
		_, mdc["gameversion.major"] = (int(v) for v in version.split(".", maxsplit=1))
		mdc["gameversion.minor"] = 0
	source_path = mdc["source_path"]
	project_path = mdc["project_path"]
	build_path = mdc["build_path"] = os.path.join(project_path, f"build/{modloader}{version}")
	make_dirs(build_path)

	# TODO: build stuff that needs to be in MainClass.java here

	# if "mod.ItemGroups.java" not in mdc:
		# mdc["mod.ItemGroups.java"] = ""
	# if "mod.ExtraOnInitialize.java" not in mdc:
		# mdc["mod.ExtraOnInitialize.java"] = ""

	mdc["mod.content_types"] = content_types_list
	for content_type in content_types_list:
		mdc[f"mod.registry.{content_type}.names"] = []

	mdc[f"mod.registry.blockitem.names"] = []
	mdc["mod.customclasses"] = []
	mdc["mod.registry.classes"] = []
	mdc[f"mod.files"] = {}

	for a in ["first", "pre", "resource", "post", "final"]:
		if f"{a}execactions" not in mdc.keys():
			mdc[f"{a}execactions"] = []

	for file in mdc["firstexecactions"]:
		mdc["curdir"] = mdc["project_path"]
		file = readf(file, mdc)
		try:
			with open(os.path.join(mdc["curdir"], file)) as f:
				j = json.load(f)
			execActions(j, mdc)
		except FileNotFoundError as e:
			print(f"Warning: file \"{file}\" listed in firstexecactions does not exist.")

	mdc["curdir"] = mdc["project_path"]

	for path in mdc["mod.paths"]:
		for fname in walk(os.path.normpath(os.path.join(mdc["project_path"], path))):
			if fname.endswith(".txt") or fname.endswith(".m3ec") or fname.endswith(".json"):
				dlist = readDictFile(fname, md=mdc)
				if type(dlist) is not dict:
					continue
				if "@iterate" not in dlist.keys():
					dlist = {"@iterate": [dlist]}
				for d in dlist["@iterate"]:
					if "@" in d.keys():
						content_type = d["@"]
						if content_type == "class":
							d2 = {"file":d["file"], "class":d["class"]}
							if "modloaders" in d.keys():
								d2["modloaders"] = d["modloaders"]
							if "gameversions" in d.keys():
								d2["gameversions"] = d["gameversions"]
							mdc["mod.customclasses"].append(d2)
							mdc["mod.registry.classes"].append(d["class"])
							continue
						elif content_type == "itemfactory":
							for cid in d["items"]:
								dictinst = {"item":d["type"], "title":" ".join([w.capitalize() for w in cid.split("_")]), "texture":cid+".png"}
								add_content(cid, "item", dictinst, mdc, fname)
							continue
						if "contentid" not in d.keys():
							if "cid" in d.keys():
								d["contentid"] = d["cid"]
							else:
								print(f"Warning: Skipping file \"{fname}\" due to missing contentid.")
								continue
						if content_type == "recipe":
							if "contentid" in d.keys():
								cid = d["contentid"]
							else:
								cid = os.path.splitext(os.path.split(fname)[-1])[0]
							add_content(cid, content_type, d, mdc, fname)
						else:
							if "contentid" in d.keys():
								cid = d["contentid"]
								if content_type == "block":
									if "blockstatetype" not in d.keys():
										d["blockstatetype"] = "Single"
									if "blockclass" not in d.keys():
										d["blockclass"] = "Block"
								# print(f"adding {content_type} {cid}")
								add_content(cid, content_type, d, mdc, fname)
							copied_d = d.copy()
							if content_type == "block":
								midcid = mdc["mod.mcpath"]+":"+cid

								if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.wall"):
									copied_d["title"] = d["title"]+" Wall"
									copied_d["drops"] = copied_d["contentid"] = cid+"_wall"
									copied_d["droptype"] = "Self"
									copied_d["blockstatetype"] = "Wall"
									copied_d["texture_bottom"] = copied_d["texture_top"] = copied_d["texture_side"] = d["texture"]
									copied_d["blockclass"] = "WallBlock"
									add_content(cid+"_wall", content_type, copied_d, mdc)
									if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.wall.recipe"):
										add_content(cid+"_wall", "recipe", {
											"@": "recipe", "recipe": "ShapedRecipe",
											"pattern": ['"###"','"###"'], "items": [midcid], "itemkeys": ["#"], "itemkeys.list.0": "#",
											"result": midcid+"_wall", "count": "6",
										}, mdc)
									if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.wall.stonecuttingrecipe"):
										add_content(cid+"_wall_stonecutter", "recipe", {
											"@": "recipe", "recipe": "StoneCuttingRecipe",
											"ingredient": midcid, "result": midcid+"_wall", "count": "1",
										}, mdc)
								if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.slab"):
									copied_d["title"] = d["title"]+" Slab"
									copied_d["drops"] = copied_d["contentid"] = cid+"_slab"
									copied_d["droptype"] = "Slab"
									copied_d["blockstatetype"] = "Slab"
									copied_d["texture_bottom"] = copied_d["texture_top"] = copied_d["texture_side"] = d["texture"]
									copied_d["blockclass"] = "SlabBlock"
									add_content(cid+"_slab", content_type, copied_d, mdc)
									if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.slab.recipe"):
										add_content(cid+"_slab", "recipe", {
											"@": "recipe", "recipe": "ShapedRecipe",
											"pattern": ['"###"'], "items": [midcid], "itemkeys": ["#"], "itemkeys.list.0": "#",
											"result": midcid+"_slab", "count": "6",
										}, mdc)
									if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.slab.stonecuttingrecipe"):
										add_content(cid+"_slab_stonecutter", "recipe", {
											"@": "recipe", "recipe": "StoneCuttingRecipe",
											"ingredient": midcid, "result": midcid+"_slab", "count": "2",
										}, mdc)
								if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.stairs"):
									copied_d["title"] = d["title"]+" Stairs"
									copied_d["drops"] = copied_d["contentid"] = cid+"_stairs"
									copied_d["droptype"] = "Self"
									copied_d["blockstatetype"] = "Stair"
									copied_d["texture_bottom"] = copied_d["texture_top"] = copied_d["texture_side"] = d["texture"]
									copied_d["blockclass"] = "ModStairBlock"
									copied_d["blockmaterialblock"] = cid
									copied_d["blockclass.isstair"] = "true"
									add_content(cid+"_stairs", content_type, copied_d, mdc)
									if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.stairs.recipe"):
										add_content(cid+"_stairs", "recipe", {
											"@": "recipe", "recipe": "ShapedRecipe",
											"pattern": ['"#  "', '"## "', '"###"'], "items": [midcid], "itemkeys": ["#"],"itemkeys.list.0": "#",
											"result": midcid+"_stairs", "count": "4",
										}, mdc)
										add_content(cid+"_stairs_reversed", "recipe", {
											"@": "recipe", "recipe": "ShapedRecipe",
											"pattern": ['"  #"', '" ##"', '"###"'], "items": [midcid], "itemkeys": ["#"], "itemkeys.list.0": "#",
											"result": midcid+"_stairs", "count": "4",
										}, mdc)
									if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.stairs.stonecuttingrecipe"):
										add_content(cid+"_stairs_stonecutter", "recipe", {
											"@": "recipe", "recipe": "StoneCuttingRecipe",
											"ingredient": midcid, "result": midcid+"_stairs", "count": "1",
										}, mdc)
								if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.trapdoor"):
									copied_d["title"] = d["title"]+" Trapdoor"
									copied_d["drops"] = copied_d["contentid"] = cid+"_trapdoor"
									copied_d["droptype"] = "Self"
									copied_d["blockstatetype"] = "Trapdoor"
									copied_d["texture_bottom"] = copied_d["texture_top"] = copied_d["texture_side"] = d["texture"]
									copied_d["blockclass"] = "ModTrapdoorBlock"
									add_content(cid+"_trapdoor", content_type, copied_d, mdc)
									if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.trapdoor.recipe"):
										add_content(cid+"_trapdoor", "recipe", {
											"@": "recipe", "recipe": "ShapedRecipe",
											"pattern": ['"###"', '"###"'], "items": [midcid], "itemkeys": ["#"], "itemkeys.list.0": "#",
											"result": midcid+"_trapdoor", "count": "2",
										}, mdc)
									if checkDictKeyTrue(mdc, f"mod.{content_type}.{cid}.autogenerate.trapdoor.stonecuttingrecipe"):
										add_content(cid+"_slab_stonecutter", "recipe", {
											"@": "recipe", "recipe": "StoneCuttingRecipe",
											"ingredient": midcid, "result": midcid+"_trapdoor", "count": "1",
										}, mdc)
					else:
						print(f"Warning: Skipping file \"{fname}\" due to missing content type.")

		# print(f"{key}: {mdc[key]}")

	if modloader in mdc.keys():
		for f in mdc[modloader]:
			readDictFile(f, mdc, mdc)

	if version in mdc.keys():
		for f in mdc[version]:
			readDictFile(f, mdc, mdc)

	if modloader+version in mdc.keys():
		for f in mdc[modloader+version]:
			readDictFile(f, mdc, mdc)

	# clean up old built files if they exist
	# if os.path.exists(os.path.join(build_path, "src")):
		# shutil.rmtree(os.path.join(build_path, "src"))
	try:
		with open(os.path.join(build_path, "m3ec_cache.json")) as f:
			PREV_WRITTEN_FILES = json.load(f)
	except FileNotFoundError:
		PREV_WRITTEN_FILES = []
	except IOError:
		PREV_WRITTEN_FILES = None

	if type(PREV_WRITTEN_FILES) is not list:
		print("Found invalid m3ec_cache.json in build directory, ignoring it.")
		PREV_WRITTEN_FILES = []

	for fname in PREV_WRITTEN_FILES:
		try:
			os.remove(fname)
		except IOError:
			pass

	WRITTEN_FILES_LIST.clear()

	try:
		with open(os.path.join(source_path, f"{modloader}{version}", "m3ec_build.json")) as f:
			versionbuilder = json.load(f)
	except FileNotFoundError:
		print(f"Warning: {modloader} {version} is not yet implemented; skipping build.")
		return False

	if "implementedFeatures" in versionbuilder.keys():
		impl = versionbuilder["implementedFeatures"]
		missing_features = False
		for content_type in content_types_list:
			if len(mdc[f"mod.registry.{content_type}.names"]):
				if content_type not in impl:
					if not missing_features:
						print(f"-----------------------------------------------\n   [!] Content Type Build Warnings [!]\n-----------------------------------------------")
					print(f"\nContent type {content_type} may not be fully implemented if at all for {modloader} {version}\n  {content_type} content will most likely not be present in the build.")
					missing_features = True
		if missing_features:
			print(f"\n-----------------------------------------------\n   End of Content Type Build Warnings\n-----------------------------------------------\n")

	for file in mdc["preexecactions"]:
		file = readf(file, mdc)
		try:
			with open(os.path.join(mdc["curdir"], file)) as f:
				j = json.load(f)
			execActions(j, mdc)
		except FileNotFoundError:
			print(f"Warning: file \"{file}\" listed in preexecactions does not exist.")

	if "firstActions" in versionbuilder.keys():
		execActions(versionbuilder["firstActions"], mdc)

	build_resources(project_path, f"{modloader}{version}", mdc)

	for file in mdc["resourceexecactions"]:
		file = readf(file, mdc)
		try:
			with open(os.path.join(mdc["curdir"], file)) as f:
				j = json.load(f)
			execActions(j, mdc)
		except FileNotFoundError:
			print(f"Warning: file \"{file}\" listed in resourceexecactions does not exist.")

	if "preActions" in versionbuilder.keys():
		execActions(versionbuilder["preActions"], mdc)
	
	if "sources" in versionbuilder.keys():
		for file in versionbuilder["sources"]:
			source, dest = file["source"], file["dest"]
			mandatory = True
			if "optional" in file.keys():
				if file["optional"]:
					mandatory = False
			if "iterate" in file.keys():
				for i in range(len(mdc[file["iterate"]])):
					mdc["%i"] = i
					mdc["%v"] = mdc[file["iterate"]][i]
					
					rv = readf_copyfile(os.path.join(source_path, f"{modloader}{version}", readf(source, mdc)), os.path.join(build_path, readf(dest, mdc)), mdc)
					if mandatory and not rv:
						print(f"Error: Failed to read source file \"{modloader}{version}/{source}\"")
						return False
			else:
				rv = readf_copyfile(os.path.join(source_path, f"{modloader}{version}", readf(source, mdc)), os.path.join(build_path, readf(dest, mdc)), mdc)
				if mandatory and not rv:
					print(f"Error: Failed to read source file \"{modloader}{version}/{source}\"")
					return False

	if "copy" in versionbuilder.keys():
		for file in versionbuilder["copy"]:
			shutil.copy(file["source"], file["dest"])

	if "mod.customclasses" in mdc.keys():
		for customclass in mdc["mod.customclasses"]:
			if "modloaders" in customclass.keys():
				if modloader not in customclass["modloaders"]:
					continue
			if "gameversions" in customclass.keys():
				if gameversion not in customclass["gameversions"]:
					continue
			fname = readf(customclass["file"], mdc)
			if not readf_copyfile(os.path.join(project_path, fname), os.path.join(build_path, "src", "main", "java", readf(customclass["class"], mdc).replace(".", os.sep)+".java"), mdc):
				print(f"Error: Failed to copy custom class file \"{fname}\"")
				return False

	if "mod.customfiles" in mdc.keys():
		# print(mdc["mod.customfiles"])
		for file in mdc["mod.customfiles"]:
			# print(file)
			source, dest = file.split(" ", maxsplit=1)
			if " " in dest:
				dest, ml = file.split(" ", maxsplit=1)
				if " " in ml:
					ml, gv = ml.split(" ", maxsplit=1)
					if gameversion not in gv:
						continue
				if modloader not in ml:
					continue
			# print(source, "-->", dest)
			if not readf_copyfile(os.path.join(project_path, source), os.path.join(build_path, readf(dest, mdc)), mdc):
				print(f"Error: Failed to copy custom file \"{source}\"")
				return False
	
	if getDictValF(mdc, "build.build_tags_and_lang", True):
		build_tags_and_lang(mdc)

	if "postActions" in versionbuilder.keys():
		execActions(versionbuilder["postActions"], mdc)

	for file in mdc["postexecactions"]:
		file = readf(file, mdc)
		try:
			with open(os.path.join(mdc["curdir"], file)) as f:
				j = json.load(f)
			execActions(j, mdc)
		except FileNotFoundError:
			print(f"Warning: file \"{file}\" listed in postexecactions does not exist.")

	if "javaVersion" in versionbuilder.keys():
		maybe_run_gradle(build_path, modenv, versionbuilder["javaVersion"], mdc)

	if "finalActions" in versionbuilder.keys():
		execActions(versionbuilder["finalActions"], mdc)

	with open(os.path.join(build_path, "m3ec_cache.json"), "w") as f:
		json.dump(WRITTEN_FILES_LIST, f)

	for file in mdc["finalexecactions"]:
		file = readf(file, mdc)
		try:
			with open(os.path.join(mdc["curdir"], file)) as f:
				j = json.load(f)
			execActions(j, mdc)
		except FileNotFoundError:
			print(f"Warning: file \"{file}\" listed in finalexecactions does not exist.")

	return True

def build_resources(project_path, builddir, mdc):
	if getDictValF(mdc, "build.custom_build_resources_step", False):
		return
	source_path = os.path.join(os.path.dirname(__file__), "data")
	src = os.path.join(source_path, builddir, "gradle")
	commons_path = os.path.join(source_path, "common")
	modmcpath = mdc["mod.mcpath"]
	sourcesdir = os.path.join(source_path, builddir)
	dest = builddir = mdc["build_path"]
	block_models_assets_dir = getDictValF(mdc, "asset_paths.block.model", os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "models", "block"))
	blockstates_assets_dir = getDictValF(mdc, "asset_paths.block.state", os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "blockstates"))
	item_models_assets_dir = getDictValF(mdc, "asset_paths.item.model", os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "models", "item"))
	# because they decided to change pluralization I guess
	if mdc["version_past_1.19.3"]:
		block_textures_assets_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "textures", "block")
		item_textures_assets_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "textures", "item")
	else:
		block_textures_assets_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "textures", "blocks")
		item_textures_assets_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "textures", "items")

	block_textures_assets_dir = getDictValF(mdc, "asset_paths.block.texture", block_textures_assets_dir)
	item_textures_assets_dir = getDictValF(mdc, "asset_paths.item.texture", item_textures_assets_dir)
	lang_dir = getDictValF(mdc, "asset_paths.lang", os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "lang"))
	build_data_dir = getDictValF(mdc, "build_paths.data", os.path.join(builddir, "src", "main", "resources", "data"))
	
	loot_table_dir = getDictValF(mdc, "build_paths.data.loot_table", os.path.join(builddir, "src", "main", "resources", "data", modmcpath, "loot_tables"))
	block_loot_table_dir = getDictValF(mdc, "build_paths.data.loot_table.block", os.path.join(loot_table_dir, "blocks"))

	if "build.gradlewrapper" in mdc.keys():
		gradlesrc = mdc["build.gradlewrapper"]
	else:
		gradlesrc = os.path.join(source_path, "gradle")

	
	if getDictValF(mdc, "build.uses_gradle", True):
		make_dir(dest)
		make_dir(os.path.join(dest, "gradle"))
		make_dir(os.path.join(dest, "gradle", "wrapper"))
		copy_file(os.path.join(gradlesrc, "gradle", "wrapper", "gradle-wrapper.jar"), os.path.join(dest, "gradle", "wrapper", "gradle-wrapper.jar"))
		copy_file(os.path.join(gradlesrc, "gradle", "wrapper", "gradle-wrapper.properties"), os.path.join(dest, "gradle", "wrapper", "gradle-wrapper.properties"))
		copy_file(os.path.join(gradlesrc, "gradlew"), os.path.join(dest, "gradlew"))
		copy_file(os.path.join(gradlesrc, "gradlew.bat"), os.path.join(dest, "gradlew.bat"))
		if os.path.exists(os.path.join(src, "settings.gradle")):
			copy_file(os.path.join(src, "settings.gradle"), os.path.join(dest, "settings.gradle"))
		create_file(os.path.join(dest, "gradle.properties"), readf_file(os.path.join(src, "gradle.properties"), mdc))
		create_file(os.path.join(dest, "build.gradle"), readf_file(os.path.join(src, "build.gradle"), mdc))

	if getDictValF(mdc, "build.standard_java_project", True):
		make_dir(os.path.join(dest, "src"))
		make_dir(os.path.join(dest, "src", "main"))
		make_dir(os.path.join(dest, "src", "main", "resources"))
		make_dir(os.path.join(dest, "src", "main", "resources", "assets"))
		make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath))
		make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "blockstates"))
		make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "lang"))
		make_dir(os.path.dirname(block_models_assets_dir))
		make_dir(block_models_assets_dir)
		make_dir(item_models_assets_dir)
		make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "textures"))
		make_dir(block_textures_assets_dir)
		make_dir(item_textures_assets_dir)
		make_dir(os.path.join(dest, "src", "main", "resources", "data"))
		make_dir(os.path.join(dest, "src", "main", "resources", "data", modmcpath))
		make_dir(os.path.join(dest, "src", "main", "java"))
		if "mod.icon" in mdc.keys():
			if "forge" in mdc["modloader"]:
				copy_file(os.path.join(project_path, mdc["mod.icon"]), os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "icon.png"))
			else:
				copy_file(os.path.join(project_path, mdc["mod.icon"]), os.path.join(dest, "src", "main", "resources", "icon.png"))
			

		prefix = mdc["mod.prefix"]
		modauthor = mdc["mod.author"]
		modmcpathdir = os.path.join(prefix, modauthor.lower(), mdc["mod.class"].lower())
		make_dir(os.path.join(dest, "src", "main", "java", prefix))
		make_dir(os.path.join(dest, "src", "main", "java", prefix, modauthor.lower()))
		make_dir(os.path.join(dest, "src", "main", "java", modmcpathdir))
		make_dir(os.path.join(dest, "src", "main", "java", modmcpathdir, "registry"))

	make_dir(loot_table_dir)
	make_dir(block_loot_table_dir)
	make_dir(getDictValF(mdc, "build_paths.data.loot_table.chest", os.path.join(loot_table_dir, "chests")))
	make_dir(getDictValF(mdc, "build_paths.data.loot_table.entity", os.path.join(loot_table_dir, "entities")))
	make_dir(getDictValF(mdc, "build_paths.data.loot_table.gameplay", os.path.join(loot_table_dir, "gameplay")))

	if getDictValF(mdc, "build.build_recipe_json", True):
		recipes_dir = getDictValF(mdc, "build_paths.data.recipe", os.path.join(builddir, "src", "main", "resources", "data", modmcpath, "recipes"))
		make_dir(recipes_dir)
	else:
		recipes_dir = None

	langdict = {"en_us":{}}
	tagdict = {}
	blocktagdict = {}
	mdc[f"mod.registry.blockitem.names"].clear()

	includedClasses = []
	for content_type in mdc["mod.content_types"]:
		for cid in mdc[f"mod.registry.{content_type}.names"]:
			nscid = mdc["mod.mcpath"]+":"+cid.lower()
			tname = mdc[f"mod.{content_type}.{cid}.{content_type}"]
			# print(cid, content_type, tname)
			# print(mdc[f"mod.{content_type}.{cid}.keys"])
			mdc["contentid"] = mdc["cid"] = cid
			keys_to_remove_later = []
			for key in mdc[f"mod.{content_type}.{cid}.keys"]:
				k = f"mod.{content_type}.{cid}.{key}"
				if k in mdc.keys():
					mdc[key] = mdc[k]
					keys_to_remove_later.append(key)
			
			if "texture" in mdc.keys():
				if "." in mdc["texture"]:
					mdc["texture"], ext = os.path.splitext(mdc["texture"])

			if content_type in ["item", "food", "armor", "tool"]:
				copy_textures(content_type, cid, mdc, project_path, item_textures_assets_dir)
				create_file(os.path.join(item_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "item_models", tname+".m3ecjson"), mdc))

			if content_type == "block":
				mdc[f"mod.registry.blockitem.names"].append(cid)
				mdc[f"mod.blockitem.{cid}.uppercased"] = cid.upper()
				copy_textures(content_type, cid, mdc, project_path, block_textures_assets_dir)
				if "blockstatetype" in mdc.keys():
					statename = mdc["blockstatetype"]
				else:
					statename = "Single"
				create_file(os.path.join(item_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "item_models", "BlockItem.m3ecjson"), mdc))
				create_file(os.path.join(blockstates_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "blockstates", statename+".m3ecjson"), mdc))
				if statename == "3Axis":
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_models", tname+".m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+"_side.json"), readf_file(os.path.join(commons_path, "block_models", tname+"_side.m3ecjson"), mdc))
				elif statename == "Slab":
					create_file(os.path.join(block_models_assets_dir, cid+"_double.json"), readf_file(os.path.join(commons_path, "block_models", "SimpleBlock.m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_models", statename+".m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+"_top.json"), readf_file(os.path.join(commons_path, "block_models", statename+"_top.m3ecjson"), mdc))
				elif statename == "Stair":
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_models", "Stair.m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+"_inner.json"), readf_file(os.path.join(commons_path, "block_models", statename+"_inner.m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+"_outer.json"), readf_file(os.path.join(commons_path, "block_models", statename+"_outer.m3ecjson"), mdc))
				elif statename == "Trapdoor":
					create_file(os.path.join(block_models_assets_dir, cid+"_bottom.json"), readf_file(os.path.join(commons_path, "block_models", "Trapdoor_bottom.m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+"_open.json"), readf_file(os.path.join(commons_path, "block_models", "Trapdoor_open.m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+"_top.json"), readf_file(os.path.join(commons_path, "block_models", "Trapdoor_top.m3ecjson"), mdc))
				elif statename == "Wall":
					create_file(os.path.join(block_models_assets_dir, cid+"_inventory.json"), readf_file(os.path.join(commons_path, "block_models", "Wall_inventory.m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+"_post.json"), readf_file(os.path.join(commons_path, "block_models", "Wall_post.m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+"_side.json"), readf_file(os.path.join(commons_path, "block_models", "Wall_side.m3ecjson"), mdc))
					create_file(os.path.join(block_models_assets_dir, cid+"_side_tall.json"), readf_file(os.path.join(commons_path, "block_models", "Wall_side_tall.m3ecjson"), mdc))
				else:
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_models", tname+".m3ecjson"), mdc))
				dtype = mdc[f"mod.{content_type}.{cid}.droptype"]
				if dtype.lower() != "none":
					create_file(os.path.join(block_loot_table_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_loot_tables", dtype+".m3ecjson"), mdc))
				if "forge" in mdc["modloader"]:
					if mdc[f"mod.block.{cid}.toolclass"] in ["AXES", "HOES", "PICKAXES", "SHOVELS"]:
						mdc[f"mod.block.{cid}.toolclass"] = mdc[f"mod.block.{cid}.toolclass"][:-1]
					if mdc[f"mod.block.{cid}.material"] == "SOIL":
						mdc[f"mod.block.{cid}.material"] = "DIRT"
				elif "fabric" in mdc["modloader"]:
					if mdc[f"mod.block.{cid}.toolclass"] in ["AXE", "HOE", "PICKAXE", "SHOVEL"]:
						mdc[f"mod.block.{cid}.toolclass"] = mdc[f"mod.block.{cid}.toolclass"]+"S"
					if mdc[f"mod.block.{cid}.material"] == "DIRT":
						mdc[f"mod.block.{cid}.material"] = "SOIL"
				if not mdc[f"mod.block.{cid}.toollevel"].isnumeric():
					mdc[f"mod.block.{cid}.toollevelstring"] = "MiningLevels." + mdc[f"mod.block.{cid}.toollevel"]
					if mdc[f"mod.block.{cid}.toollevel"] in ["WOOD", "STONE", "IRON", "DIAMOND", "NETHERITE"]:
						mdc[f"mod.block.{cid}.toollevelint"] = str(["WOOD", "STONE", "IRON", "DIAMOND", "NETHERITE"].index(mdc[f"mod.block.{cid}.toollevel"]))
					else:
						mdc[f"mod.block.{cid}.toollevelint"] = "0"
				else:
					mdc[f"mod.block.{cid}.toollevelstring"] = mdc[f"mod.block.{cid}.toollevel"]
					mdc[f"mod.block.{cid}.toollevelint"] = mdc[f"mod.block.{cid}.toollevel"]
				# print(mdc[f"mod.block.{cid}.toollevelstring"], mdc[f"mod.block.{cid}.toollevelint"])

			if recipes_dir is not None and content_type == "recipe":
				create_file(os.path.join(recipes_dir, cid+".json"), readf_file(os.path.join(commons_path, "recipes", tname+".m3ecjson"), mdc))
			if content_type in ["item", "block", "food", "armor", "tool"]:
				if "langs" in mdc[f"mod.{content_type}.{cid}.keys"]:
					for lang in mdc[f"mod.{content_type}.{cid}.langs"]:
						if lang not in langdict.keys():
							langdict[lang] = {}
						langdict[lang][f"{content_type}.{modmcpath}.{cid}"] = mdc[f"mod.{content_type}.{cid}.{lang}"]
				if content_type in ["food", "armor", "tool"]:
					content_type_mc = "item"
				else:
					content_type_mc = content_type
				langdict["en_us"][f"{content_type_mc}.{modmcpath}.{cid}"] = mdc[f"mod.{content_type}.{cid}.title"]

			if content_type in ["block", "item", "food", "armor", "tool"]:
				if "itemtags" in mdc[f"mod.{content_type}.{cid}.keys"]:
					if type(mdc[f"mod.{content_type}.{cid}.itemtags"]) is list:
						for tag in mdc[f"mod.{content_type}.{cid}.itemtags"]:
							if tag in tagdict.keys():
								tagdict[tag].append(nscid)
							else:
								tagdict[tag] = [nscid]
					else:
						for tag in mdc[f"mod.{content_type}.{cid}.itemtags"].split(" "):
							if tag in tagdict.keys():
								tagdict[tag].append(nscid)
							else:
								tagdict[tag] = [nscid]

			if content_type in ["block"]:
				if "blocktags" in mdc[f"mod.{content_type}.{cid}.keys"]:
					if type(mdc[f"mod.{content_type}.{cid}.blocktags"]) is list:
						for tag in mdc[f"mod.{content_type}.{cid}.blocktags"]:
							if tag in blocktagdict.keys():
								blocktagdict[tag].append(nscid)
							else:
								blocktagdict[tag] = [nscid]
					else:
						for tag in mdc[f"mod.{content_type}.{cid}.blocktags"].split(" "):
							if tag in blocktagdict.keys():
								blocktagdict[tag].append(nscid)
							else:
								blocktagdict[tag] = [nscid]

			if "customclass" in mdc.keys():
				mdc[f"mod.{content_type}.{cid}.customclass"] = mdc["customclass"]
				# print(f"Custom class {mdc['customclass']} for {content_type} {cid}")
			elif content_type in ["item", "food", "armor", "tool"]:
				mdc[f"mod.{content_type}.{cid}.customclass"] = "Item"
			
			for k in keys_to_remove_later:
				del mdc[k]


	if "mod.langs" in mdc.keys():
		for lang in mdc["mod.langs"]:
			if lang not in langdict.keys():
				langdict[lang] = {}
			langdict[lang][f"itemGroup.{modmcpath}.general"] = mdc[f"mod.{lang}"]
			langdict[lang][f"itemGroup.{modmcpath}tab"] = mdc[f"mod.{lang}"]
	langdict["en_us"][f"itemGroup.{modmcpath}.general"] = mdc["mod.title"]
	langdict["en_us"][f"itemGroup.{modmcpath}tab"] = mdc["mod.title"]

	mdc["langdict"] = langdict
	mdc["tagdict"] = tagdict
	mdc["blocktagdict"] = blocktagdict


def build_tags_and_lang(mdc):
	langdict = mdc["langdict"]
	tagdict = mdc["tagdict"]
	blocktagdict = mdc["blocktagdict"]

	if "mod.extralangentries" in mdc:
		for lang in mdc["mod.extralangentries"]:
			ldk = f"mod.extralangentries.{lang}"
			if ldk in mdc.keys():
				for item in mdc[ldk]:
					key, value = [s.strip(" \t") for s in item.split(":", maxsplit=1)]
					langdict[lang][key] = value

	if "mod.itemtags" in mdc:
		for tag in mdc["mod.itemtags"]:
			if tag in mdc:
				fulltag = ":".join(tag.split("/", maxsplit=1))
				if fulltag not in tagdict.keys():
					tagdict[fulltag] = []
				for cid in mdc[tag]:
					t, cid = cid.split(":", maxsplit=1)
					if "item" in t:
						tagdict[fulltag].append(readf(cid, mdc))

	if "mod.blocktags" in mdc:
		for tag in mdc["mod.blocktags"]:
			if tag in mdc:
				fulltag = ":".join(tag.split("/", maxsplit=1))
				if fulltag not in blocktagdict.keys():
					blocktagdict[fulltag] = []
				for cid in mdc[tag]:
					t, cid = cid.split(":", maxsplit=1)
					if "block" in t:
						blocktagdict[fulltag].append(readf(cid, mdc))

	lang_dir = os.path.join(mdc["build_path"], "src", "main", "resources", "assets", mdc["mod.mcpath"], "lang")
	build_data_dir = os.path.join(mdc["build_path"], "src", "main", "resources", "data")

	for lang in langdict.keys():
		with open(os.path.join(lang_dir, lang+".json"),"w") as f:
			json.dump(langdict[lang], f)

	plural = not ("version_past_1.21" in mdc and mdc["version_past_1.21"])

	for tag in tagdict.keys():
		if ":" in tag:
			ns, t = tag.split(":")
		else:
			print(f"Error: tags should always be namespaced. Example: \"c:ingots\"\nBad tag: \"{tag}\"")
			exit(1)
		mdc["%namespace"] = ns
		tag_item_dir = getDictValF(mdc, "build_paths.data.tag.item", os.path.join(build_data_dir, ns, "tags", "items"))
		make_dir(os.path.dirname(os.path.join(tag_item_dir, t)))
		with open(os.path.join(tag_item_dir, t+".json"), "w") as f:
			json.dump({"replace": False, "values": tagdict[tag]}, f)

	for tag in blocktagdict.keys():
		if ":" in tag:
			ns, t = tag.split(":")
		else:
			print(f"Error: tags should always be namespaced. Example: \"c:ingots\"\nBad tag: \"{tag}\"")
			exit(1)
		mdc["%namespace"] = ns
		tag_block_dir = getDictValF(mdc, "build_paths.data.tag.block", os.path.join(build_data_dir, ns, "tags", "blocks"))
		make_dir(os.path.dirname(os.path.join(tag_block_dir, t)))
		with open(os.path.join(tag_block_dir, t+".json"), "w") as f:
			json.dump({"replace": False, "values": blocktagdict[tag]}, f)


def copy_textures(content_type, cid, mdc, project_path, dest_dir):
	project_tex_path = os.path.join(project_path, mdc["mod.textures"])
	# print(project_tex_path)
	for side in ["", "_top", "_bottom", "_side", "_front", "_back"]:
		if f"mod.{content_type}.{cid}.texture{side}" in mdc.keys():
			tex, ext = os.path.splitext(mdc[f"mod.{content_type}.{cid}.texture{side}"])
			copy_file(os.path.join(project_tex_path, tex)+".png", os.path.join(dest_dir, os.path.basename(tex))+".png")
			mdc[f"texture{side}"] = texture_pathify(mdc, tex, content_type, cid)
			if os.path.exists(os.path.join(project_tex_path, tex)+".png.mcmeta"):
				copy_file(os.path.join(project_tex_path, tex)+".png.mcmeta", os.path.join(dest_dir, os.path.basename(tex))+".png.mcmeta")


if __name__=='__main__':
	if len(sys.argv) < 2:
		print("""
Minecraft Multiple Mod Environment Compiler v0.10
Usage:
	python m3ec.py path modenv
where modenv can be any combination of:
+ all
+ 1.16.5
+ 1.17
+ 1.17.1
+ 1.18
+ 1.18.1
+ 1.18.2
+ 1.19
+ 1.19.2
+ forge
+ forge1.16.5
+ forge1.18.1
+ forge1.18.2
+ forge1.19
+ forge1.19.2
+ forge1.20.1
+ fabric
+ fabric1.17
+ fabric1.17.1
+ fabric1.18
+ fabric1.18.1
+ fabric1.18.2
+ fabric1.19
+ fabric1.19.2
+ fabric1.19.3
+ fabric1.19.4
+ fabric1.20.1

Note: Not all the game versions/modloaders listed are implemented to the same degree.
      If a feature is present in your mod that is not yet supported by the version/modloader implementation,
	  those features will be skipped. Some will print a warning to the console.

Additionally, modenv may be appended with any combination of:
+ buildjar (builds mod into a jar file)
+ runclient (launches an offline client with the mod installed)
+ runserver (launches an offline server with the mod installed)

---------------------------------------------------------------------
--  interactive build prompt                                       --
--  input "quit" to quit, "help" for help.                         --
--  usage: path modenv                                             --
---------------------------------------------------------------------
""")
		while True:
			d = input("m3ec> ").split(" ")
			if len(d):
				if d[0] in ["exit", "quit", "e", "q", "x"]:
					break
				interpret_args(d)
	else:
		interpret_args(sys.argv[1:])


