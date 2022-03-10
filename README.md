# M3EC

## Minecraft Multi Mod Environment Compiler
Version 0.6

This compiler/script operates on the mentality of "as few files as possible" to create a mod.
Check out the `testrubymod` folder for usage examples.
Currently it only supports a handful of Minecraft versions/modloaders.

M3EC is Licensed under the GPL version 3.

## Prerequisites
- Python 3.6 or higher.
- Building for MC versions prior to 1.17.x: Java JDK/OpenJDK 8.
- Building for MC versions 1.17.x: Java JDK/OpenJDK 16.
- Building for MC versions 1.18.x: Java JDK/OpenJDK 17.

## Documentation
Currently there isn't much documentation. It can be found in the `docs` folder of this repository.
There is also a website: https://beckadamtheinventor.github.io/M3EC.

## Usage
To build a project:
+ `python m3ec.py path_to_mod_dir modenv`
Example:
`python m3ec.py testrubymod fabric1.18.1`

### Supported Versions (Fabric)
- 1.16.5
- 1.17.x
- 1.18.x

### Supported Versions (Forge)
- 1.16.5

### Planned Versions (Forge)
- 1.12.2
- 1.17.x
- 1.18.x

Once the mod project is built, you can use your choice of java IDEs (such as IntelliJ) to build the mod's jar file, or build and/or test the mod from the terminal by appending to the end of the M3EC build command with the any of the following:
- `buildjar` build the mod jar file.
- `runclient` launch an offline client with the mod installed.
- `runserver` launch an offline server with the mod installed.
Your mod's jar file will be in the build/libs directory of the built project.

When building, the program may prompt for a Java jdk path for a specific jdk version.
On Windows, Mac, and Linux M3EC should detect a JDK automatically. If it can't find the needed version it will prompt for a path to it.



## Features
- simple items
- foods without effect attributes
- simple single-texture blocks
- grass-block-like 3-texture blocks
- grass/flower-like single-texture cross blocks
- fortune-able blocks (such as ores)
- item dropping blocks (such as campfires)
- recipes of all default vanilla types
- as many languages as supplied
- tools and tool materials

## Planned Features
- armor and armor materials
- multiple creative tabs
- scriptable block/item behaviours
- more generation options
- custom dimensions
