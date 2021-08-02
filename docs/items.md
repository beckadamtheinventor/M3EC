
# M3EC Item documentation

Registering a simple stone rod item:
```
@:         item
item:      SimpleItem
contentid: stone_rod
texture:   textures/stone_rod.png
```

Registering a charcoal rod usable as fuel:
```
@:         fuel
fuel:      SimpleItem
contentid: charcoal_rod
texture:   textures/charcoal_rod.png
# burn time in game ticks. Coal has a burn time of 1600 for example.
burntime:  800
```

Registering a candy apple food item:
```
@:          food
food:       SimpleItem
contentid:  candy_apple
texture:    textures/candy_apple.png
# Hunger points and saturation modifier. An apple gives 2 and 2.4, respectively.
hunger:     1
saturation: 4
# probably makes the food quicker to eat?
snack:        .snack()
# makes the food always edible, even when the player is full.
alwaysEdible: .alwaysEdible()
# here you can add status effects to the food (TODO)
statusEffects:
```

