# M3EC

## Minecraft Multi Mod Environment Compiler
Version 0.2

This compiler/script operates on the mentality of "as few files as possible" to create a mod.
Check out the `testrubymod` folder for usage example.
Currently it only supports fabric 1.16.5 and 1.17. Forge support will (probably) come soon after it releases for 1.17.

M3EC is Licensed under the GPL version 3.


## Documentation
Documentation can be found in the `docs` folder of this repository.


## Usage

To build a given project for a given modloader for a specified game version:
+ `python m3ec.py path_to_mod_dir modenv`

Valid `modenv`s:
+ fabric1.16.5
+ fabric1.17.1
+ fabric1.17
+ forge1.16.5 (coming soon)
+ forge1.17.1 (coming soon)
+ forge1.12.2 (coming soon)
+ all (builds all supported mod environments and game versions)
+ 1.16.5 (builds for both forge and fabric)
+ 1.17.1 (builds for both forge and fabric)
+ 1.17 (builds for both forge and fabric)
+ 1.12.2 (builds for both forge and fabric)


Once the mod project is built, you can use your choice of java IDEs (such as IntelliJ) to build the mod's jar file.
Alernatively you can compile the mod from the terminal. Open a command window and navigate to the respective `modenv_build` folder within your peojct's source directory.
Then run this command:
+ `gradlew build jar`
Your mod's jar file will be in the build/libs directory.

If the build fails with an error such as `RELEASE_8 less than RELEASE_16` then you will need to tell gradle where the java version is that you need to use, because MC 1.17 uses Java 16 instead of versions prior which use Java 8.
Running the following command should fix the issue:
+ `gradlew build jar -Dorg.gradle.java.home=[path to java 16 jdk directory]`
On Windows this will be somewhere in `C:\\Program Files\\Java\\`.
On Linux, it will be somewhere in `/usr/lib/jvm/`.


## Features
- simple items
- foods with or without effect attributes
- simple single-texture blocks
- grass-block-like 3-texture blocks
- grass/flower-like single-texture cross blocks
- fortune-able blocks (such as ores)
- item dropping blocks (such as campfires)
- recipes of all default vanilla types
- armor and armor materials
- tools and tool materials
- as many languages as supplied
