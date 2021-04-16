#--------------------------------------------------------------------
# linoone: abilities.py
#
# Page generator for the Pokémon abilities page. Lists all the
# abilities.
#--------------------------------------------------------------------
from generators.base_generator import BaseGenerator


class AbilitiesGenerator(BaseGenerator):
    def prepare_template_data(self):
        """
        Prepares any additional data the page generator needs to
        render itself. Returns a dict of variables and/or functions
        that will be exposed to the template.
        """
        ability_mons = create_ability_map(
            self.core_data["mon_base_stats"],
            self.core_data["national_to_species"]
        )
        sorted_abilities = get_sorted_abilities(self.core_data["ability_names"])
        return {
            "ability_mons": ability_mons,
            "sorted_abilities": sorted_abilities,
        }


    def generate(self, env):
        """
        Generates all of the ability pages into the distribution directory.
        """
        for ability in self.core_data["ability_names"]:
            self.render_template(
                env,
                "ability.html",
                "abilities/%s.html" % ability,
                extra_data={
                    'ability': ability,
                }
            )

        self.render_template(env, "abilities.html", "abilities.html")


def create_ability_map(mon_base_stats, national_to_species):
    """
    Create a convenient ability mapping with all the Pokémon that
    have each ability.
    """
    result = {}
    for national_num in national_to_species:
        species = national_to_species[national_num]
        ability1 = mon_base_stats[species]["abilities"][0]
        ability2 = mon_base_stats[species]["abilities"][1]
        if ability1 not in result:
            result[ability1] = []
        if ability2 not in result:
            result[ability2] = []

        result[ability1].append(national_num)
        if ability1 != ability2:
            result[ability2].append(national_num)

    for ability in result:
        result[ability] = sorted(result[ability], key=int)

    return result


def get_sorted_abilities(ability_names):
    """
    Gets the sorted list of abilities by their names.
    """
    keys = list(ability_names.keys())
    keys.sort(key = lambda ability: ability_names[ability].lower())
    return keys
