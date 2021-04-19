#--------------------------------------------------------------------
# linoone: map_sections.py
#
# Page generator for the region map section pages.
#--------------------------------------------------------------------
import os

from generators.base_generator import BaseGenerator

from PIL import Image, ImageDraw


class MapSectionsGenerator(BaseGenerator):
    def prepare_template_data(self):
        """
        Prepares any additional data the page generator needs to
        render itself. Returns a dict of variables and/or functions
        that will be exposed to the template.
        """
        map_sections = create_map_sections_map(
            self.core_data["maps"],
            self.core_data["region_map_sections"]
        )
        return {
            "map_sections": map_sections,
        }


    def generate(self, env):
        """
        Generates all of the map section pages into the distribution directory.
        """
        self.generate_region_map_section_pics(self.core_data["region_map_sections"])
        for map_section in self.core_data["region_map_sections"]:
            self.render_template(
                env,
                "map_section.html",
                "map_sections/%s.html" % map_section,
                extra_data={
                    'map_section': map_section,
                }
            )

        self.render_template(env, "map_sections.html", "map_sections.html")


    def generate_region_map_section_pics(self, region_map_sections, force=False):
        """
        Generates a region map image with the map section highlighted for each map section.
        """
        dest_images_dir = os.path.join(self.config["dist_dir"], "images/region_map_sections")
        os.makedirs(dest_images_dir, exist_ok=True)
        tiles_filepath = os.path.join(self.config["project_dir"], "graphics/pokenav/region_map.png")
        tilemap_filepath = os.path.join(self.config["project_dir"], "graphics/pokenav/region_map_map.bin")
        tiles_img = Image.open(tiles_filepath)
        tiles_img_width = tiles_img.size[0] // 8
        with open(tilemap_filepath, "rb") as f:
            tilemap = bytes(f.read())

        base_map_image = Image.new("P", (240, 160))
        base_map_image.putpalette(tiles_img.getpalette())
        for y in range(20):
            for x in range(30):
                tile_id = tilemap[y * 64 + x]
                row = tile_id // tiles_img_width
                column = tile_id % tiles_img_width
                src_x = column * 8
                src_y = row * 8
                dest_x = x * 8
                dest_y = y * 8
                tile_img = tiles_img.crop((src_x, src_y, src_x + 8, src_y + 8))
                base_map_image.paste(tile_img, (dest_x, dest_y))
        base_map_image = base_map_image.convert("RGB")

        for mapsec_id in region_map_sections:
            map_section = region_map_sections[mapsec_id]
            dest_filepath = os.path.join(self.config["dist_dir"], "images/region_map_sections/%s.png" % (mapsec_id))
            if force or not os.path.exists(dest_filepath):
                img = base_map_image.copy()
                draw = ImageDraw.Draw(img)
                pixel_x = (map_section["x"] + 1) * 8
                pixel_y = (map_section["y"] + 2) * 8
                width = map_section["width"] * 8
                height = map_section["height"] * 8
                left = pixel_x - 4
                top = pixel_y - 4
                right = pixel_x + width + 3
                bottom = pixel_y + height + 3
                draw.rectangle([left, top, right, bottom], outline="#FF00FF", width=4)
                img.save(dest_filepath)


def create_map_sections_map(maps, region_map_sections):
    """
    Create a convenient region map section mapping with all the maps that
    are located in each section.
    """
    result = {}
    for cur_map in maps:
        mapsec = maps[cur_map]["region_map_section"]
        if mapsec not in result:
            result[mapsec] = []

        result[mapsec].append(cur_map)

    for mapsec in result:
        result[mapsec] = sorted(result[mapsec], key=lambda m: maps[m]["id"])

    return result
