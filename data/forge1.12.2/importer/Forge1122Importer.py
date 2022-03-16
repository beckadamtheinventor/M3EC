
import os

class Forge1122Importer:
	def __init__(self, source):
		self.source = source
		self.files = []
		self.paths = []
		self.manifest = {}
		self.ScanTree(source)

	def ScanTree(self, path):
		sourcepath = os.path.join(path, "main", "java")
		prefix = author = modname = None

		for root, dirs, files in os.walk(sourcepath):
			for d in dirs:
				prefix = d
				break
			break
		if prefix is None:
			raise FileNotFoundError(f"Missing project directory structure in {path}")

		for root, dirs, files in os.walk(os.path.join(sourcepath, prefix)):
			for d in dirs:
				author = d
				break
			break
		if author is None:
			raise FileNotFoundError(f"Missing project directory structure in {path}")

		for root, dirs, files in os.walk(os.path.join(sourcepath, prefix, author)):
			for d in dirs:
				modname = d
				break
			break
		if modname is None:
			raise FileNotFoundError(f"Missing project directory structure in {path}")

		self.manifest["mod.prefix"] = prefix
		self.manifest["mod.author"] = author
		self.manifest["mod.mcpath"] = modname

		with open(os.path.join(path, "main", "resources", "mcmod.info")) as f:
			mcmodinfo = json.load(f)

		self.manifest["mod.mcmodinfo"] = mcmodinfo
		self.manifest["mod.title"] = mcmodinfo["name"]
		self.manifest["mod.description"] = mcmodinfo["description"]
		self.manifest["mod.homepage"] = mcmodinfo["url"]
		self.manifest["mod.credits"] = mcmodinfo["credits"]
		self.manifest["mod.icon"] = mcmodinfo["logoFile"]

	def GetManifestString(self):
		modprefix = self.manifest["mod.prefix"]
		modauthor = self.manifest["mod.author"]
		modclass = self.manifest["mod.class"]
		modmcpath = self.manifest["mod.mcpath"]
		modtitle = self.manifest["mod.title"]
		moddescription = self.manifest["mod.description"]
		modhomepage = self.manifest["mod.homepage"]
		modiconitem = self.manifest["mod.iconItem"]
		return f"""
@:         manifest
mod:
.prefix:      {modprefix}
.author:      {modauthor}
.class:       {modclass}
.mcpath:      {modmcpath}
.title:       {modtitle}
.description: {moddescription}
.homepage:    {modhomepage}
+.paths:      items
+.paths:      blocks
+.paths:      recipes
+.paths:      armor
+.paths:      tools
+.paths:      ores
.textures:    textures
.iconItem: {modiconitem}
"""

