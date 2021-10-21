
import os, sys, json, re

def build(project_path, modenv):
	if " " in modenv:
		modenv = modenv.split(" ")
	else:
		modenv = [modenv]
	content_types_list = ["item", "food", "fuel", "block", "ore", "recipe", "armor", "tool", "armormaterial", "toolmaterial"]
	source_path = os.path.join(os.path.dirname(__file__),"sources")

	if os.path.isdir(project_path):
		manifest_file = os.path.join(project_path, "manifest.txt")
	else:
		manifest_file = project_path
		project_path = os.path.dirname(project_path)
	with open(manifest_file) as f:
		manifest = f.read().splitlines()

	manifest_dict = readDictFile(manifest_file)
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
	modmcpathdir = os.path.join(prefix, modauthor.lower(), modclass.lower())

	for k in ["credits", "description"]:
		if f"mod.{k}" not in manifest_dict.keys():
			manifest_dict[f"mod.{k}"] = ""

	if "mod.license" not in manifest_dict.keys():
		print("--------------------WARNING---------------------\nMod license defaulting to \"All Rights Reserved\".\n\
Please specify your mod's license in its manifest file to avoid licensing confusion.\n\
Check the list of common licenses from https://choosealicense.com/ and choose the one that best fits your needs.\n\
------------------------------------------------\n")
		manifest_dict["mod.license"] = "All Rights Reserved"


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
			if fname.endswith(".txt"):
				d = readDictFile(fname, {})
				if "@" in d.keys():
					content_type = d["@"]
					if "contentid" in d.keys():
						cid = d["contentid"]
						if cid not in manifest_dict[f"mod.registry.{content_type}.names"]:
							manifest_dict[f"mod.registry.{content_type}.names"].append(cid)
							manifest_dict[f"mod.{content_type}.{cid}.keys"] = list(d.keys())
							for key in d.keys():
								manifest_dict[f"mod.{content_type}.{cid}.{key}"] = d[key]
							manifest_dict[f"mod.{content_type}.{cid}.uppercased"] = cid.upper()
							manifest_dict[f"mod.{content_type}.{cid}.mcpath"] = cid.lower()
							manifest_dict[f"mod.{content_type}.{cid}.class"] = "".join([word.capitalize() for word in cid.split("_")])
						else:
							print(f"Found more than one instance of {content_type} \"{cid}\"! Aborting.")
							exit()
					else:
						print(f"Warning: Skipping file \"{fname}\" due to missing contentid.")
				else:
					print(f"Warning: Skipping file \"{fname}\" due to missing content type.")

	# for key in manifest_dict.keys():
		# print(f"{key}: {manifest_dict[key]}")

	source_path = os.path.join(os.path.dirname(__file__),"sources")
	path = project_path

	if "fabric1.17" in modenv or "1.17" in modenv or "all" in modenv or "fabric" in modenv:
		print("Building fabric 1.17 mod project")
		manifest_dict["modloader"] = "fabric"

		build_resources(project_path, "fabric1.17", manifest_dict)

		data = readf_file(os.path.join(source_path, "fabric1.17", "MainClass.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric1.17/MainClass.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric1.17_build", "src", "main", "java", modmcpathdir, f"{modclass}.java"), data)

		data = readf_file(os.path.join(source_path, "fabric1.17", "registry", "ModBlocks.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric1.17/registry/ModBlocks.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric1.17_build", "src", "main", "java", modmcpathdir, "registry", "ModBlocks.java"), data)

		data = readf_file(os.path.join(source_path, "fabric1.17", "registry", "ModItems.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric1.17/registry/ModItems.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric1.17_build", "src", "main", "java", modmcpathdir, "registry", "ModItems.java"), data)

	if "fabric1.17.1" in modenv or "1.17.1" in modenv or "all" in modenv or "fabric" in modenv:
		print("Building fabric 1.17.1 mod project")
		manifest_dict["modloader"] = "fabric"

		build_resources(project_path, "fabric1.17.1", manifest_dict)

		data = readf_file(os.path.join(source_path, "fabric1.17.1", "MainClass.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric1.17.1/MainClass.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric1.17.1_build", "src", "main", "java", modmcpathdir, f"{modclass}.java"), data)

		data = readf_file(os.path.join(source_path, "fabric1.17.1", "registry", "ModBlocks.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric1.17.1/registry/ModBlocks.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric1.17.1_build", "src", "main", "java", modmcpathdir, "registry", "ModBlocks.java"), data)

		data = readf_file(os.path.join(source_path, "fabric1.17.1", "registry", "ModItems.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric1.17.1/registry/ModItems.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric1.17.1_build", "src", "main", "java", modmcpathdir, "registry", "ModItems.java"), data)

	if "fabric1.16.5" in modenv or "1.16.5" in modenv or "all" in modenv or "fabric" in modenv:
		print("Building fabric 1.16.5 mod project")
		manifest_dict["modloader"] = "fabric"

		build_resources(project_path, "fabric1.16.5", manifest_dict)

		data = readf_file(os.path.join(source_path, "fabric1.16.5", "MainClass.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric1.16.5/MainClass.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric1.16.5_build", "src", "main", "java", modmcpathdir, f"{modclass}.java"), data)

		data = readf_file(os.path.join(source_path, "fabric1.16.5", "registry", "ModBlocks.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric1.16.5/registry/ModBlocks.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric1.16.5_build", "src", "main", "java", modmcpathdir, "registry", "ModBlocks.java"), data)

		data = readf_file(os.path.join(source_path, "fabric1.16.5", "registry", "ModItems.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric1.16.5/registry/ModItems.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric1.16.5_build", "src", "main", "java", modmcpathdir, "registry", "ModItems.java"), data)

	if "forge1.16.5" in modenv or "1.16.5" in modenv or "all" in modenv or "forge" in modenv:
		print("Building forge 1.16.5 mod project")
		manifest_dict["modloader"] = "forge"

		build_resources(project_path, "forge1.16.5", manifest_dict)

		data = readf_file(os.path.join(source_path, "forge1.16.5", "MainClass.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge1.16.5/MainClass.java.txt\"")
		else:
			create_file(os.path.join(path, "forge1.16.5_build", "src", "main", "java", modmcpathdir, f"{modclass}.java"), data)

		data = readf_file(os.path.join(source_path, "forge1.16.5", "pack.mcmeta"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge1.16.5/pack.mcmeta\"")
		else:
			create_file(os.path.join(path, "forge1.16.5_build", "src", "main", "resources", "pack.mcmeta"), data)

		make_dir(os.path.join(path, "forge1.16.5_build", "src", "main", "resources", "META-INF"))
		data = readf_file(os.path.join(source_path, "forge1.16.5", "META-INF", "mods.toml"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge1.16.5/META-INF/mods.toml\"")
		else:
			create_file(os.path.join(path, "forge1.16.5_build", "src", "main", "resources", "META-INF", "mods.toml"), data)

		data = readf_file(os.path.join(source_path, "forge1.16.5", "registry", "ModBlocks.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge1.16.5/registry/ModBlocks.java.txt\"")
		else:
			create_file(os.path.join(path, "forge1.16.5_build", "src", "main", "java", modmcpathdir, "registry", "ModBlocks.java"), data)

		data = readf_file(os.path.join(source_path, "forge1.16.5", "registry", "ModItems.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge1.16.5/registry/ModItems.java.txt\"")
		else:
			create_file(os.path.join(path, "forge1.16.5_build", "src", "main", "java", modmcpathdir, "registry", "ModItems.java"), data)

		make_dir(os.path.join(path, "forge1.16.5_build", "src", "main", "java", modmcpathdir, "blocks"))
		for block in manifest_dict["mod.registry.block.names"]:
			manifest_dict["$%f"] = block
			
			data = readf_file(os.path.join(source_path, "forge1.16.5", "Block.java.txt"), manifest_dict)
			if data is None:
				print("Warning: Failed to read source \"forge1.16.5/Block.java.txt\"")
			else:
				create_file(os.path.join(path, "forge1.16.5_build", "src", "main", "java", modmcpathdir, "blocks", manifest_dict[f"mod.block.{block}.class"]+".java"), data)

	if "forge1.12.2" in modenv or "1.12.2" in modenv or "all" in modenv or "forge" in modenv:
		print("Building forge 1.12.2 mod project")
		manifest_dict["modloader"] = "forge"

		build_resources(project_path, "forge1.12.2", manifest_dict)

		data = readf_file(os.path.join(source_path, "forge1.12.2", "MainClass.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge1.12.2/MainClass.java.txt\"")
		else:
			create_file(os.path.join(path, "forge1.12.2_build", "src", "main", "java", modmcpathdir, f"{modclass}.java"), data)

		data = readf_file(os.path.join(source_path, "forge1.12.2", "init", "ModBlocks.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge1.12.2/init/ModBlocks.java.txt\"")
		else:
			create_file(os.path.join(path, "forge1.12.2_build", "src", "main", "java", modmcpathdir, "init", "ModBlocks.java"), data)

		data = readf_file(os.path.join(source_path, "forge1.12.2", "init", "ModItems.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge1.12.2/init/ModItems.java.txt\"")
		else:
			create_file(os.path.join(path, "forge1.12.2_build", "src", "main", "java", modmcpathdir, "init", "ModItems.java"), data)

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
			for key in manifest_dict[f"mod.{content_type}.{cid}.keys"]:
				k = f"mod.{content_type}.{cid}.{key}"
				if k in manifest_dict.keys():
					manifest_dict[key] = manifest_dict[k]

			if content_type in ["item", "food", "armor", "tool", "fuel"]:
				create_file(os.path.join(item_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "item_models", tname+".json"), manifest_dict))
				copy_textures(content_type, cid, manifest_dict, project_path, item_textures_assets_dir)

			if content_type == "block":
				manifest_dict[f"mod.registry.blockitem.names"].append(cid)
				manifest_dict[f"mod.blockitem.{cid}.uppercased"] = cid.upper()
				if "hasInventory" in manifest_dict.keys():
					if manifest_dict["hasInventory"]:
						if "inventoryType" in manifest_dict.keys():
							c = "inventoryType"
							if c not in includedClasses:
								includedClasses.append(c)
								copy_file(os.path.join(build_java_dir, "registry", manifest_dict["inventoryType"]+".java"), os.path.join(build_java_dir, "registry", manifest_dict["inventoryType"]+".java"))
							create_file(os.path.join(build_java_dir, "registry", manifest_dict["class"]+".java"), readf_file(os.path.join(sourcesdir, "registry", "Inventory.java.txt")), manifest_dict)
				statename = manifest_dict["blockstatetype"]
				if tname.lower() == "custom":
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(project_path, manifest_dict["blockmodel"]), manifest_dict))
				else:
					create_file(os.path.join(block_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_models", tname+".json"), manifest_dict))
				create_file(os.path.join(item_models_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "item_models", "BlockItem.json"), manifest_dict))
				if statename.lower() == "custom":
					create_file(os.path.join(blockstates_assets_dir, cid+".json"), readf_file(os.path.join(project_path, manifest_dict["blockstate"]), manifest_dict))
				else:
					create_file(os.path.join(blockstates_assets_dir, cid+".json"), readf_file(os.path.join(commons_path, "blockstates", statename+".json"), manifest_dict))
				copy_textures(content_type, cid, manifest_dict, project_path, block_textures_assets_dir)
				dtype = manifest_dict[f"mod.{content_type}.{cid}.droptype"]
				if dtype.lower() != "none":
					create_file(os.path.join(block_loot_table_dir, cid+".json"), readf_file(os.path.join(commons_path, "block_loot_tables", dtype+".json"), manifest_dict))
			elif content_type == "recipe":
				create_file(os.path.join(recipes_dir, cid+".json"), readf_file(os.path.join(commons_path, "recipes", tname+".json"), manifest_dict))

			if content_type in ["armormaterial", "toolmaterial"]:
				create_file(os.path.join(build_java_dir, "registry", cid+".java"), readf_file(os.path.join(sourcesdir, "registry", tname+".java.txt"), manifest_dict))
			if content_type == "tool":
				create_file(os.path.join(build_java_dir, "registry", manifest_dict[f"mod.{content_type}.{cid}.class"]+".java"), readf_file(os.path.join(sourcesdir, "registry", "ToolItem.java.txt"), manifest_dict))

			if content_type in ["item", "block", "food", "fuel", "armor", "tool"]:
				if "langs" in manifest_dict[f"mod.{content_type}.{cid}.keys"]:
					for lang in manifest_dict[f"mod.{content_type}.{cid}.langs"]:
						if lang not in langdict.keys():
							langdict[lang] = {}
						langdict[lang][f"{content_type}.{modmcpath}.{cid}"] = manifest_dict[f"mod.{content_type}.{cid}.{lang}"]
				langdict["en_us"][f"{content_type}.{modmcpath}.{cid}"] = manifest_dict[f"mod.{content_type}.{cid}.title"]

	if "mod.langs" in manifest_dict.keys():
		for lang in manifest_dict["mod.langs"]:
			if lang not in langdict.keys():
				langdict[lang] = {}
			langdict[lang][f"itemGroup.{modmcpath}.general"] = manifest_dict[f"mod.{lang}"]
	langdict["en_us"][f"itemGroup.{modmcpath}.general"] = manifest_dict["mod.title"]

	for lang in langdict.keys():
		with open(os.path.join(lang_dir, lang+".json"),"w") as f:
			json.dump(langdict[lang], f)

	if "fabric" in manifest_dict["modloader"]:
		create_file(os.path.join(builddir, "src", "main", "resources", "fabric.mod.json"), readf_file(os.path.join(sourcesdir, "fabric.mod.json"), manifest_dict))

def copy_textures(content_type, cid, manifest_dict, project_path, dest_dir):
	if f"mod.{content_type}.{cid}.texture" in manifest_dict.keys():
		tex = manifest_dict[f"mod.{content_type}.{cid}.texture"]
		if "/" in tex: tex2 = tex.rsplit("/",maxsplit=1)[1]
		elif "\\" in tex: tex2 = tex.rsplit("\\",maxsplit=1)[1]
		else: tex2 = ""
		copy_file(os.path.join(project_path, tex), os.path.join(dest_dir, tex2))
	if f"mod.{content_type}.{cid}.{cid}_top" in manifest_dict.keys():
		tex = manifest_dict[f"mod.{content_type}.{cid}.{cid}_top"]
		if "/" in tex: tex2 = tex.rsplit("/",maxsplit=1)[1]
		elif "\\" in tex: tex2 = tex.rsplit("\\",maxsplit=1)[1]
		copy_file(os.path.join(project_path, tex), os.path.join(dest_dir, tex2))
	if f"mod.{content_type}.{cid}.{cid}_bottom" in manifest_dict.keys():
		tex = manifest_dict[f"mod.{content_type}.{cid}.{cid}_bottom"]
		if "/" in tex: tex2 = tex.rsplit("/",maxsplit=1)[1]
		elif "\\" in tex: tex2 = tex.rsplit("\\",maxsplit=1)[1]
		copy_file(os.path.join(project_path, tex), os.path.join(dest_dir, tex2))
	if f"mod.{content_type}.{cid}.{cid}_side" in manifest_dict.keys():
		tex = manifest_dict[f"mod.{content_type}.{cid}.{cid}_side"]
		if "/" in tex: tex2 = tex.rsplit("/",maxsplit=1)[1]
		elif "\\" in tex: tex2 = tex.rsplit("\\",maxsplit=1)[1]
		copy_file(os.path.join(project_path, tex), os.path.join(dest_dir, tex2))

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
		return None

def readf(data, d):
	# r = re.compile("\\$\\{.*\\}")
	if "$%f" in d.keys():
		data = data.replace("$%f", d["$%f"])
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
			print(f"Critical internal error! {key} not found in dictionary passed to readf!")
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
				print(f"Critical internal error! {key} not found in dictionary passed to readf!")
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
			# print(f"Checking if {key} is defined")
			j = data.find("---end",n)
			if key in d.keys():
				l = d[key]
				data2.append(data[n:j])
				j += 6
			else:
				j += 6
		data2.append(data[j:])
		data = "".join(data2)

	while any(["${"+key+"}" in data for key in d.keys()]):
		for key in d.keys():
			data = data.replace("${"+key+"}", str(d[key]))
	# data2 = []
	# i = 0
	# for match in r.finditer(data):
		# data2.append(data[i:match.start()])
		# i = match.end()
	# data2.append(data[i:])
	# return "".join(data2)
	if "forge" in d["modloader"]:
		for word in ["PICKAXES", "SHOVELS", "SWORDS", "HOES", "AXES"]:
			data = data.replace(word, word[:-1])
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

def readDictFile(fname, d={}):
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
								d[f"{k}.list.{len(d[k])}"] = v
								d[k].append(v)
							else:
								d[f"{k}.list.{len(d[k])}"] = v
								d[k] += v
						else:
							d[ns].append(v)
					else:
						k = name[1:]
						if k not in d.keys():
							d[f"{k}.list.0"] = v
							d[k] = [v]
						elif type(d[k]) is list:
							d[f"{k}.list.{len(d[k])}"] = v
							d[k].append(v)
						else:
							d[f"{k}.list.{len(d[k])}"] = v
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
Minecraft Multiple Mod Environment Compiler v0.2
Very much unfinished, currently only supports fabric 1.16.5 and 1.17.
Usage:
	python m3ec.py path modenv""")
		exit()
	else:
		build(sys.argv[1], " ".join(sys.argv[2:]))


