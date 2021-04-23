import argparse
import os
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape

from setup.core_data import load_core_data
from setup.core_funcs import load_core_funcs
from settings import load_project_settings
from generators import (
    AbilitiesGenerator,
    IndexGenerator,
    MapSectionsGenerator,
    MapsGenerator,
    MonPicsGenerator,
    MonSummariesGenerator,
    MovesGenerator,
    PokedexGenerator,
    TypesGenerator,
)


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
    project_settings = load_project_settings(config)

    # Create Jinja templating environment
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html"])
    )

    # Execute all of the artifact generators to build the static website.
    artifact_generators = [
        IndexGenerator,
        PokedexGenerator,
        MonSummariesGenerator,
        MonPicsGenerator,
        TypesGenerator,
        AbilitiesGenerator,
        MovesGenerator,
        MapSectionsGenerator,
        MapsGenerator,
    ]
    for generator in artifact_generators:
        g = generator(config, core_data, core_funcs, project_settings)
        g.run(env)
