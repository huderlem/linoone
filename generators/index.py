#--------------------------------------------------------------------
# linoone: index.py
#
# Page generator for the homepage.
#--------------------------------------------------------------------
from generators.base_generator import BaseGenerator


class IndexGenerator(BaseGenerator):
    def generate(self, env):
        """
        Generates all of the Pokémon type pages into the distribution directory.
        """
        self.render_template(env, "index.html", "index.html")
