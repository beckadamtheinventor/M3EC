# M3EC

## Minecraft Multi Mod Environment Compiler
Version 0.1

This compiler/script operates on the mentality of "as few files as possible" to create a mod.
Check out the `testrubymod` folder for usage example.
Currently it only supports fabric on mc 1.17. Forge support will (probably) come soon after it releases for 1.17.

## Usage
build for fabric 1.17:
+ python m3ec.py path_to_mod_dir fabric

build for forge: (eventually)
+ python m3ec.py path_to_mod_dir forge

Licensed under the GPL version 3.

## Features
- simple items
- foods without custom effect attributes
- simple single-texture blocks
- fortune-able blocks (such as ores)
- item dropping blocks (such as campfires)
- recipes of all methods from 1.16
- tools and tool materials
- armor and armor materials
- as many languages as supplied
