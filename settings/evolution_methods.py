#--------------------------------------------------------------------
# linoone: evolution_methods.py
#
# Project settings for evolution methods.
#--------------------------------------------------------------------
from enum import Enum

EvolutionParamTypes = Enum("EvolutionParamTypes", "none level item gt_number")

# Evolution methods metadata settings that can't be automatically
# determined from source files inspection.
class EvolutionMethodSettings:
    def __init__(self):
        self.evolution_methods = {
            "1": {
                "id": "EVO_FRIENDSHIP",
                "description": "High friendship",
                "param_type": EvolutionParamTypes.none,
            },
            "2": {
                "id": "EVO_FRIENDSHIP_DAY",
                "description": "High friendship during day",
                "param_type": EvolutionParamTypes.none,
            },
            "3": {
                "id": "EVO_FRIENDSHIP_NIGHT",
                "description": "High friendship during night",
                "param_type": EvolutionParamTypes.none,
            },
            "4": {
                "id": "EVO_LEVEL",
                "description": "Level up",
                "param_type": EvolutionParamTypes.level,
            },
            "5": {
                "id": "EVO_TRADE",
                "description": "Trade",
                "param_type": EvolutionParamTypes.none,
            },
            "6": {
                "id": "EVO_TRADE_ITEM",
                "description": "Trade with item",
                "param_type": EvolutionParamTypes.item,
            },
            "7": {
                "id": "EVO_ITEM",
                "description": "Use item",
                "param_type": EvolutionParamTypes.item,
            },
            "8": {
                "id": "EVO_LEVEL_ATK_GT_DEF",
                "description": "Attack > Defense on level up",
                "param_type": EvolutionParamTypes.level,
            },
            "9": {
                "id": "EVO_LEVEL_ATK_EQ_DEF",
                "description": "Attack == Defense on level up",
                "param_type": EvolutionParamTypes.level,
            },
            "10": {
                "id": "EVO_LEVEL_ATK_LT_DEF",
                "description": "Attack < Defense on level up",
                "param_type": EvolutionParamTypes.level,
            },
            "11": {
                "id": "EVO_LEVEL_SILCOON",
                "description": "Silcoon personality on level up",
                "param_type": EvolutionParamTypes.level,
            },
            "12": {
                "id": "EVO_LEVEL_CASCOON",
                "description": "Cascoon personality on level up",
                "param_type": EvolutionParamTypes.level,
            },
            "13": {
                "id": "EVO_LEVEL_NINJASK",
                "description": "Ninjask",
                "param_type": EvolutionParamTypes.level,
            },
            "14": {
                "id": "EVO_LEVEL_SHEDINJA",
                "description": "Shedinja",
                "param_type": EvolutionParamTypes.level,
            },
            "15": {
                "id": "EVO_BEAUTY",
                "description": "Beauty",
                "param_type": EvolutionParamTypes.gt_number,
            },
        }


    def get_label(self, method, param, items):
        """
        Builds the human-friendly label of the evolution method.
        """
        evo_method = self.evolution_methods[method]
        if evo_method["param_type"] == EvolutionParamTypes.none:
            return evo_method["description"]
        elif evo_method["param_type"] == EvolutionParamTypes.level:
            return "%s (%s)" % (evo_method["description"], param)
        elif evo_method["param_type"] == EvolutionParamTypes.item:
            return "%s %s" % (evo_method["description"], items[param]["name"])
        elif evo_method["param_type"] == EvolutionParamTypes.gt_number:
            return "%s > %s" % (evo_method["description"], param)
        else:
            return "UNKNOWN EVOLUTION METHOD"


evolution_methods = EvolutionMethodSettings()
