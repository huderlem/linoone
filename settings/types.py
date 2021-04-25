#--------------------------------------------------------------------
# linoone: types.py
#
# Project settings for Pokémon types.
#--------------------------------------------------------------------
from enum import Enum

# Pokémon types metadata that can't be automatically
# determined from source files inspection.
class TypesSettings:
    def __init__(self):
        self.types = {
            "0": {
                "icon_filepath": "graphics/types/normal.png",
            },
            "1": {
                "icon_filepath": "graphics/types/fight.png",
            },
            "2": {
                "icon_filepath": "graphics/types/flying.png",
            },
            "3": {
                "icon_filepath": "graphics/types/poison.png",
            },
            "4": {
                "icon_filepath": "graphics/types/ground.png",
            },
            "5": {
                "icon_filepath": "graphics/types/rock.png",
            },
            "6": {
                "icon_filepath": "graphics/types/bug.png",
            },
            "7": {
                "icon_filepath": "graphics/types/ghost.png",
            },
            "8": {
                "icon_filepath": "graphics/types/steel.png",
            },
            "9": {
                "icon_filepath": "graphics/types/mystery.png",
            },
            "10": {
                "icon_filepath": "graphics/types/fire.png",
            },
            "11": {
                "icon_filepath": "graphics/types/water.png",
            },
            "12": {
                "icon_filepath": "graphics/types/grass.png",
            },
            "13": {
                "icon_filepath": "graphics/types/electric.png",
            },
            "14": {
                "icon_filepath": "graphics/types/psychic.png",
            },
            "15": {
                "icon_filepath": "graphics/types/ice.png",
            },
            "16": {
                "icon_filepath": "graphics/types/dragon.png",
            },
            "17": {
                "icon_filepath": "graphics/types/dark.png",
            },
        }


types = TypesSettings()
