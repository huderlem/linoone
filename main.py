import argparse
import os
import pickle
import re
import urllib.parse

import parse.mons as mons
from generators.pokedex import PokedexGenerator
from generators.mon_summaries import MonSummariesGenerator
from generators.mon_pics import MonPicsGenerator
from generators.type_mons import TypeMonsGenerator

from jinja2 import Environment, FileSystemLoader, select_autoescape


project_data = {
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
            f = open(project_data[name]["cache_file"], "rb")
            d = pickle.load(f)
            f.close()
            return d
        except:
            pass

    f = open(project_data[name]["cache_file"], "wb")
    d = project_data[name]["func"](config)
    pickle.dump(d, f)
    return d


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


def load_core_data(config):
    """
    Loads the core data from the decomp source files, which are made
    available to the page generator templates.
    """
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
    return {
        "mon_base_stats": mon_base_stats,
        "mon_dex_entries": mon_dex_entries,
        "mon_learnsets": mon_learnsets,
        "mon_species_names": mon_species_names,
        "mon_evolutions": mon_evolutions,
        "species_to_national": species_to_national,
        "national_to_species": national_to_species,
        "mon_front_pics": mon_front_pics,
        "mon_back_pics": mon_back_pics,
        "mon_icon_pics": mon_icon_pics,
        "mon_shiny_palettes": mon_shiny_palettes,
        "ability_names": ability_names,
        "ability_descriptions": ability_descriptions,
        "type_names": type_names,
        "move_names": move_names,
    }


def load_core_funcs(config):
    """
    Loads the core functions that are made available to the page generator templates.
    """
    root = config["base_url"]
    if root is None:
        root = config["dist_dir"]

    make_url = make_url_factory(root)
    return {
        "make_url": make_url,
    }


if __name__ == "__main__":
    argparser = argparse.ArgumentParser("Linoone - Decomp Website Builder")
    argparser.add_argument("project_dir", help="directory of the decomp project")
    args = argparser.parse_args()

    # Load program config.
    config = {}
    config["project_dir"] = args.project_dir
    config["website_title"] = "pokeemerald"
    config["dist_dir"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dist")
    config["base_url"] = None

    # Load core data and functions to be used by generators and their templates.
    core_data = load_core_data(config)
    core_funcs = load_core_funcs(config)

    # Create Jinja templating environment
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html"])
    )

    # Execute all of the artifact generators to build the static website.
    artifact_generators = [
        PokedexGenerator,
        MonSummariesGenerator,
        MonPicsGenerator,
        TypeMonsGenerator,
    ]
    for generator in artifact_generators:
        g = generator(config, core_data, core_funcs)
        g.run(env)
