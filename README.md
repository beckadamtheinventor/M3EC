# M3EC

## Minecraft Multi Mod Environment Compiler
Version 0.4

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
Documentation can be found in the `docs` folder of this repository.

## Usage
To build a project:
+ `python m3ec.py path_to_mod_dir modenv`
Example:
`python m3ec.py testrubymod fabric1.18.1`

Valid `modenv`s:
+ fabric (builds all supported game versions for fabric)
+ fabric1.16.5
+ fabric1.17.1
+ fabric1.18.1
+ forge (builds all supported game versions for forge)
+ forge1.12.2 (coming soon)
+ forge1.16.5 (partial support)
+ forge1.17.1 (coming soon)
+ all (builds all supported mod environments and game versions)
+ 1.16.5 (builds all supported 1.16.5 mod environments)
+ 1.17.1 (builds all supported 1.17.1 mod environments)
+ 1.18.1 (builds all supported 1.18.1 mod environments)
+ 1.12.2 (builds all supported 1.12.2 mod environments)


Once the mod project is built, you can use your choice of java IDEs (such as IntelliJ) to build the mod's jar file.

Alernatively you can compile and/or test the mod from the terminal by appending to the end of the project build command.
- `buildjar` build the mod jar file.
- `runclient` launch an offline client with the mod installed.
- `runserver` launch an offline server with the mod installed.
Your mod's jar file will be in the build/libs directory of the built project.

When building, the program may prompt for a Java jdk path for a specific jdk version.
On Windows you can find your java installations somewhere in `C:\\Program Files\\Java\\` or `C:\\Program Files (x86)\\Java\\`.
On Linux, they will be somewhere in or around `/usr/lib/jvm/`.



## Features
- simple items
- foods with or without effect attributes
- simple single-texture blocks
- grass-block-like 3-texture blocks
- grass/flower-like single-texture cross blocks
- fortune-able blocks (such as ores)
- item dropping blocks (such as campfires)
- recipes of all default vanilla types
- as many languages as supplied

## Currently Broken Features
- armor and armor materials
- tools and tool materials
