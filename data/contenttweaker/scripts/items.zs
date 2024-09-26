#loader contenttweaker

import mods.contenttweaker.VanillaFactory;
import mods.contenttweaker.Item;

---iter mod.registry.item.names
var ${$%v^camel} = VanillaFactory.createItem("$%v");
---if mod.item.$%v.maxstacksize
${$%v^camel}.maxStackSize = ${mod.item.$%v.maxstacksize};---fi
${$%v^camel}.beaconPayment = ${mod.item.$%v.beaconpayment^bool};
${$%v^camel}.register();
---end

---iter mod.registry.tool.names
var ${$%v^camel} = VanillaFactory.createItem("$%v");
${%v^camel}.toolClass = "${mod.tool.$%v.toolclass^lower}";
${%v^camel}.toolLevel = "${mod.tool.$%v.toollevel}";
---end

---iter mod.registry.food.names
var ${$%v^camel} = VanillaFactory.createItemFood("$%v", 0);
---if mod.food.$%v.alwaysedible
${$%v^camel}.alwaysEdible = ${mod.food.$%v.alwaysedible^bool};---fi
---if mod.food.$%v.wolffood
${$%v^camel}.wolffood = ${mod.food.$%v.wolffood^bool};---fi
---if mod.food.$%v.saturation
${$%v^camel}.wolffood = ${mod.food.$%v.saturation};---fi
---if mod.food.$%v.hunger
${$%v^camel}.healamount = ${mod.food.$%v.hunger};---fi
${$%v^camel}.register();
---end