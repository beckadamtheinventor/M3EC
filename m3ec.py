
import os, sys, json, shutil

from _m3ec.actions import *
from _m3ec.gradle import *
from _m3ec.util import *

def interpret_args(argv):
	content_types_list = ["item", "food", "fuel", "block", "ore", "recipe", "armor", "tool", "armormaterial", "toolmaterial", "enchantment", "recipetype"]
	source_path = os.path.join(os.path.dirname(__file__), "data")
	if argv[0].lower() == "help":
		print("""Usage:
project_path all|fabric|forge[gameversion]|fabric[gameversion]
gen|generate item|food|fuel|block|ore|recipe|armor[material]|tool[material] content_id|Title [output_file] [key:value...]
""")
	elif len(argv) > 1:
		if argv[0].lower() in ("generate", "gen"):
			if argv[1] in content_types_list:
				if len(argv) > 2:
					title, cid, upper = ParseContentTitle(argv[2])
				else:
					title = cid = upper = ""
				d = {"cid": cid, "title": title, "upper": upper}
				if len(argv) > 4:
					for a in argv[4:]:
						if ":" in a:
							k, v = a.split(":", maxsplit=1)
							d[k] = v
						else:
							d[a] = "yes"
				data = getDictString(d)
				if len(argv) > 3:
					try:
						with open(argv[3], "w") as f:
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
	content_types_list = ["item", "food", "fuel", "block", "ore", "recipe", "armor", "tool", "armormaterial", "toolmaterial", "enchantment", "recipetype"]
	source_path = os.path.join(os.path.dirname(__file__), "data")

	if not os.path.exists(project_path):
		print(f"Manifest file \"{project_path}\" not found. Aborting.")
		return False

	manifest_file = os.path.join(project_path, "manifest.m3ec")
	if not os.path.exists(manifest_file):
		manifest_file = os.path.join(project_path, "manifest.txt")
		if not os.path.exists(manifest_file):
			print(f"Manifest file (manifest.m3ec/manifest.txt) not found in \"{project_path}\". Aborting.")
			return False

	if not os.path.isdir(project_path):
		project_path = os.path.dirname(project_path)

	manifest_dict = readDictFile(manifest_file)

	manifest_dict["manifest_file"] = manifest_file
	manifest_dict["project_path"] = project_path

	try:
		fname = os.path.join(source_path, "mc", "blocks.json")
		with open(fname) as f:
			blocks = json.load(f)
		for block in blocks["content"]:
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
	manifest_dict["mod.customclasses"] = []
	manifest_dict["mod.registry.classes"] = []
	manifest_dict[f"mod.files"] = {}

	for a in ["first", "pre", "post", "final"]:
		if f"{a}ExecActions" not in manifest_dict.keys():
			manifest_dict[f"{a}ExecActions"] = []

	for file in manifest_dict["firstExecActions"]:
		try:
			with open(file) as f:
				j = json.load(f)
		except FileNotFoundError:
			print(f"Warning: file \"{file}\" listed in firstExecActions does not exist.")
		execActions(j, manifest_dict)

	for path in manifest_dict["mod.paths"]:
		for fname in walk(os.path.normpath(os.path.join(project_path, path))):
			if fname.endswith(".txt") or fname.endswith(".m3ec"):
				d = readDictFile(fname)
				if "@" in d.keys():
					content_type = d["@"]
					if content_type == "class":
						manifest_dict["mod.customclasses"].append({"file":d["file"], "class":d["class"],"modloader":d["modloader"], "gameversions":d["gameversions"]})
						manifest_dict["mod.registry.classes"].append(d["class"])
						continue
					elif content_type == "itemfactory":
						for cid in d["items"]:
							dictinst = {"item":d["type"], "title":" ".join([w.capitalize() for w in cid.split("_")]), "texture":cid+".png"}
							add_content(cid, "item", dictinst, manifest_dict, fname)
						continue
					if "contentid" not in d.keys():
						print(f"Warning: Skipping file \"{fname}\" due to missing contentid.")
						continue
					if content_type == "recipe":
						if "contentid" in d.keys():
							cid = d["contentid"]
						else:
							cid = os.path.splitext(os.path.split(fname)[-1])[0]
						add_content(cid, content_type, d, manifest_dict, fname)
					else:
						if "contentid" in d.keys():
							cid = d["contentid"]
							if content_type == "block":
								if "blockstatetype" not in d.keys():
									d["blockstatetype"] = "Single"
								if "BlockClass" not in d.keys():
									d["BlockClass"] = "Block"
							# print(f"adding {content_type} {cid}", d)
							add_content(cid, content_type, d, manifest_dict, fname)
						if content_type == "block":
							midcid = manifest_dict["mod.mcpath"]+":"+cid
							if checkDictKeyTrue(manifest_dict, f"mod.{content_type}.{cid}.autogenerate.slab"):
								d = readDictFile(fname)
								d["title"] = d["title"]+" Slab"
								d["drops"] = d["contentid"] = cid+"_slab"
								d["droptype"] = "Slab"
								d["blockstatetype"] = "Slab"
								d["texture_bottom"] = d["texture_top"] = d["texture_side"] = d["texture"]
								d["BlockClass"] = "SlabBlock"
								add_content(cid+"_slab", content_type, d, manifest_dict)
								if checkDictKeyTrue(manifest_dict, f"mod.{content_type}.{cid}.autogenerate.slab.recipe"):
									add_content(cid+"_slab", "recipe", {
										"@": "recipe", "recipe": "ShapedRecipe",
										"pattern": ['"###"'], "items": [midcid], "itemkeys": ["#"], "itemkeys.list.0": "#",
										"result": midcid+"_slab", "count": "6",
									}, manifest_dict)
								if checkDictKeyTrue(manifest_dict, f"mod.{content_type}.{cid}.autogenerate.slab.stonecuttingrecipe"):
									add_content(cid+"_slab_stonecutter", "recipe", {
										"@": "recipe", "recipe": "StoneCuttingRecipe",
										"ingredient": midcid, "result": midcid+"_slab", "count": "2",
									}, manifest_dict)
							if checkDictKeyTrue(manifest_dict, f"mod.{content_type}.{cid}.autogenerate.stairs"):
								d = readDictFile(fname)
								d["title"] = d["title"]+" Stairs"
								d["drops"] = d["contentid"] = cid+"_stairs"
								d["droptype"] = "Self"
								d["blockstatetype"] = "Stair"
								d["texture_bottom"] = d["texture_top"] = d["texture_side"] = d["texture"]
								d["BlockClass"] = "ModStairBlock"
								d["BlockMaterialBlock"] = cid
								d["BlockClass.isStair"] = "true"
								add_content(cid+"_stairs", content_type, d, manifest_dict)
								if checkDictKeyTrue(manifest_dict, f"mod.{content_type}.{cid}.autogenerate.stairs.recipe"):
									add_content(cid+"_stairs", "recipe", {
										"@": "recipe", "recipe": "ShapedRecipe",
										"pattern": ['"#  "', '"## "', '"###"'], "items": [midcid], "itemkeys": ["#"],"itemkeys.list.0": "#",
										"result": midcid+"_stairs", "count": "4",
									}, manifest_dict)
									add_content(cid+"_stairs_reversed", "recipe", {
										"@": "recipe", "recipe": "ShapedRecipe",
										"pattern": ['"  #"', '" ##"', '"###"'], "items": [midcid], "itemkeys": ["#"], "itemkeys.list.0": "#",
										"result": midcid+"_stairs", "count": "4",
									}, manifest_dict)
								if checkDictKeyTrue(manifest_dict, f"mod.{content_type}.{cid}.autogenerate.stairs.stonecuttingrecipe"):
									add_content(cid+"_stairs_stonecutter", "recipe", {
										"@": "recipe", "recipe": "StoneCuttingRecipe",
										"ingredient": midcid, "result": midcid+"_stairs", "count": "1",
									}, manifest_dict)
							if checkDictKeyTrue(manifest_dict, f"mod.{content_type}.{cid}.autogenerate.trapdoor"):
								d = readDictFile(fname)
								d["title"] = d["title"]+" Trapdoor"
								d["drops"] = d["contentid"] = cid+"_trapdoor"
								d["droptype"] = "Self"
								d["blockstatetype"] = "Trapdoor"
								d["texture_bottom"] = d["texture_top"] = d["texture_side"] = d["texture"]
								d["BlockClass"] = "ModTrapdoorBlock"
								add_content(cid+"_trapdoor", content_type, d, manifest_dict)
								if checkDictKeyTrue(manifest_dict, f"mod.{content_type}.{cid}.autogenerate.trapdoor.recipe"):
									add_content(cid+"_trapdoor", "recipe", {
										"@": "recipe", "recipe": "ShapedRecipe",
										"pattern": ['"###"', '"###"'], "items": [midcid], "itemkeys": ["#"], "itemkeys.list.0": "#",
										"result": midcid+"_trapdoor", "count": "2",
									}, manifest_dict)
								if checkDictKeyTrue(manifest_dict, f"mod.{content_type}.{cid}.autogenerate.trapdoor.stonecuttingrecipe"):
									add_content(cid+"_slab_stonecutter", "recipe", {
										"@": "recipe", "recipe": "StoneCuttingRecipe",
										"ingredient": midcid, "result": midcid+"_trapdoor", "count": "1",
									}, manifest_dict)
				else:
					print(f"Warning: Skipping file \"{fname}\" due to missing content type.")

		# print(f"{key}: {manifest_dict[key]}")

	source_path = manifest_dict["source_path"] = os.path.join(os.path.dirname(__file__), "data")
	path = project_path

	if "forge1.16.5" in modenv or "1.16.5" in modenv or "all" in modenv or "forge" in modenv:
		build_mod("forge", "1.16.5", modenv, manifest_dict.copy())

	if "forge1.18.1" in modenv or "1.18.1" in modenv or "all" in modenv or "forge" in modenv:
		build_mod("forge", "1.18.1", modenv, manifest_dict.copy())

	if "forge1.18.2" in modenv or "1.18.2" in modenv or "all" in modenv or "forge" in modenv:
		build_mod("forge", "1.18.2", modenv, manifest_dict.copy())

	# if "forge1.12.2" in modenv or "1.12.2" in modenv or "all" in modenv or "forge" in modenv:
		# build_mod("forge", "1.12.2", modenv, manifest_dict.copy())

	if "fabric1.16.5" in modenv or "1.16.5" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.16.5", modenv, manifest_dict.copy())

	if "fabric1.17" in modenv or "1.17" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.17", modenv, manifest_dict.copy())

	if "fabric1.17.1" in modenv or "1.17.1" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.17.1", modenv, manifest_dict.copy())

	if "fabric1.18" in modenv or "1.18" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.18", modenv, manifest_dict.copy())

	if "fabric1.18.1" in modenv or "1.18.1" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.18.1", modenv, manifest_dict.copy())

	if "fabric1.18.2" in modenv or "1.18.2" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.18.2", modenv, manifest_dict.copy())

	if "fabric1.19" in modenv or "1.19" in modenv or "all" in modenv or "fabric" in modenv:
		build_mod("fabric", "1.19", modenv, manifest_dict.copy())

	for file in manifest_dict["finalExecActions"]:
		try:
			with open(file) as f:
				j = json.load(f)
		except FileNotFoundError:
			print(f"Warning: file \"{file}\" listed in preExecActions does not exist.")
		execActions(j, manifest_dict)

def build_mod(modloader, version, modenv, manifest_dict):
	print(f"\n\
\n\
-----------------------------------------------\n\
   Building {modloader} {version} mod project\n")
	manifest_dict["modloader"] = modloader
	manifest_dict["gameversion"] = gameversion = version
	source_path = manifest_dict["source_path"]
	project_path = manifest_dict["project_path"]
	build_path = manifest_dict["build_path"] = os.path.join(project_path, f"{modloader}{version}_build")

	for file in manifest_dict["preExecActions"]:
		try:
			with open(file) as f:
				j = json.load(f)
		except FileNotFoundError:
			print(f"Warning: file \"{file}\" listed in preExecActions does not exist.")
		execActions(j, manifest_dict)

	try:
		with open(os.path.join(source_path, f"{modloader}{version}", "m3ec_build.json")) as f:
			versionbuilder = json.load(f)
	except FileNotFoundError:
		print(f"Warning: {modloader} {version} is not yet implemented; skipping build.")
		return False

	if "firstActions" in versionbuilder.keys():
		execActions(versionbuilder["firstActions"], manifest_dict)

	build_resources(project_path, f"{modloader}{version}", manifest_dict)

	if "preActions" in versionbuilder.keys():
		execActions(versionbuilder["preActions"], manifest_dict)
	
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

	if "mod.customclasses" in manifest_dict.keys():
		for customclass in manifest_dict["mod.customclasses"]:
			if "modloaders" in customclass.keys():
				if modloader not in customclass["modloaders"]:
					continue
			if "gameversions" in customclass.keys():
				if gameversion not in customclass["gameversions"]:
					continue
			fname = readf(customclass["file"], manifest_dict)
			if not readf_copyfile(os.path.join(project_path, fname), os.path.join(build_path, "src", "main", "java", readf(customclass["class"], manifest_dict).replace(".", os.sep)+".java"), manifest_dict):
				print(f"Error: Failed to copy custom class file \"{fname}\"")
				return False

	if "mod.customfiles" in manifest_dict.keys():
		# print(manifest_dict["mod.customfiles"])
		for file in manifest_dict["mod.customfiles"]:
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
			if not readf_copyfile(os.path.join(project_path, source), os.path.join(build_path, readf(dest, manifest_dict)), manifest_dict):
				print(f"Error: Failed to copy custom file \"{source}\"")
				return False

	if "postActions" in versionbuilder.keys():
		execActions(versionbuilder["postActions"], manifest_dict)

	if "javaVersion" in versionbuilder.keys():
		maybe_run_gradle(os.path.join(project_path, f"{modloader}{version}_build"), modenv, versionbuilder["javaVersion"])

	if "finalActions" in versionbuilder.keys():
		execActions(versionbuilder["finalActions"], manifest_dict)

	for file in manifest_dict["postExecActions"]:
		try:
			with open(file) as f:
				j = json.load(f)
		except FileNotFoundError:
			print(f"Warning: file \"{file}\" listed in preExecActions does not exist.")
		execActions(j, manifest_dict)

	return True

def build_resources(project_path, builddir, manifest_dict):
	source_path = os.path.join(os.path.dirname(__file__),"data")
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

			if content_type in ["item", "food", "armor", "tool"]:
				copy_textures(content_type, cid, manifest_dict, project_path, item_textures_assets_dir)
				create_file(os.path.join(item_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "item_models", tname+".m3ecjson"), manifest_dict))

			if content_type == "block":
				manifest_dict[f"mod.registry.blockitem.names"].append(cid)
				manifest_dict[f"mod.blockitem.{cid}.uppercased"] = cid.upper()
				copy_textures(content_type, cid, manifest_dict, project_path, block_textures_assets_dir)
				if "blockstatetype" in manifest_dict.keys():
					statename = manifest_dict["blockstatetype"]
				else:
					statename = "Single"
				create_file(os.path.join(item_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "item_models", "BlockItem.m3ecjson"), manifest_dict))
				create_file(os.path.join(blockstates_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "blockstates", statename+".m3ecjson"), manifest_dict))
				if statename == "3Axis":
					create_file(os.path.join(block_models_assets_dir, cid+"_side.json"), readf_file(os.path.join(commons_path, "block_models", tname+"_side.m3ecjson"), manifest_dict))
				elif statename == "Trapdoor":
					create_file(os.path.join(block_models_assets_dir, cid+"_bottom.json"), readf_file(os.path.join(commons_path, "block_models", "Trapdoor_bottom.m3ecjson"), manifest_dict))
					create_file(os.path.join(block_models_assets_dir, cid+"_open.json"), readf_file(os.path.join(commons_path, "block_models", "Trapdoor_open.m3ecjson"), manifest_dict))
					create_file(os.path.join(block_models_assets_dir, cid+"_top.json"), readf_file(os.path.join(commons_path, "block_models", "Trapdoor_top.m3ecjson"), manifest_dict))
				elif statename == "Slab":
					create_file(os.path.join(block_models_assets_dir, cid+"_double.json"), readf_file(os.path.join(commons_path, "block_models", "SimpleBlock.m3ecjson"), manifest_dict))
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_models", statename+".m3ecjson"), manifest_dict))
					create_file(os.path.join(block_models_assets_dir, cid+"_top.json"), readf_file(os.path.join(commons_path, "block_models", statename+"_top.m3ecjson"), manifest_dict))
				elif statename == "Stair":
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_models", "Stair.m3ecjson"), manifest_dict))
					create_file(os.path.join(block_models_assets_dir, cid+"_inner.json"), readf_file(os.path.join(commons_path, "block_models", statename+"_inner.m3ecjson"), manifest_dict))
					create_file(os.path.join(block_models_assets_dir, cid+"_outer.json"), readf_file(os.path.join(commons_path, "block_models", statename+"_outer.m3ecjson"), manifest_dict))
				else:
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_models", tname+".m3ecjson"), manifest_dict))
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
				if not manifest_dict[f"mod.block.{cid}.toollevel"].isnumeric():
					manifest_dict[f"mod.block.{cid}.toollevelstring"] = "MiningLevels." + manifest_dict[f"mod.block.{cid}.toollevel"]
					if manifest_dict[f"mod.block.{cid}.toollevel"] in ["WOOD", "STONE", "IRON", "DIAMOND", "NETHERITE"]:
						manifest_dict[f"mod.block.{cid}.toollevelint"] = str(["WOOD", "STONE", "IRON", "DIAMOND", "NETHERITE"].index(manifest_dict[f"mod.block.{cid}.toollevel"]))
					else:
						manifest_dict[f"mod.block.{cid}.toollevelint"] = "0"
				else:
					manifest_dict[f"mod.block.{cid}.toollevelstring"] = manifest_dict[f"mod.block.{cid}.toollevel"]
					manifest_dict[f"mod.block.{cid}.toollevelint"] = manifest_dict[f"mod.block.{cid}.toollevel"]
				# print(manifest_dict[f"mod.block.{cid}.toollevelstring"], manifest_dict[f"mod.block.{cid}.toollevelint"])

			if content_type == "recipe":
				create_file(os.path.join(recipes_dir, cid+".json"), readf_file(os.path.join(commons_path, "recipes", tname+".m3ecjson"), manifest_dict))
			if content_type in ["toolmaterial", "armormaterial"]:
				manifest_dict[f"mod.{content_type}.{cid}.class"] = cid
			if content_type in ["item", "block", "food", "armor", "tool"]:
				if "langs" in manifest_dict[f"mod.{content_type}.{cid}.keys"]:
					for lang in manifest_dict[f"mod.{content_type}.{cid}.langs"]:
						if lang not in langdict.keys():
							langdict[lang] = {}
						langdict[lang][f"{content_type}.{modmcpath}.{cid}"] = manifest_dict[f"mod.{content_type}.{cid}.{lang}"]
				if content_type in ["food", "armor", "tool"]:
					content_type_mc = "item"
				else:
					content_type_mc = content_type
				langdict["en_us"][f"{content_type_mc}.{modmcpath}.{cid}"] = manifest_dict[f"mod.{content_type}.{cid}.title"]

			if "customclass" in manifest_dict.keys():
				manifest_dict[f"mod.{content_type}.{cid}.customclass"] = manifest_dict["customclass"]
			elif content_type in ["item", "food", "armor", "tool"]:
				manifest_dict[f"mod.{content_type}.{cid}.customclass"] = "Item"


	if "mod.langs" in manifest_dict.keys():
		for lang in manifest_dict["mod.langs"]:
			if lang not in langdict.keys():
				langdict[lang] = {}
			langdict[lang][f"itemGroup.{modmcpath}.general"] = manifest_dict[f"mod.{lang}"]
	langdict["en_us"][f"itemGroup.{modmcpath}.general"] = manifest_dict["mod.title"]

	for lang in langdict.keys():
		with open(os.path.join(lang_dir, lang+".json"),"w") as f:
			json.dump(langdict[lang], f)


def copy_textures(content_type, cid, manifest_dict, project_path, dest_dir):
	project_tex_path = os.path.join(project_path, manifest_dict["mod.textures"])
	# print(project_tex_path)
	for side in ["", "_top", "_bottom", "_side", "_front", "_back"]:
		if f"mod.{content_type}.{cid}.texture{side}" in manifest_dict.keys():
			tex, ext = os.path.splitext(manifest_dict[f"mod.{content_type}.{cid}.texture{side}"])
			copy_file(os.path.join(project_tex_path, tex)+".png", os.path.join(dest_dir, os.path.basename(tex))+".png")
			manifest_dict[f"texture{side}"] = texture_pathify(manifest_dict, tex, content_type, cid)


if __name__=='__main__':
	if len(sys.argv) < 2:
		print("""
Minecraft Multiple Mod Environment Compiler v0.6
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
+ fabric1.18
+ fabric1.18.1
+ fabric1.18.2
+ forge
+ forge1.16.5

Note: Not all the game versions/modloaders listed are implemented to the same degree.
      If a feature is present in your mod that is not yet supported by the version/modloader implementation,
	  those features will be skipped and a warning will be printed to the console.

Additionally, modenv may be appended with any combination of:
+ buildjar (builds mod into a jar file)
+ runclient (launches an offline client with the mod installed)
+ runserver (launches an offline server with the mod installed)

---------------------------------------------------------------------
--  interactive build prompt
--  input "quit" to quit, "help" for help.
--  usage: path modenv
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


