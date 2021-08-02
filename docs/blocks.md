
# M3EC Block documentation

Defining a simple, single block state "Ruby Ore" block:
```
@:               block
block:           SimpleBlock
# Defines the block as having only one blockstate
blockstatetype:  SimpleBlockState
contentid:         ruby_ore
title:             Ruby Ore
texture:           textures/ruby/ruby_ore.png

# ore drops ruby and is affected by fortune
droptype:          Fortunable
drops:             modid:ruby

# hardness and resistance of emerald ore
hardness:          ${mc.emerald_ore.hardness}
resistance:        ${mc.emerald_ore.resistance}
# block material type
material:          STONE
# breaks with pickaxes
toolclass:         PICKAXES
# breaks with iron level pickaxe or higher
toollevel:         2
# requires the correct tool to drop items
requiresTool:      .requiresTool()
# Sounds like stone
sounds:            STONE
```


