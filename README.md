# M3EC

## Minecraft Multi Mod Environment Compiler
Version 0.9

This compiler/script operates on the mentality of "as few files as possible" to create a mod.
Check out the `testrubymod` folder for usage examples.

M3EC is Licensed under the GPL version 3.


## About
M3EC is a script that turns a series of simple content manifest files into the code required to build a Minecraft Mod. It has support for a variety of content types, such as simple blocks/items, tools/tool materials, ores, and more.
M3EC mod building is designed to require as few files as possible. Have you ever found yourself adding countless files to countless nested directories just to make a simple content mod? M3EC can build a working content mod for all the versions and modloaders it supports with only 3 files: the mod's main manifest, a png image, and a content manifest!

M3EC supports building for a wide variety of modloaders and game versions from fabric 1.16.5 to 1.19 and forge 1.16.5, 1.18.2, and 1.19. (with 1.12.2 support planned) It can even build and launch the mod for you and select the appropriate JDK automatically!


## Prerequisites
- Python 3.6 or higher.
- Building for MC versions prior to 1.17.x: Java JDK/OpenJDK 8.
- Building for MC versions 1.17.x: Java JDK/OpenJDK 16.
- Building for MC versions 1.18.x: Java JDK/OpenJDK 17.


## Documentation
Currently there isn't much documentation. It can be found in the `docs` folder of this repository.
There is also a website: https://beckadamtheinventor.github.io/M3EC.
However, there is an example mod (with most if not all features included) to help get you started.

## Usage
To build a project:
+ `python m3ec.py path_to_mod_dir modenv`
Example:
`python m3ec.py testrubymod fabric1.18.1`


### Supported Versions (Fabric)
- 1.16.5
- 1.17.x
- 1.18.x
- 1.19
- 1.19.2
- 1.19.3
- 1.19.4
- 1.20.1

### Supported Versions (Forge)
- 1.16.5
- 1.18.1
- 1.18.2
- 1.19
- 1.19.2
- 1.20.1

### Planned Versions (Forge)
- 1.12.2
- 1.17.x

Once the mod project is built, you can use your choice of java IDEs (such as IntelliJ) to build the mod's jar file, or build and/or test the mod from the terminal by appending to the end of the M3EC build command with the any of the following:
- `buildjar` build the mod jar file.
- `runclient` launch an offline client with the mod installed.
- `runserver` launch an offline server with the mod installed.
Your mod's jar file will be in the build/libs directory of the built project.

When building, the program may prompt for a Java jdk path for a specific jdk version.
On Windows, Mac, and Linux M3EC should detect a JDK automatically. If it can't find the needed version you can enter the path manually.



## Features
- simple items
- foods (without effect attributes)
- simple single-texture blocks
- grass-block-like 3-texture blocks
- grass/flower-like single-texture cross blocks
- fortunable blocks (such as ores)
- item dropping blocks (such as campfires)
- all vanilla recipe types
- as many languages as you're willing to add
- tools and tool materials
- armor and armor materials
- custom block/item behaviour (requires custom java class)

## Planned Features
- multiple creative tabs
- scriptable block/item behaviours
- more generation options
- custom dimensions
