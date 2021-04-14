import argparse
import os
import pickle
import re
import urllib.parse

import parse.mons as mons
from parse.util import parse_jasc_file

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from bs4 import BeautifulSoup as bs
from PIL import Image

def get_sorted_national_dex_numbers(national_to_species):
    """
    Gets the sorted numerical list of national dex numbers from the
    given dict mapping.
    """
    keys = list(national_to_species.keys())
    keys.sort(key = int)
    return keys


def create_evolution_map(mon_evolutions):
    """
    Create a convenient evolution mapping for each species' from and
    to evolutions.
    """
    evos_map = {}
    for species in mon_evolutions:
        if species not in evos_map:
            evos_map[species] = {'from': [], 'to': []}

        evos = mon_evolutions[species]
        for evo in evos:
            dest_species = evo['dest_species']
            if dest_species not in evos_map:
                evos_map[dest_species] = {'from': [], 'to': []}
            evos_map[dest_species]['from'].append({
                'method': evo['method'],
                'param': evo['param'],
                'species': species,
            })
            evos_map[species]['to'].append({
                'method': evo['method'],
                'param': evo['param'],
                'species': evo['dest_species'],
            })

    return evos_map


data = {
    "mon_base_stats": {
        "func": mons.parse_base_stats,
        "cache_file": "mon_base_stats.pickle"
    },
    "mon_dex_entries": {
        "func": mons.parse_dex_entries,
        "cache_file": "mon_dex_entries.pickle"
    },
    "mon_learnsets": {
        "func": mons.parse_levelup_learnsets,
        "cache_file": "mon_learnsets.pickle"
    },
    "mon_species_names": {
        "func": mons.parse_species_names,
        "cache_file": "mon_species_names.pickle"
    },
    "mon_evolutions": {
        "func": mons.parse_evolutions,
        "cache_file": "mon_evolutions.pickle"
    },
    "species_maps": {
        "func": mons.parse_species_mapping,
        "cache_file": "species_maps.pickle"
    },
    "mon_front_pics": {
        "func": mons.parse_mon_front_pics,
        "cache_file": "mon_front_pics.pickle"
    },
    "mon_back_pics": {
        "func": mons.parse_mon_back_pics,
        "cache_file": "mon_back_pics.pickle"
    },
    "mon_icon_pics": {
        "func": mons.parse_mon_icon_pics,
        "cache_file": "mon_icon_pics.pickle"
    },
    "mon_shiny_palettes": {
        "func": mons.parse_mon_shiny_palettes,
        "cache_file": "mon_shiny_palettes.pickle"
    },
    "ability_names": {
        "func": mons.parse_ability_names,
        "cache_file": "ability_names.pickle"
    },
    "ability_descriptions": {
        "func": mons.parse_ability_descriptions,
        "cache_file": "ability_descriptions.pickle"
    },
    "type_names": {
        "func": mons.parse_type_names,
        "cache_file": "type_names.pickle"
    },
    "move_names": {
        "func": mons.parse_move_names,
        "cache_file": "move_names.pickle"
    },
}


def load_data(name, config, force=False):
    """
    Loads data from the project. Cached the data to a pickle file to avoid
    future loads, since they are slow.
    """
    if not force:
        try:
            f = open(data[name]["cache_file"], "rb")
            d = pickle.load(f)
            f.close()
            return d
        except:
            pass

    f = open(data[name]["cache_file"], "wb")
    d = data[name]["func"](config)
    pickle.dump(d, f)
    return d


def generate_mon_pics(species_to_pics, species_to_national, name, crop, force=False):
    """
    Processes and generates the various mon images into the distribution directory.
    """
    os.makedirs("dist/images/pokemon", exist_ok=True)
    for species in species_to_pics:
        if species not in species_to_national:
            continue

        filepath = species_to_pics[species]
        png_filepath = re.sub(r'\.4bpp.*', '.png', filepath)
        dest_filepath = "dist/images/pokemon/%s_%s.png" % (species_to_national[species], name)
        if force or not os.path.exists(dest_filepath):
            try:
                img = Image.open(png_filepath)
                cropped_img = img.crop(crop)
                cropped_img.save(dest_filepath)
            except FileNotFoundError:
                print("Skipping %s pic for species %s because %s doesn't exist." % (name, species, png_filepath))


def generate_shiny_mon_pics(species_to_pics, species_to_national, name, crop, mon_shiny_palettes, force=False):
    """
    Processes and generates the various shiny mon images into the distribution directory.
    """
    os.makedirs("dist/images/pokemon", exist_ok=True)
    for species in species_to_pics:
        if species not in species_to_national:
            continue

        filepath = species_to_pics[species]
        png_filepath = re.sub(r'\.4bpp.*', '.png', filepath)
        dest_filepath = "dist/images/pokemon/%s_%s_shiny.png" % (species_to_national[species], name)
        if force or not os.path.exists(dest_filepath):
            try:
                img = Image.open(png_filepath)
                cropped_img = img.crop(crop)
                if img.mode == "P" and species in mon_shiny_palettes and os.path.exists(mon_shiny_palettes[species]) and (force or not os.path.exists(dest_filepath)):
                    palette_filepath = re.sub(r'\.gbapal.*', '.pal', mon_shiny_palettes[species])
                    shiny_palette = parse_jasc_file(palette_filepath)
                    if shiny_palette is not None:
                        cropped_img.putpalette(shiny_palette)
                        cropped_img.save(dest_filepath)
            except FileNotFoundError:
                print("Skipping shiny %s pic for species %s because %s doesn't exist." % (name, species, png_filepath))


def make_url_factory(root):
    """
    Factory function to create a make_url() function that resolves urls.
    The resulting function is intended to be used in the HTML templates
    to generate urls that will function properly for both local and live
    web scenarios.
    """
    live_web = False
    if root.startswith('http'):
        live_web = True
        if not root.endswith('/'):
            root += '/'

    def make_url(path):
        if live_web:
            return urllib.parse.urljoin(root, path)
        else:
            return os.path.normpath(os.path.join(root, path))

    return make_url


if __name__ == "__main__":
    argparser = argparse.ArgumentParser("Linoone - Decomp Website Builder")
    argparser.add_argument("project_dir", help="directory of the decomp project")
    args = argparser.parse_args()

    config = {}
    config["project_dir"] = args.project_dir
    config["website_title"] = "pokeemerald"
    mon_base_stats = load_data("mon_base_stats", config)
    mon_dex_entries = load_data("mon_dex_entries", config)
    mon_learnsets = load_data("mon_learnsets", config)
    mon_species_names = load_data("mon_species_names", config)
    mon_evolutions = load_data("mon_evolutions", config)
    species_to_national, national_to_species = load_data("species_maps", config)
    mon_front_pics = load_data("mon_front_pics", config)
    mon_back_pics = load_data("mon_back_pics", config)
    mon_icon_pics = load_data("mon_icon_pics", config)
    mon_shiny_palettes = load_data("mon_shiny_palettes", config)
    ability_names = load_data("ability_names", config)
    ability_descriptions = load_data("ability_descriptions", config)
    type_names = load_data("type_names", config)
    move_names = load_data("move_names", config)
    national_dex_numbers = get_sorted_national_dex_numbers(national_to_species)
    evolution_map = create_evolution_map(mon_evolutions)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.makedirs(os.path.join(dir_path, "dist"), exist_ok=True)
    os.makedirs(os.path.join(dir_path, "dist/pokedex"), exist_ok=True)
    os.makedirs(os.path.join(dir_path, "dist/images"), exist_ok=True)
    output_dir = os.path.join(dir_path, "dist")
    make_url = make_url_factory(output_dir)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html"])
    )
    template = env.get_template("pokedex.html")
    output = template.render(
        **config,
        make_url=make_url,
        national_dex_numbers=national_dex_numbers,
        national_to_species=national_to_species,
        mon_species_names=mon_species_names,
        mon_base_stats=mon_base_stats,
        type_names=type_names
    )
    soup = bs(output, "html.parser")
    prettyHTML = soup.prettify(formatter="html5")
    with open("dist/pokedex.html", "w", encoding="utf-8") as f:
        f.write(prettyHTML)

    for national_num in national_dex_numbers:
        template = env.get_template("mon_summary.html")
        output = template.render(
            **config,
            make_url=make_url,
            species=national_to_species[national_num],
            species_to_national=species_to_national,
            national_num=national_num,
            mon_species_names=mon_species_names,
            mon_base_stats=mon_base_stats,
            type_names=type_names,
            mon_dex_entries=mon_dex_entries,
            ability_names=ability_names,
            mon_learnsets=mon_learnsets,
            move_names=move_names,
            evolution_map=evolution_map
        )
        soup = bs(output, "html.parser")
        prettyHTML = soup.prettify(formatter="html5")
        filepath = "dist/pokedex/%s.html" % national_num
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prettyHTML)

    generate_mon_pics(mon_front_pics, species_to_national, "front", (0, 0, 64, 64))
    generate_mon_pics(mon_back_pics, species_to_national, "back", (0, 0, 64, 64))
    generate_shiny_mon_pics(mon_front_pics, species_to_national, "front", (0, 0, 64, 64), mon_shiny_palettes)
    generate_shiny_mon_pics(mon_back_pics, species_to_national, "back", (0, 0, 64, 64), mon_shiny_palettes)
    generate_mon_pics(mon_icon_pics, species_to_national, "icon", (0, 0, 32, 32))
