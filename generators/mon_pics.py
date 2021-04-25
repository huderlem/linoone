#--------------------------------------------------------------------
# linoone: mon_pics.py
#
# Pokémon images generator.
#--------------------------------------------------------------------
import os
import re

from generators.base_generator import BaseGenerator
from util.file_formats import parse_jasc_file

from PIL import Image


class MonPicsGenerator(BaseGenerator):
    def generate(self, env):
        """
        Generates the various Pokémon image assets into the distribution directory.
        """
        poke_images_dir = os.path.join(self.config["dist_dir"], "images/pokemon")
        os.makedirs(poke_images_dir, exist_ok=True)
        self.generate_mon_pics(self.core_data["mon_front_pics"], self.core_data["species_to_national"], "front", (0, 0, 64, 64))
        self.generate_mon_pics(self.core_data["mon_back_pics"], self.core_data["species_to_national"], "back", (0, 0, 64, 64))
        self.generate_shiny_mon_pics(self.core_data["mon_front_pics"], self.core_data["species_to_national"], "front", (0, 0, 64, 64), self.core_data["mon_shiny_palettes"])
        self.generate_shiny_mon_pics(self.core_data["mon_back_pics"], self.core_data["species_to_national"], "back", (0, 0, 64, 64), self.core_data["mon_shiny_palettes"])
        self.generate_mon_pics(self.core_data["mon_icon_pics"], self.core_data["species_to_national"], "icon", (0, 0, 32, 32))

        type_images_dir = os.path.join(self.config["dist_dir"], "images/types")
        os.makedirs(type_images_dir, exist_ok=True)
        self.generate_type_pics(self.core_data["type_names"], self.project_settings["types"])


    def generate_mon_pics(self, species_to_pics, species_to_national, name, crop, force=False):
        """
        Processes and generates the various mon images into the distribution directory.
        """
        for species in species_to_pics:
            if species not in species_to_national:
                continue

            filepath = species_to_pics[species]
            png_filepath = re.sub(r"\.4bpp.*", ".png", filepath)
            dest_filepath = os.path.join(self.config["dist_dir"], "images/pokemon/%s_%s.png" % (species_to_national[species], name))
            if force or not os.path.exists(dest_filepath):
                if not os.path.exists(png_filepath):
                    print("Skipping %s pic for species %s because %s doesn't exist." % (name, species, png_filepath))
                else:
                    img = Image.open(png_filepath)
                    cropped_img = img.crop(crop)
                    cropped_img.save(dest_filepath)


    def generate_shiny_mon_pics(self, species_to_pics, species_to_national, name, crop, mon_shiny_palettes, force=False):
        """
        Processes and generates the various shiny mon images into the distribution directory.
        """
        for species in species_to_pics:
            if species not in species_to_national:
                continue

            filepath = species_to_pics[species]
            png_filepath = re.sub(r"\.4bpp.*", ".png", filepath)
            dest_filepath = os.path.join(self.config["dist_dir"], "images/pokemon/%s_%s_shiny.png" % (species_to_national[species], name))
            if force or not os.path.exists(dest_filepath):
                try:
                    img = Image.open(png_filepath)
                    cropped_img = img.crop(crop)
                    if img.mode == "P" and species in mon_shiny_palettes and os.path.exists(mon_shiny_palettes[species]) and (force or not os.path.exists(dest_filepath)):
                        palette_filepath = re.sub(r"\.gbapal.*", ".pal", mon_shiny_palettes[species])
                        shiny_palette = parse_jasc_file(palette_filepath)
                        if shiny_palette is not None:
                            cropped_img.putpalette(shiny_palette)
                            cropped_img.save(dest_filepath)
                except FileNotFoundError:
                    print("Skipping shiny %s pic for species %s because %s doesn't exist." % (name, species, png_filepath))


    def generate_type_pics(self, type_names, type_settings):
        """
        Generates the Pokémon type icon images.
        """
        for t in type_names:
            source_filepath = os.path.join(self.config["project_dir"], type_settings.types[t]["icon_filepath"])
            dest_filepath = os.path.join(self.config["dist_dir"], "images/types/%s.png" % t)
            img = Image.open(source_filepath)
            img.save(dest_filepath)
