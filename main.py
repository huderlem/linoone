import argparse
import os
import pickle

import parse.mons as mons
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from bs4 import BeautifulSoup as bs

def get_sorted_national_dex_numbers(national_to_species):
    """
    Gets the sorted numerical list of national dex numbers from the
    given dict mapping.
    """
    keys = list(national_to_species.keys())
    keys.sort(key = int)
    return keys


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
    "mon_icon_pics": {
        "func": mons.parse_mon_icon_pics,
        "cache_file": "mon_icon_pics.pickle"
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
    mon_icon_pics = load_data("mon_icon_pics", config)
    ability_names = load_data("ability_names", config)
    ability_descriptions = load_data("ability_descriptions", config)
    type_names = load_data("type_names", config)
    move_names = load_data("move_names", config)
    national_dex_numbers = get_sorted_national_dex_numbers(national_to_species)

    os.makedirs("dist", exist_ok=True)
    os.makedirs("dist/pokedex", exist_ok=True)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html"])
    )
    template = env.get_template("pokedex.html")
    output = template.render(
        **config,
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
            species=national_to_species[national_num],
            national_num=national_num,
            mon_species_names=mon_species_names,
            mon_base_stats=mon_base_stats,
            type_names=type_names,
            mon_dex_entries=mon_dex_entries,
            ability_names=ability_names,
            mon_learnsets=mon_learnsets,
            move_names=move_names
        )
        soup = bs(output, "html.parser")
        prettyHTML = soup.prettify(formatter="html5")
        filepath = "dist/pokedex/%s.html" % national_num
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prettyHTML)
