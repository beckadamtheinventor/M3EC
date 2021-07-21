
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
							manifest_dict[f"mod.{content_type}.{cid}.uppercased"] = cid.replace(" ", "_").upper()
							manifest_dict[f"mod.{content_type}.{cid}.mcpath"] = cid.replace(" ", "_").lower()
						else:
							print(f"Found more than one instance of {content_type} \"{cid}\"! Aborting.")
							exit()
					else:
						print(f"Warning: Skipping file \"{fname}\" due to missing contentid.")
				else:
					print(f"Warning: Skipping file \"{fname}\" due to missing content type.")

	# for key in manifest_dict.keys():
		# print(f"{key}: {manifest_dict[key]}")

	if "fabric1.17" in modenv:
		print("Building fabric 1.17 mod project")
		path = project_path
		make_dir(os.path.join(path, "fabric1.17_build"))

		src = os.path.join(source_path, "fabric1.17", "gradle")
		dest = os.path.join(path, "fabric1.17_build")
		make_dir(os.path.join(dest, "gradle"))
		make_dir(os.path.join(dest, "gradle", "wrapper"))
		copy_file(os.path.join(src, "gradle", "wrapper", "gradle-wrapper.jar"), os.path.join(dest, "gradle", "wrapper", "gradle-wrapper.jar"))
		copy_file(os.path.join(src, "gradle", "wrapper", "gradle-wrapper.properties"), os.path.join(dest, "gradle", "wrapper", "gradle-wrapper.properties"))
		copy_file(os.path.join(src, "build.gradle"), os.path.join(dest, "build.gradle"))
		copy_file(os.path.join(src, "gradlew"), os.path.join(dest, "gradlew"))
		copy_file(os.path.join(src, "gradlew.bat"), os.path.join(dest, "gradlew.bat"))
		copy_file(os.path.join(src, "settings.gradle"), os.path.join(dest, "settings.gradle"))
		create_file(os.path.join(dest, "gradle.properties"), readf_file(os.path.join(src, "gradle.properties.txt"), manifest_dict))

		make_dir(os.path.join(path, "fabric1.17_build", "src"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets", modmcpath))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets", modmcpath, "blockstates"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets", modmcpath, "lang"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets", modmcpath, "models"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets", modmcpath, "models", "block"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets", modmcpath, "models", "item"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets", modmcpath, "textures"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets", modmcpath, "textures", "blocks"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "assets", modmcpath, "textures", "items"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "data"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "data", modmcpath))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "data", modmcpath, "loot_tables"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "blocks"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "chests"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "entities"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "gameplay"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "resources", "data", modmcpath, "recipes"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "java"))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "java", prefix))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "java", prefix, modauthor.lower()))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "java", modmcpathdir))
		make_dir(os.path.join(path, "fabric1.17_build", "src", "main", "java", modmcpathdir, "registry"))

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

	if "fabric" in modenv:
		print("Building fabric mod project")
		path = project_path
		make_dir(os.path.join(path, "fabric_build"))

		src = os.path.join(source_path, "fabric", "gradle")
		dest = os.path.join(path, "fabric_build")
		make_dir(os.path.join(dest, "gradle"))
		make_dir(os.path.join(dest, "gradle", "wrapper"))
		copy_file(os.path.join(src, "gradle", "wrapper", "gradle-wrapper.jar"), os.path.join(dest, "gradle", "wrapper", "gradle-wrapper.jar"))
		copy_file(os.path.join(src, "gradle", "wrapper", "gradle-wrapper.properties"), os.path.join(dest, "gradle", "wrapper", "gradle-wrapper.properties"))
		copy_file(os.path.join(src, "build.gradle"), os.path.join(dest, "build.gradle"))
		copy_file(os.path.join(src, "gradlew"), os.path.join(dest, "gradlew"))
		copy_file(os.path.join(src, "gradlew.bat"), os.path.join(dest, "gradlew.bat"))
		copy_file(os.path.join(src, "settings.gradle"), os.path.join(dest, "settings.gradle"))
		create_file(os.path.join(dest, "gradle.properties"), readf_file(os.path.join(src, "gradle.properties.txt"), manifest_dict))

		make_dir(os.path.join(path, "fabric_build", "src"))
		make_dir(os.path.join(path, "fabric_build", "src", "main"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets", modmcpath))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets", modmcpath, "blockstates"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets", modmcpath, "lang"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets", modmcpath, "models"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets", modmcpath, "models", "block"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets", modmcpath, "models", "item"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets", modmcpath, "textures"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets", modmcpath, "textures", "blocks"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "assets", modmcpath, "textures", "items"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "data"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "data", modmcpath))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "data", modmcpath, "loot_tables"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "blocks"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "chests"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "entities"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "gameplay"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "resources", "data", modmcpath, "recipes"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "java"))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "java", prefix))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "java", prefix, modauthor.lower()))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "java", modmcpathdir))
		make_dir(os.path.join(path, "fabric_build", "src", "main", "java", modmcpathdir, "registry"))

		build_resources(project_path, "fabric", manifest_dict)

		data = readf_file(os.path.join(source_path, "fabric", "MainClass.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric/MainClass.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric_build", "src", "main", "java", modmcpathdir, f"{modclass}.java"), data)

		data = readf_file(os.path.join(source_path, "fabric", "registry", "ModBlocks.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric/registry/ModBlocks.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric_build", "src", "main", "java", modmcpathdir, "registry", "ModBlocks.java"), data)

		data = readf_file(os.path.join(source_path, "fabric", "registry", "ModItems.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"fabric/registry/ModItems.java.txt\"")
		else:
			create_file(os.path.join(path, "fabric_build", "src", "main", "java", modmcpathdir, "registry", "ModItems.java"), data)

	if "forge" in modenv:
		print("Building forge mod project")
		make_dir(os.path.join(path, "forge_build"))
		make_dir(os.path.join(path, "forge_build", "src"))
		make_dir(os.path.join(path, "forge_build", "src", "main"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets", modmcpath))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets", modmcpath, "blockstates"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets", modmcpath, "lang"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets", modmcpath, "models"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets", modmcpath, "models", "block"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets", modmcpath, "models", "item"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets", modmcpath, "textures"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets", modmcpath, "textures", "blocks"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "assets", modmcpath, "textures", "items"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "data"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "data", modmcpath))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "data", modmcpath, "loot_tables"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "blocks"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "chests"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "entities"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "data", modmcpath, "loot_tables", "gameplay"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "resources", "data", modmcpath, "recipes"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "java"))
		make_dir(os.path.join(path, "forge_build", "src", "main", "java", prefix))
		make_dir(os.path.join(path, "forge_build", "src", "main", "java", prefix, modauthor.lower()))
		make_dir(os.path.join(path, "forge_build", "src", "main", "java", modmcpathdir))
		make_dir(os.path.join(path, "forge_build", "src", "main", "java", modmcpathdir, "init"))

		build_resources(project_path, "forge", manifest_dict)

		data = readf_file(os.path.join(source_path, "forge", "MainClass.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge/MainClass.java.txt\"")
		else:
			create_file(os.path.join(path, "forge_build", "src", "main", "java", modmcpathdir, f"{modclass}.java"), data)

		data = readf_file(os.path.join(source_path, "forge", "init", "ModBlocks.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge/init/ModBlocks.java.txt\"")
		else:
			create_file(os.path.join(path, "forge_build", "src", "main", "java", modmcpathdir, "init", "ModBlocks.java"), data)

		data = readf_file(os.path.join(source_path, "forge", "init", "ModItems.java.txt"), manifest_dict)
		if data is None:
			print("Warning: Failed to read source \"forge/init/ModItems.java.txt\"")
		else:
			create_file(os.path.join(path, "forge_build", "src", "main", "java", modmcpathdir, "init", "ModItems.java"), data)

def build_resources(project_path, builddir, manifest_dict):
	source_path = os.path.join(os.path.dirname(__file__),"sources")
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
	langdict = {"en_us":{}}
	manifest_dict[f"mod.registry.blockitem.names"].clear()

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

	create_file(os.path.join(builddir, "src", "main", "resources", "fabric.mod.json"), readf_file(os.path.join(sourcesdir, "fabric.mod.json"), manifest_dict))

def copy_textures(content_type, cid, manifest_dict, project_path, dest_dir):
	if f"mod.{content_type}.{cid}.texture" in manifest_dict.keys():
		tex = manifest_dict[f"mod.{content_type}.{cid}.texture"]
		if "/" in tex: tex2 = tex.rsplit("/",maxsplit=1)[1]
		elif "\\" in tex: tex2 = tex.rsplit("\\",maxsplit=1)[1]
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


