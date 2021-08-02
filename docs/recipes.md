
# M3EC Recipe documentation

Shapeless recipe:
```
@:      recipe
recipe: ShapelessRecipe
+ingredients: minecraft:diamond
+ingredients: minecraft:diamond_block
+ingredients: minecraft:apple
result:       minecraft:diamond_horse_armor
count:        1
```

Shaped recipe:
```
@:        recipe
recipe:   ShapedRecipe
+pattern:  " . "
+pattern:  ".d."
+pattern:  " . "
+itemkeys: "."
+items:    minecraft:cobblestone
+itemkeys: "d"
+items:    minecraft:diamond
result:    minecraft:obsidian
count:     1
```

