
import os, sys, subprocess, shutil

from .util import *

def maybe_run_gradle(path, modenv, javaver, md):
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

	if "buildjar" in modenvlow or "build" in modenvlow:
		print("\n-----------------------------------------------\n\tbuilding JAR\n")
		subprocess.Popen([os.path.join(path, fname), "build", "jar", javapath], cwd=path).wait()
		jd = os.path.join(os.path.dirname(path), "built_mod_jars")
		make_dir(jd)
		for f in walk(os.path.join(path, "build", "libs")):
			shutil.copy(f, os.path.join(jd, os.path.splitext(os.path.basename(f))[0]+"-"+md["modloader"]+md["gameversion"]+".jar"))
	if "runclient" in modenvlow:
		print("\n-----------------------------------------------\n\tRunning Client\n")
		subprocess.Popen([os.path.join(path, fname), "runClient", javapath], cwd=path).wait()
	if "runserver" in modenvlow:
		print("\n-----------------------------------------------\n\tRunning Server\n")
		subprocess.Popen([os.path.join(path, fname), "runServer", javapath], cwd=path).wait()


def find_java_version(javaver):
	if sys.platform.startswith("win32"):
		for p in ["Program Files\\Eclipse Adoptium", "Program Files\\Java", "Program Files (x86)\\Java", "Program Files (x86)\\Eclipse Adoptium"]:
			javapath = find_jdk(f"C:\\{p}", javaver)
			if javapath is not None:
				break
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
				if d.startswith("jdk") and (f"-{javaver}" in d or f"1.{javaver}" in d):
					return os.path.join(root, d)
	return None
