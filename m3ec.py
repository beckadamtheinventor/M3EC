
import os, sys, json, subprocess, shutil

def build(project_path, modenv):
	if " " in modenv:
		modenv = modenv.split(" ")
	else:
		modenv = [modenv]
	content_types_list = ["item", "food", "fuel", "block", "ore", "recipe", "armor", "tool", "armormaterial", "toolmaterial", "enchantment"]
	source_path = os.path.join(os.path.dirname(__file__),"sources")

	if not os.path.exists(project_path):
		print(f"Manifest file \"{project_path}\" not found. Aborting.")

	manifest_file = os.path.join(project_path, "manifest.m3ec")
	if not os.path.exists(manifest_file):
		manifest_file = os.path.join(project_path, "manifest.txt")
		if not os.path.exists(manifest_file):
			print(f"Manifest file (manifest.m3ec/manifest.txt) not found in \"{project_path}\". Aborting.")

	if not os.path.isdir(project_path):
		project_path = os.path.dirname(project_path)

	manifest_dict = readDictFile(manifest_file)

	manifest_dict["manifest_file"] = manifest_file
	manifest_dict["project_path"] = project_path

	try:
		fname = os.path.join(source_path, "mc", "blocks.json")
		with open(fname) as f:
			blocks = json.load(f)
		for block in blocks:
			blockid = block["name"]
			for key in block.keys():
				if key != blockid:
					manifest_dict[f"mc.{blockid}.{key}"] = block[key]
	except FileNotFoundError:
		print(f"Warning: data file \"{fname}\" not found!")

	prefix, modauthor, modclass = (getDictVal(manifest_dict, k, manifest_file) for k in \
		["mod.prefix", "mod.author", "mod.class"])

	if "mod.package" not in manifest_dict:
		manifest_dict["mod.package"] = f"{prefix}.{modauthor}.{modclass}".lower()
	if "mod.mcpath" not in manifest_dict:
		manifest_dict["mod.mcpath"] = modclass.lower()

	manifest_dict["mod.maven_group"] = f"{prefix}.{modauthor}".lower()


	modpath = manifest_dict["mod.package"]
	modmcpath = manifest_dict["mod.mcpath"]
	modmcpathdir = 	manifest_dict["mod.packagedir"] = os.path.join(prefix, modauthor, modclass).lower()

	for k in ["credits", "description"]:
		if f"mod.{k}" not in manifest_dict.keys():
			manifest_dict[f"mod.{k}"] = ""

	if "mod.license" not in manifest_dict.keys():
		print("--------------------WARNING---------------------\nMod license defaulting to \"All Rights Reserved\".\n\
Please specify your mod's license in its manifest file to avoid licensing confusion.\n\
Check the list of common licenses from https://choosealicense.com/ and choose the one that best fits your needs.\n\
------------------------------------------------\n")
		manifest_dict["mod.license"] = "All Rights Reserved"

	if "mod.iconItem" not in manifest_dict.keys():
		print("Warning: Icon item for custom creative tab unspecified. Defaulting to first item registered.")

	# TODO: build stuff that needs to be in MainClass.java here

	# if "mod.ItemGroups.java" not in manifest_dict:
		# manifest_dict["mod.ItemGroups.java"] = ""
	# if "mod.ExtraOnInitialize.java" not in manifest_dict:
		# manifest_dict["mod.ExtraOnInitialize.java"] = ""

	manifest_dict["mod.content_types"] = content_types_list
	for content_type in content_types_list:
		manifest_dict[f"mod.registry.{content_type}.names"] = []

	manifest_dict[f"mod.registry.blockitem.names"] = []

	for path in manifest_dict["mod.paths"]:
		for fname in walk(ospath(os.path.join(project_path, path))):
			if fname.endswith(".txt") or fname.endswith(".m3ec"):
				d = readDictFile(fname)
				if "@" in d.keys():
					content_type = d["@"]
					if content_type == "itemfactory":
						for cid in d["items"]:
							dictinst = {"item":d["type"], "title":" ".join([w.capitalize() for w in cid.split("_")]), "texture":cid+".png"}
							add_content(cid, "item", dictinst, manifest_dict)
					elif content_type == "recipe":
						if "contentid" in d.keys():
							cid = d["contentid"]
						else:
							cid = os.path.splitext(os.path.split(fname)[-1])[0]
						add_content(cid, content_type, d, manifest_dict)
					else:
						if "contentid" in d.keys():
							cid = d["contentid"]
							add_content(cid, content_type, d, manifest_dict)
						else:
							print(f"Warning: Skipping file \"{fname}\" due to missing contentid.")
				else:
					print(f"Warning: Skipping file \"{fname}\" due to missing content type.")

	# for key in manifest_dict.keys():
		# print(f"{key}: {manifest_dict[key]}")

	source_path = manifest_dict["source_path"] = os.path.join(os.path.dirname(__file__), "sources")
	path = project_path

	if "fabric1.18.2" in modenv or "1.18.2" in modenv or "all" in modenv or "fabric" in modenv:
		make_dir(os.path.join(path, "fabric1.18.2_build", "src", "main", "resources", "data", "minecraft"))
		make_dir(os.path.join(path, "fabric1.18.2_build", "src", "main", "resources", "data", "minecraft", "tags"))
		make_dir(os.path.join(path, "fabric1.18.2_build", "src", "main", "resources", "data", "minecraft", "tags", "blocks"))
		make_dir(os.path.join(path, "fabric1.18.2_build", "src", "main", "resources", "data", "minecraft", "tags", "blocks", "mineable"))
		
		toolclasses = ["axe", "pickaxe", "shovel", "hoe"]
		toollevels = ["stone", "iron", "diamond"]
		for toolclass in toolclasses:
			manifest_dict[f"mod.registry.requires_{toolclass}"] = []
		for toollevel in toollevels:
			manifest_dict[f"mod.registry.requires_{toollevel}"] = []
		
		for block in manifest_dict["mod.registry.block.names"]:
			toollevel = toolclass = None
			if f"mod.block.{block}.toolclass" in manifest_dict.keys():
				toolclass = manifest_dict[f"mod.block.{block}.toolclass"]
			if f"mod.block.{block}.toollevel" in manifest_dict.keys():
				toollevel = manifest_dict[f"mod.block.{block}.toollevel"]
			if toolclass is None or toollevel is None:
				print(f"Error: Block {block} must contain toolclass and toollevel or neither of them.")
				exit(1)
			if toolclass is not None and toollevel is not None:
				try:
					toollevel = toollevels[int(toollevel)]
				except:
					pass
				if toolclass == "PICKAXES":
					toolclass = "pickaxe"
				elif toolclass == "AXES":
					toolclass = "axe"
				elif toolclass == "SHOVELS":
					toolclass = "shovel"
				elif toolclass == "HOES":
					toolclass = "hoe"
				manifest_dict[f"mod.block.{block}.hastoolrequirements"] = "true"
				manifest_dict[f"mod.registry.requires_{toolclass}"].append(block)
				manifest_dict[f"mod.registry.requires_{toollevel}"].append(block)
		for toolclass in toolclasses:
			if len(manifest_dict[f"mod.registry.requires_{toolclass}"]):
				create_file(os.path.join(path, "fabric1.18.2_build", "src", "main", "resources", "data", "minecraft", "tags", "blocks", "mineable", f"{toolclass}.m3ecjson"),
					readf_file(os.path.join(os.path.dirname(__file__), "sources", f"requires_{toolclass}.m3ecjson"), manifest_dict))
		for toollevel in toollevels:
			if len(manifest_dict[f"mod.registry.requires_{toollevel}"]):
				create_file(os.path.join(path, "fabric1.18.2_build", "src", "main", "resources", "data", "minecraft", "tags", "blocks", f"needs_{toollevel}_tool.m3ecjson"),
					readf_file(os.path.join(os.path.dirname(__file__), "sources", f"requires_{toollevel}.m3ecjson"), manifest_dict))

		build_mod("fabric", "1.18.2", modenv, manifest_dict)

	if "fabric1.18" in modenv or "1.18" in modenv or "all" in modenv or "fabric" in modenv:
		print("Fabric 1.18.0 builds are broken right now; ores will be skipped.")
		build_mod("fabric", "1.18", modenv, manifest_dict)

	if "fabric1.18.1" in modenv or "1.18.1" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.18.1", modenv, manifest_dict)

	if "fabric1.17" in modenv or "1.17" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.17", modenv, manifest_dict)

	if "fabric1.17.1" in modenv or "1.17.1" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.17.1", modenv, manifest_dict)

	if "fabric1.16.5" in modenv or "1.16.5" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.16.5", modenv, manifest_dict)

	if "forge1.16.5" in modenv or "1.16.5" in modenv or "all" in modenv or "forge" in modenv:
		build_mod("forge", "1.16.5", modenv, manifest_dict)

	if "forge1.12.2" in modenv or "1.12.2" in modenv or "all" in modenv or "forge" in modenv:
		build_mod("forge", "1.12.2", modenv, manifest_dict)


def build_mod(modloader, version, modenv, manifest_dict):
	print(f"Building {modloader} {version} mod project")
	manifest_dict["modloader"] = modloader
	source_path = manifest_dict["source_path"]
	project_path = manifest_dict["project_path"]
	build_path = manifest_dict["build_path"] = os.path.join(project_path, f"{modloader}{version}_build")

	try:
		with open(os.path.join(source_path, f"{modloader}{version}", "m3ec_build.json")) as f:
			versionbuilder = json.load(f)
	except FileNotFoundError:
		print(f"Warning: {modloader} {version} is not yet implemented; skipping build.")
		return False

	if "firstActions" in versionbuilder.keys():
		execActions(versionbuilder["firstActions"], versionbuilder, manifest_dict)

	build_resources(project_path, f"{modloader}{version}", manifest_dict)

	if "preActions" in versionbuilder.keys():
		execActions(versionbuilder["preActions"], versionbuilder, manifest_dict)
	
	if "sources" in versionbuilder.keys():
		for file in versionbuilder["sources"]:
			source, dest = file["source"], file["dest"]
			mandatory = True
			if "optional" in file.keys():
				if file["optional"] is True:
					mandatory = False
			if "iterate" in file.keys():
				for i in range(len(manifest_dict[file["iterate"]])):
					manifest_dict["%i"] = i
					manifest_dict["%v"] = manifest_dict[file["iterate"]][i]
					rv = readf_copyfile(os.path.join(source_path, f"{modloader}{version}", source), os.path.join(build_path, readf(dest, manifest_dict)), manifest_dict)
					if mandatory and not rv:
						print(f"Error: Failed to read source file \"{modloader}{version}/{source}\"")
						return False
			else:
				rv = readf_copyfile(os.path.join(source_path, f"{modloader}{version}", source), os.path.join(build_path, readf(dest, manifest_dict)), manifest_dict)
				if mandatory and not rv:
					print(f"Error: Failed to read source file \"{modloader}{version}/{source}\"")
					return False

	if "copy" in versionbuilder.keys():
		for file in versionbuilder["copy"]:
			shutil.copy(file["source"], file["dest"])

	if "postActions" in versionbuilder.keys():
		execActions(versionbuilder["postActions"], versionbuilder, manifest_dict)

	if "javaVersion" in versionbuilder.keys():
		maybe_run_gradle(os.path.join(project_path, f"{modloader}{version}_build"), modenv, versionbuilder["javaVersion"])

	if "finalActions" in versionbuilder.keys():
		execActions(versionbuilder["finalActions"], versionbuilder, manifest_dict)

	return True

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


def build_resources(project_path, builddir, manifest_dict):
	source_path = os.path.join(os.path.dirname(__file__),"sources")
	src = os.path.join(source_path, builddir, "gradle")
	dest = os.path.join(project_path, builddir+"_build")
	commons_path = os.path.join(source_path, "common")
	modmcpath = manifest_dict["mod.mcpath"]
	sourcesdir = os.path.join(source_path, builddir)
	builddir = os.path.join(project_path, builddir+"_build")
	build_java_dir = os.path.join(builddir, "src", "main", "java", manifest_dict["mod.prefix"], manifest_dict["mod.author"], manifest_dict["mod.class"])
	block_models_assets_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "models", "block")
	block_textures_assets_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "textures", "blocks")
	blockstates_assets_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "blockstates")
	item_models_assets_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "models", "item")
	item_textures_assets_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "textures", "items")
	lang_dir = os.path.join(builddir, "src", "main", "resources", "assets", modmcpath, "lang")
	block_loot_table_dir = os.path.join(builddir, "src", "main", "resources", "data", modmcpath, "loot_tables", "blocks")
	recipes_dir = os.path.join(builddir, "src", "main", "resources", "data", modmcpath, "recipes")

	# clean up old source files in case of deletions
	if os.path.exists(os.path.join(builddir, "src")):
		shutil.rmtree(os.path.join(builddir, "src"))

	make_dir(dest)
	make_dir(os.path.join(dest, "gradle"))
	make_dir(os.path.join(dest, "gradle", "wrapper"))
	copy_file(os.path.join(src, "gradle", "wrapper", "gradle-wrapper.jar"), os.path.join(dest, "gradle", "wrapper", "gradle-wrapper.jar"))
	copy_file(os.path.join(src, "gradle", "wrapper", "gradle-wrapper.properties"), os.path.join(dest, "gradle", "wrapper", "gradle-wrapper.properties"))
	copy_file(os.path.join(src, "gradlew"), os.path.join(dest, "gradlew"))
	copy_file(os.path.join(src, "gradlew.bat"), os.path.join(dest, "gradlew.bat"))
	if os.path.exists(os.path.join(src, "settings.gradle")):
		copy_file(os.path.join(src, "settings.gradle"), os.path.join(dest, "settings.gradle"))
	create_file(os.path.join(dest, "gradle.properties"), readf_file(os.path.join(src, "gradle.properties"), manifest_dict))
	create_file(os.path.join(dest, "build.gradle"), readf_file(os.path.join(src, "build.gradle"), manifest_dict))

	make_dir(os.path.join(dest, "src"))
	make_dir(os.path.join(dest, "src", "main"))
	make_dir(os.path.join(dest, "src", "main", "resources"))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets"))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "blockstates"))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "lang"))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "models"))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "models", "block"))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "models", "item"))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "textures"))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "textures", "blocks"))
	make_dir(os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "textures", "items"))
	make_dir(os.path.join(dest, "src", "main", "resources", "data"))
	make_dir(os.path.join(dest, "src", "main", "resources", "data", modmcpath))
	make_dir(os.path.join(dest, "src", "main", "resources", "data", modmcpath, "loot_tables"))
	make_dir(os.path.join(dest, "src", "main", "resources", "data", modmcpath, "loot_tables", "blocks"))
	make_dir(os.path.join(dest, "src", "main", "resources", "data", modmcpath, "loot_tables", "chests"))
	make_dir(os.path.join(dest, "src", "main", "resources", "data", modmcpath, "loot_tables", "entities"))
	make_dir(os.path.join(dest, "src", "main", "resources", "data", modmcpath, "loot_tables", "gameplay"))
	make_dir(os.path.join(dest, "src", "main", "resources", "data", modmcpath, "recipes"))
	make_dir(os.path.join(dest, "src", "main", "java"))
	if "mod.icon" in manifest_dict.keys():
		copy_file(os.path.join(project_path, manifest_dict["mod.icon"]), os.path.join(dest, "src", "main", "resources", "assets", modmcpath, "icon.png"))

	prefix = manifest_dict["mod.prefix"]
	modauthor = manifest_dict["mod.author"]
	modmcpathdir = os.path.join(prefix, modauthor.lower(), manifest_dict["mod.class"].lower())
	make_dir(os.path.join(dest, "src", "main", "java", prefix))
	make_dir(os.path.join(dest, "src", "main", "java", prefix, modauthor.lower()))
	make_dir(os.path.join(dest, "src", "main", "java", modmcpathdir))
	make_dir(os.path.join(dest, "src", "main", "java", modmcpathdir, "registry"))
	langdict = {"en_us":{}}
	manifest_dict[f"mod.registry.blockitem.names"].clear()

	includedClasses = []
	for content_type in manifest_dict["mod.content_types"]:
		for cid in manifest_dict[f"mod.registry.{content_type}.names"]:
			tname = manifest_dict[f"mod.{content_type}.{cid}.{content_type}"]
			# print(cid, content_type, tname)
			# print(manifest_dict[f"mod.{content_type}.{cid}.keys"])
			manifest_dict["contentid"] = manifest_dict["cid"] = cid
			for key in manifest_dict[f"mod.{content_type}.{cid}.keys"]:
				k = f"mod.{content_type}.{cid}.{key}"
				if k in manifest_dict.keys():
					manifest_dict[key] = manifest_dict[k]
			
			if "texture" in manifest_dict.keys():
				if "." in manifest_dict["texture"]:
					manifest_dict["texture"], ext = os.path.splitext(manifest_dict["texture"])

			if content_type in ["item", "food", "armor", "tool", "fuel"]:
				copy_textures(content_type, cid, manifest_dict, project_path, item_textures_assets_dir)
				create_file(os.path.join(item_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "item_models", tname+".m3ecjson"), manifest_dict))

			if content_type == "block":
				manifest_dict[f"mod.registry.blockitem.names"].append(cid)
				manifest_dict[f"mod.blockitem.{cid}.uppercased"] = cid.upper()
				copy_textures(content_type, cid, manifest_dict, project_path, block_textures_assets_dir)
				statename = manifest_dict["blockstatetype"]
				if tname.lower() == "custom":
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(project_path, manifest_dict["blockmodel"]), manifest_dict))
				else:
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_models", tname+".m3ecjson"), manifest_dict))
				create_file(os.path.join(item_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "item_models", "BlockItem.m3ecjson"), manifest_dict))
				if statename.lower() == "custom":
					create_file(os.path.join(blockstates_assets_dir, cid+".json"), readf_file(os.path.join(project_path, manifest_dict["blockstate"]), manifest_dict))
				else:
					create_file(os.path.join(blockstates_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "blockstates", statename+".m3ecjson"), manifest_dict))
				dtype = manifest_dict[f"mod.{content_type}.{cid}.droptype"]
				if dtype.lower() != "none":
					create_file(os.path.join(block_loot_table_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_loot_tables", dtype+".m3ecjson"), manifest_dict))
				if "forge" in manifest_dict["modloader"]:
					if manifest_dict[f"mod.block.{cid}.toolclass"] in ["AXES", "HOES", "PICKAXES", "SHOVELS"]:
						manifest_dict[f"mod.block.{cid}.toolclass"] = manifest_dict[f"mod.block.{cid}.toolclass"][:-1]
					if manifest_dict[f"mod.block.{cid}.material"] == "SOIL":
						manifest_dict[f"mod.block.{cid}.material"] = "DIRT"
				elif "fabric" in manifest_dict["modloader"]:
					if manifest_dict[f"mod.block.{cid}.toolclass"] in ["AXE", "HOE", "PICKAXE", "SHOVEL"]:
						manifest_dict[f"mod.block.{cid}.toolclass"] = manifest_dict[f"mod.block.{cid}.toolclass"]+"S"
					if manifest_dict[f"mod.block.{cid}.material"] == "DIRT":
						manifest_dict[f"mod.block.{cid}.material"] = "SOIL"
			if content_type == "recipe":
				create_file(os.path.join(recipes_dir, cid+".json"), readf_file(os.path.join(commons_path, "recipes", tname+".m3ecjson"), manifest_dict))
			if content_type in ["toolmaterial", "armormaterial"]:
				manifest_dict[f"mod.{content_type}.{cid}.class"] = cid
			if content_type in ["item", "block", "food", "fuel", "armor", "tool"]:
				if "langs" in manifest_dict[f"mod.{content_type}.{cid}.keys"]:
					for lang in manifest_dict[f"mod.{content_type}.{cid}.langs"]:
						if lang not in langdict.keys():
							langdict[lang] = {}
						langdict[lang][f"{content_type}.{modmcpath}.{cid}"] = manifest_dict[f"mod.{content_type}.{cid}.{lang}"]
				if content_type in ["food", "fuel", "armor", "tool"]:
					content_type_mc = "item"
				else:
					content_type_mc = content_type
				langdict["en_us"][f"{content_type_mc}.{modmcpath}.{cid}"] = manifest_dict[f"mod.{content_type}.{cid}.title"]

	if "mod.langs" in manifest_dict.keys():
		for lang in manifest_dict["mod.langs"]:
			if lang not in langdict.keys():
				langdict[lang] = {}
			langdict[lang][f"itemGroup.{modmcpath}.general"] = manifest_dict[f"mod.{lang}"]
	langdict["en_us"][f"itemGroup.{modmcpath}.general"] = manifest_dict["mod.title"]

	for lang in langdict.keys():
		with open(os.path.join(lang_dir, lang+".json"),"w") as f:
			json.dump(langdict[lang], f)


def add_content(cid, content_type, d, manifest_dict):
	# print(f"registering {content_type} {cid}.")
	if cid not in manifest_dict[f"mod.registry.{content_type}.names"]:
		manifest_dict[f"mod.registry.{content_type}.names"].append(cid)
		manifest_dict[f"mod.{content_type}.{cid}.keys"] = list(d.keys())
		for key in d.keys():
			# print(f"mod.{content_type}.{cid}.{key} = {d[key]}")
			manifest_dict[f"mod.{content_type}.{cid}.{key}"] = d[key]
		manifest_dict[f"mod.{content_type}.{cid}.uppercased"] = cid.upper()
		manifest_dict[f"mod.{content_type}.{cid}"] = manifest_dict[f"mod.{content_type}.{cid}.mcpath"] = cid.lower()
		manifest_dict[f"mod.{content_type}.{cid}.class"] = "".join([word.capitalize() for word in cid.split("_")])
	else:
		print(f"Found more than one instance of {content_type} \"{cid}\"! Aborting.")
		exit()
	if content_type == "item" and "mod.iconItem" not in manifest_dict.keys():
		manifest_dict["mod.iconItem"] = manifest_dict[f"mod.{content_type}.{cid}.uppercased"]

def maybe_run_gradle(path, modenv, javaver):
	path = os.path.abspath(path)
	modenvlow = [m.lower() for m in modenv]
	if "buildjar" in modenvlow or "runclient" in modenvlow or "runserver" in modenvlow:
		javapath = find_java_version(javaver)
		if javapath is not None:
			javapath = "-Dorg.gradle.java.home="+javapath
		if sys.platform.startswith("win32"):
			fname = "gradlew.bat"
		else:
			fname = "gradlew"

	if "buildjar" in modenv:
		subprocess.Popen([os.path.join(path, fname), "build", "jar", javapath], cwd=path).wait()
	if "runClient" in modenv:
		subprocess.Popen([os.path.join(path, fname), "runClient", javapath], cwd=path).wait()
	if "runServer" in modenv:
		subprocess.Popen([os.path.join(path, fname), "runServer", javapath], cwd=path).wait()


def find_java_version(javaver):
	if sys.platform.startswith("win32"):
		javapath = find_jdk("C:\\Program Files\\Java", javaver)
		if javapath is None:
			javapath = find_jdk("C:\\Program Files (x86)\\Java", javaver)
	else:
		javapath = find_jdk("/usr/lib/jvm", javaver)

	if javapath is None:
		try:
			return input(f"Input path to Java jdk {javaver} by pasting or typing it here and pressing enter.\n\
	Or type \"default\" to use system default java path.\n")
		except:
			pass

		if javapath.lower() == "default":
			print(f"Using default Java for Java jdk {javaver}")
			return None
		else:
			return os.path.normpath(javapath)

	return javapath

def find_jdk(path, javaver):
	if os.path.exists(path):
		for root, dirs, files in os.walk(path):
			for d in dirs:
				if javaver in d and d.startswith("jdk"):
					return os.path.join(root, d)
	return None

def copy_textures(content_type, cid, manifest_dict, project_path, dest_dir):
	project_tex_path = os.path.join(project_path, manifest_dict["mod.textures"])
	# print(project_tex_path)
	if f"mod.{content_type}.{cid}.texture" in manifest_dict.keys():
		tex = texture_pathify(manifest_dict[f"mod.{content_type}.{cid}.texture"])
		copy_file(os.path.join(project_tex_path, tex)+".png", os.path.join(dest_dir, os.path.basename(tex))+".png")
		manifest_dict["texture"] = os.path.basename(tex)
	if f"mod.{content_type}.{cid}.texture_top" in manifest_dict.keys():
		tex = texture_pathify(manifest_dict[f"mod.{content_type}.{cid}.texture_top"])
		copy_file(os.path.join(project_tex_path, tex)+".png", os.path.join(dest_dir, os.path.basename(tex))+".png")
		manifest_dict["texture_top"] = os.path.basename(tex)
	if f"mod.{content_type}.{cid}.texture_bottom" in manifest_dict.keys():
		tex = texture_pathify(manifest_dict[f"mod.{content_type}.{cid}.texture_bottom"])
		copy_file(os.path.join(project_tex_path, tex)+".png", os.path.join(dest_dir, os.path.basename(tex))+".png")
		manifest_dict["texture_bottom"] = os.path.basename(tex)
	if f"mod.{content_type}.{cid}.texture_side" in manifest_dict.keys():
		tex = texture_pathify(manifest_dict[f"mod.{content_type}.{cid}.texture_side"])
		copy_file(os.path.join(project_tex_path, tex)+".png", os.path.join(dest_dir, os.path.basename(tex))+".png")
		manifest_dict["texture_side"] = os.path.basename(tex)

def texture_pathify(tex):
	tex, ext = os.path.splitext(tex)
	return tex

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
			key = data[i+6:n]
			# print(f"Checking if {key} is defined. ",end="")
			j = data.find("---fi",n)
			if key in d.keys():
				# print("key found.")
				l = d[key]
				data2.append(data[n:j])
				# print(data2[-1])
				j += 5
			else:
				# print("key not found.")
				j += 5
		data2.append(data[j:])
		data = "".join(data2)

	while any([any(["${"+key+M+"}" in data for M in ["","^CAPITAL","^UPPER","^LOWER"]]) for key in d.keys()]):
		for key in d.keys():
			data = data.replace("${"+key+"^CAPITAL}", str(d[key]).capitalize()).replace("${"+key+"^UPPER}", str(d[key]).upper()).replace("${"+key+"^LOWER}", str(d[key]).lower()).replace("${"+key+"}", str(d[key]))
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
	return data

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
		d = dict()
	try:
		with open(fname) as f:
			return readDictString(f.read(), d)
	except FileNotFoundError:
		return None

def readDictString(data, d={}):
	ns = ""
	for line in data.splitlines():
		if len(line) and not line.startswith("#"):
			if ":" in line:
				name, value = line.split(":",maxsplit=1)
				v = value.lstrip(" \t")
				if line.startswith("+"):
					if line.startswith("+."):
						if len(name)>2:
							k = ns+name[1:]
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
					else:
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
	return d

def ospath(path):
	if sys.platform == "win32":
		return os.path.abspath(os.path.normpath(path.replace("/", "\\")))
	else:
		return os.path.abspath(os.path.normpath(path.replace("\\", "/")))


if __name__=='__main__':
	if len(sys.argv) < 3:
		print("""
Minecraft Multiple Mod Environment Compiler v0.6
Very much unfinished, currently only supports a handful of minecraft/modloader versions.
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
+ fabric
+ fabric1.16.5
+ fabric1.17
+ fabric1.17.1
+ fabric1.18 (ores are broken and will be skipped)
+ fabric1.18.1
+ fabric1.18.2
+ forge
+ forge1.16.5

Additionally, modenv may be appended with any combination of:
+ buildjar (builds mod into a jar file)
+ runclient (launches an offline client with the mod installed)
+ runserver (launches an offline server with the mod installed)

---------------------------------------------------------------------
--  input "quit" to quit.
---------------------------------------------------------------------
""")
		while True:
			d = input("m3ec> ").split(" ")
			if len(d) > 1:
				build(d[0], " ".join(d[1:]))
			elif len(d):
				if d[0] in ["exit", "quit", "e", "q", "x"]:
					break
	else:
		build(sys.argv[1], " ".join(sys.argv[2:]))


