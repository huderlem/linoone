#--------------------------------------------------------------------
# linoone: type_mons.py
#
# Page generator for the Pokémon type pages. Each page lists the
# Pokémon that have each typing.
#--------------------------------------------------------------------
from generators.base_generator import BaseGenerator


class TypeMonsGenerator(BaseGenerator):
    def prepare_template_data(self):
        """
        Prepares any additional data the page generator needs to
        render itself. Returns a dict of variables and/or functions
        that will be exposed to the template.
        """
        types_map = create_types_map(
            self.core_data["type_names"],
            self.core_data["mon_base_stats"],
            self.core_data["national_to_species"]
        )
        return {
            "types_map": types_map,
        }


    def generate(self, env):
        """
        Generates all of the Pokémon summary pages into the distribution directory.
        """
        for type_id in self.custom_data["types_map"]:
            self.render_template(
                env,
                "type_mons.html",
                "types/%s.html" % type_id,
                extra_data={
                    'type_id': type_id,
                }
            )


def create_types_map(type_names, mon_base_stats, national_to_species):
    """
    Create a convenient type mapping with all the Pokémon that
    have each typing.
    """
    types_map = {}
    for national_num in national_to_species:
        species = national_to_species[national_num]
        type1 = mon_base_stats[species]["type1"]
        type2 = mon_base_stats[species]["type2"]
        if type1 not in types_map:
            types_map[type1] = []
        if type2 not in types_map:
            types_map[type2] = []

        types_map[type1].append(national_num)
        if type1 != type2:
            types_map[type2].append(national_num)

    for type_id in types_map:
        types_map[type_id] = sorted(types_map[type_id], key=int)

    return types_map
