
import os, sys, shutil, json

from .util import *

def ParseModTree(path):
	manifest_dict = {}
	d = root = dictDir(path)

	if "src" in d.keys():
		d = d["src"]

	if "main" in d.keys():
		d = d["main"]

	if "resources" in d.keys():
		resource_root = d["resources"]
		if "fabric.mod.json" in resource_root.keys():
			modloader = "fabric"
			with open(os.path.join(path, "src", "main", "resources", "fabric.mod.json")) as f:
				j = json.load(f)
			entrypoints = j["entrypoints"]["main"]
			modloaderversion = j["depends"]["fabricloader"]
			gameversion = j["depends"]["minecraft"]
			javaversion = j["depends"]["java"]
			mixins = j["mixins"]
			manifest_dict["mod.mcpath"] = j["id"]
			manifest_dict["mod.author"] = ", ".join(j["authors"])
			manifest_dict["mod.homepage"] = j["contact"]["homepage"]
			manifest_dict["mod.sources"] = j["contact"]["sources"]
			
		elif "META-INF" in resource_root.keys():
			modloader = "forge"
		else:
			return None

	if "java" in d.keys():
		java_root = d = d["java"]

	return manifest_dict
