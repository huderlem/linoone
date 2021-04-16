#--------------------------------------------------------------------
# linoone: types.py
#
# Page generator for the Pokémon type pages. Each page lists the
# Pokémon that have each typing.
#--------------------------------------------------------------------
from generators.base_generator import BaseGenerator


class TypesGenerator(BaseGenerator):
    def prepare_template_data(self):
        """
        Prepares any additional data the page generator needs to
        render itself. Returns a dict of variables and/or functions
        that will be exposed to the template.
        """
        type_mons_map = create_type_mons_map(
            self.core_data["type_names"],
            self.core_data["mon_base_stats"],
            self.core_data["national_to_species"]
        )
        type_moves_map = create_type_moves_map(
            self.core_data["type_names"],
            self.core_data["moves"],
            self.core_data["move_names"]
        )
        return {
            "type_mons_map": type_mons_map,
            "type_moves_map": type_moves_map,
        }


    def generate(self, env):
        """
        Generates all of the Pokémon type pages into the distribution directory.
        """
        for type_id in self.core_data["type_names"]:
            self.render_template(
                env,
                "type.html",
                "types/%s.html" % type_id,
                extra_data={
                    'type_id': type_id,
                }
            )


def create_type_mons_map(type_names, mon_base_stats, national_to_species):
    """
    Create a convenient type mapping with all the Pokémon that
    have each typing.
    """
    type_mons_map = {}
    for national_num in national_to_species:
        species = national_to_species[national_num]
        type1 = mon_base_stats[species]["type1"]
        type2 = mon_base_stats[species]["type2"]
        if type1 not in type_mons_map:
            type_mons_map[type1] = []
        if type2 not in type_mons_map:
            type_mons_map[type2] = []

        type_mons_map[type1].append(national_num)
        if type1 != type2:
            type_mons_map[type2].append(national_num)

    for type_id in type_mons_map:
        type_mons_map[type_id] = sorted(type_mons_map[type_id], key=int)

    return type_mons_map


def create_type_moves_map(type_names, moves, move_names):
    """
    Create a convenient type mapping with all the moves that
    have each typing.
    """
    type_moves_map = {}
    for move in moves:
        move_type = moves[move]["type"]
        if move_type not in type_moves_map:
            type_moves_map[move_type] = []

        type_moves_map[move_type].append(move)

    for move in type_moves_map:
        type_moves_map[move] = sorted(type_moves_map[move], key=lambda m: move_names[m])

    return type_moves_map
