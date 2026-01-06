from game.systems.enums.item_type import Item_Type

ITEM_DEFINITIONS = {
    "basic_sword": {
        "name": "Basic Sword",
        "category": Item_Type.WEAPON,
        "stackable": False,
        "unique": True,
        "stats": {"damage": +7},
        "effect": None,
        "value": 90
    },
    
    "improved_sword": {
        "name": "Improved Sword",
        "category": Item_Type.WEAPON,
        "stackable": False,
        "unique": True,
        "stats": {"damage": +20},
        "effect": None,
        "value": 300
    },

    "venom_fang_dagger": {
    "name": "Venom Fang Dagger",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": True,
    "stats": {"damage": +3},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.99, # 0.80
        "status": {
            "id": "poison",
            "magnitude": 2,
            "duration": 3,
        }
        }
    ],
    "value": 150
    },

    "cracked_warhammer": {
    "name": "Cracked Warhammer",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": True,
    "stats": {"damage": +6},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.96, #0,45
        "status": {
            "id": "weakened",
            "duration": 4,
            "magnitude": 0.8,
        }
        }
    ],
    "value": 160
    },

    "frostbrand_sword": {
    "name": "Frostbrand Sword",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": True,
    "stats": {"damage": +5},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.99, #0,15
        "status": {
            "id": "stun",
            "duration": 2,
            "magnitude": None,
        }
        }
    ],
    "value": 145
    },

    "bloodletter_axe": {
    "name": "Bloodletter Axe",
    "category": Item_Type.WEAPON,
    "stackable": False,
    "unique": True,
    "stats": {"damage": +7},
    "effect": [
        {
        "trigger": "on_hit",
        "chance": 0.95, # 0,60
        "status": {
            "id": "strength_up",
            "duration": 2,
            "magnitude": 1.25,
            "target": "self"
        }
        }
    ],
    "value": 170
    },

    "basic_armor": {
        "name": "Basic Armor",
        "category": Item_Type.ARMOR,
        "stackable": False,
        "unique": True,
        "stats": {"defence": +8},
        "effect": None,
        "value": 90
    },

    "improved_armor": {
        "name": "Improved Armor",
        "category": Item_Type.ARMOR,
        "stackable": False,
        "unique": True,
        "stats": {"defence": +25},
        "effect": None,
        "value": 400
    },

    "ring_of_vital_flow": {
    "name": "Ring of Vital Flow",
    "category": Item_Type.RING,
    "stackable": False,
    "unique": True,
    "stats": None,
    "effect": [
        {
        "trigger": "on_equip",
        "status": {
            "id": "regen",
            "duration": -1,   # infinite while equipped
            "magnitude": 1
        }
        }
    ],
    "value": 75
    },

    "ring_of_iron_will": {
    "name": "Ring of Iron Will",
    "category": Item_Type.RING,
    "stackable": False,
    "unique": True,
    "stats": {"stun_resist": 0.50},
    "effect": None,
    "value": 65
    },

    "ring_of_corruption": {
    "name": "Ring of Corruption",
    "category": Item_Type.RING,
    "stackable": False,
    "unique": True,
    "stats": None,
    "effect": [
        {
        "trigger": "on_turn",
        "status": {
            "id": "strength_up",
            "duration": 2,
            "magnitude": 1.15
        }
        }
    ],
    "value": 100
    },

    "small_healing_potion": {
        "name": "Small Healing Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {"heal": 30},
        "value": 15
    },

    "medium_healing_potion": {
        "name": "Medium Healing Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {"heal": 70},
        "value": 30
    },

    "grand_healing_potion": {
        "name": "Grand Healing Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {"heal": 150},
        "value": 60
    },

    "stamina_tonic": {
        "name": "Stamina Tonic",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "restore_resource": 20
        },
        "value": 18
    },

    "second_wind_potion": {
        "name": "Second Wind Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "restore_resource": 40
        },
        "value": 32
    },

    "antivenom_vial": {
        "name": "Antivenom Vial",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "poison"
        },
        "value": 30
    },

    "cooling_salve": {
        "name": "Cooling Salve",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "burn"
        },
        "value": 30
    },

    "coagulant_tonic": {
        "name": "Coagulant Tonic",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "bleed"
        },
        "value": 30
    },

    "battle_elixir": {
        "name": "Battle Elixir",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "weakened"
        },
        "value": 30
    },

    "reinforcement_draught": {
        "name": "Reinforcement Draught",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "remove_status": "armor_down"
        },
        "value": 30
    },

    "explosive_potion": {
        "name": "Explosive Potion",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {"damage": 25},
        "value": 25
    },

    "lesser_fortitude_draught": {
        "name": "Lesser Fortitude Draught",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "apply_status": {
                "id": "defending",
                "duration": 2,
                "magnitude": None
            }
        },
        "value": 20
    },

    "strength_elixir": {
        "name": "Strength Elixir",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "effect": {
            "apply_status": {
                "id": "strength_up",
                "duration": 3,
                "magnitude": None
            }
        },
        "value": 30
    },
    
    "volatile_concoction": {
        "name": "Volatile Concoction",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "apply_status": {
                "id": "strength_up",
                "duration": 2,
                "magnitude": None
            },
            "damage": 5
        },
        "value": 40
    },

    "sluggish_brew": {
        "name": "Sluggish Brew",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "apply_status": {
                "id": "weakened",
                "duration": 2,
                "magnitude": None
            }
        },
        "value": 25
    },

    "poison_flask": {
        "name": "Poison Flask",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": {
            "apply_status": {
                "id": "poison",
                "duration": 3,
                "magnitude": 1
            }
        },
        "value": 30
    },
    "regeneration_draught": {
        "name": "Regeneration Draught",
        "category": Item_Type.CONSUMABLE,
        "stackable": True,
        "unique": False,
        "effect": {
            "apply_status": {
                    "id": "regen",
                    "duration": 3,
                    "magnitude": 2
            }
        },
        "value": 40
    },

    "wolf_tooth": {
        "name": "Wolf Tooth",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 8
    },
    
    "slime_goop": {
        "name": "Slime Goop",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 5
    },
    
    "goblin_ear": {
        "name": "Goblin Ear",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 3
    },
    
    "broken_helm": {
        "name": "Broken Helm",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 13
    },

    "tarnished_insignia": {
        "name": "Tarnished Insignia",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 14
    },
    
    "rotted_bone": {
        "name": "Rotted Bone",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 4
    },
    
    "boar_tusk": {
        "name": "Boar Tusk",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 6
    },

    "matted_hide": {
        "name": "Matted Hide",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 15
    },
  
    "hardened_slime_core": {
        "name": "Hardened Slime Core",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 50
    },

    "charred_scale": {
        "name": "Charred Scale",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 140
    },

    "ashen_drake_claw": {
        "name": "Ashen Drake Claw",
        "category": Item_Type.SCRAP,
        "stackable": True,
        "unique": False,
        "stats": None,
        "effect": None,
        "value": 270
    },
}

