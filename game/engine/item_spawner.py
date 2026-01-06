from game.core.Item_class import Items
from game.definitions.item_definitions import ITEM_DEFINITIONS

def spawn_item(item_type):
    template = ITEM_DEFINITIONS[item_type].copy()

    item_obj = Items(
        name      = template["name"],
        category  = template["category"],
        stackable = template["stackable"],
        unique    = template["unique"],
        stats     = template.get("stats"),
        effect    = template.get("effect"),
        value     = template["value"],
    )
    item_obj.id = item_type

    # Attach optional behavior data
    if "on_hit_status" in template:
        item_obj.on_hit_status = template["on_hit_status"]

    if "on_equip_status" in template:
        item_obj.on_equip_status = template["on_equip_status"]

    return item_obj

