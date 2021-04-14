#--------------------------------------------------------------------
# linoone: pokedex.py
#
# Page generator for the Pokédex listing.
#--------------------------------------------------------------------
from generators.base_generator import BaseGenerator


class PokedexGenerator(BaseGenerator):
    def prepare_template_data(self):
        """
        Prepares any additional data the page generator needs to
        render itself. Returns a dict of variables and/or functions
        that will be exposed to the template.
        """
        national_dex_numbers = get_sorted_national_dex_numbers(self.core_data['national_to_species'])
        return {
            'national_dex_numbers': national_dex_numbers,
        }


    def generate(self, env):
        """
        Generates the pokedex page into the distribution directory.
        """
        self.render_template(env, "pokedex.html", "pokedex.html")


def get_sorted_national_dex_numbers(national_to_species):
    """
    Gets the sorted numerical list of national dex numbers from the
    given dict mapping.
    """
    keys = list(national_to_species.keys())
    keys.sort(key = int)
    return keys
