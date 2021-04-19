#--------------------------------------------------------------------
# linoone: maps.py
#
# Page generator for the individual map pages.
#--------------------------------------------------------------------
import os

from generators.base_generator import BaseGenerator

from PIL import Image, ImageDraw


class MapsGenerator(BaseGenerator):
    def prepare_template_data(self):
        """
        Prepares any additional data the page generator needs to
        render itself. Returns a dict of variables and/or functions
        that will be exposed to the template.
        """
        return {}


    def generate(self, env):
        """
        Generates all of the map pages into the distribution directory.
        """
        for map_id in self.core_data["maps"]:
            self.render_template(
                env,
                "map.html",
                "maps/%s.html" % map_id,
                extra_data={
                    'map_id': map_id,
                }
            )
