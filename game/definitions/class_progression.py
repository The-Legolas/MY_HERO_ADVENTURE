

CLASS_PROGRESSION = {
    "warrior": {
        "level_cap": 10,
        "xp_curve": "linear",
        "xp_per_level": [
            0,    # level 1
            100,
            200,
            400,
            700,
            1000,
            1300,
            1600,
            2000,
            2500,
            3000,  # level 10
        ],
        "level_rewards": {

            2: {
                "stats": {"hp": +10, "damage": +2, "defence": +3, "resource": +10},
                "skills": ["war_cry"],
            },
            3: {
                "stats": {"hp": +10, "damage": +2, "defence": +3, "resource": +10},
                "skills": ["iron_guard", "exhausting_assault"],
            },
            4: {
                "stats": {"hp": +10, "damage": +2, "defence": +3, "resource": +10},
                "skills": ["poison_strike"],
            },
            5: {
                "stats": {"hp": +10, "damage": +2, "defence": +3, "resource": +10},
                "skills": ["sundering_blow"],
            },
            6: {
                "stats": {"hp": +10, "damage": +2, "resource": +30},
            },
            7: {
                "stats": {"hp": +10, "damage": +2, "defence": +3, "resource": +10},
                "skills": ["concussive_strike"],
            },
            8: {
                "stats": {"hp": +10, "damage": +2, "defence": +3, "resource": +10},
                "skills": ["searing_thrust"],
            },
            9: {
                "stats": {"hp": +10, "damage": +2, "defence": +3, "resource": +10},
                "skills": ["rallying_breath"],
            },
            10: {
                "stats": {"hp": +10, "damage": +2, "defence": +3, "resource": +10},
                "skills": ["ultimate_rage"],
            },
        },
    },
}
