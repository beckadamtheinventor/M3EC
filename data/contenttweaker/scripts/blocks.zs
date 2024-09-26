#loader contenttweaker

import mods.contenttweaker.VanillaFactory;
import mods.contenttweaker.Block;

---iter mod.registry.block.names
var ${$%v^camel} = VanillaFactory.createBlock("$%v", <blockmaterial:${mod.block.$%v.material}>);
---if mod.block.$%v.lightopacity
${$%v^camel}.setLightOpacity(${mod.block.$%v.lightopacity});---fi
---if mod.block.$%v.lightlevel
${$%v^camel}.setLightValue(${mod.block.$%v.lightlevel});---fi
---if mod.block.$%v.hardness
${$%v^camel}.setBlockHardness(${mod.block.$%v.hardness});---fi
---if mod.block.$%v.resistance
${$%v^camel}.setBlockResistance(${mod.block.$%v.resistance});---fi
---if mod.block.$%v.toolclass
${$%v^camel}.setToolClass(${mod.block.$%v.toolclass});---fi
---if mod.block.$%v.toollevel
${$%v^camel}.setToolLevel(${mod.block.$%v.toollevel});---fi
${$%v^camel}.setBlockSoundType(<soundtype:${mod.block.$%v.sounds}>);
---if mod.block.$%v.slipperiness
${$%v^camel}.setSlipperiness(${mod.block.$%v.slipperiness});---fi
${$%v^camel}.register();
---end
