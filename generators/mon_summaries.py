#--------------------------------------------------------------------
# linoone: mon_summaries.py
#
# Page generator for the Pokémon summary pages.
#--------------------------------------------------------------------
import base64
import os
import re

from graphviz import Digraph

from generators.base_generator import BaseGenerator


class MonSummariesGenerator(BaseGenerator):
    def prepare_template_data(self):
        """
        Prepares any additional data the page generator needs to
        render itself. Returns a dict of variables and/or functions
        that will be exposed to the template.
        """
        evolution_map = self.create_evolution_sets()
        evolution_svgs = self.create_evolution_svgs(evolution_map)
        encounters_map = create_encounters_map(self.core_data["wild_mons"], self.core_data["id_to_species"])
        return {
            "evolution_map": evolution_map,
            "encounters_map": encounters_map,
            "evolution_svgs": evolution_svgs,
        }


    def generate(self, env):
        """
        Generates all of the Pokémon summary pages into the distribution directory.
        """
        for national_num in self.core_data["national_to_species"]:
            if national_num in self.core_data["mon_dex_entries"]:
                self.render_template(
                    env,
                    "mon_summary.html",
                    "pokedex/%s.html" % national_num,
                    extra_data={
                        "national_num": national_num,
                        "species": self.core_data["national_to_species"][national_num],
                    }
                )


    def create_evolution_sets(self):
        """
        Create a convenient evolution mapping for each species' full
        evolution set.
        """
        evos_map = {}
        for species in self.core_data["mon_evolutions"]:
            if species not in evos_map:
                evos_map[species] = {"from": [], "to": []}

            evos = self.core_data["mon_evolutions"][species]
            for evo in evos:
                dest_species = evo["dest_species"]
                if dest_species not in evos_map:
                    evos_map[dest_species] = {"from": [], "to": []}
                evos_map[dest_species]["from"].append({
                    "method": evo["method"],
                    "param": evo["param"],
                    "species": species,
                })
                evos_map[species]["to"].append({
                    "method": evo["method"],
                    "param": evo["param"],
                    "species": evo["dest_species"],
                })

        return evos_map


    def create_evolution_svgs(self, evolution_map):
        """
        Uses graphviz to generate an SVG to display the full
        evolution chain for each species.
        """
        # Navigate to the pokemon images distribution directory so that
        # graphviz can load the images properly. We return back to the
        # current directory once the graphviz work is completed.
        cur_dir = os.getcwd()
        os.chdir(os.path.join(self.config["dist_dir"], "images/pokemon"))

        svgs = {}
        species_names = self.core_data["mon_species_names"]
        species_to_national = self.core_data["species_to_national"]
        for species in self.core_data["mon_base_stats"]:
            if species in evolution_map and (len(evolution_map[species]["to"]) > 0 or len(evolution_map[species]["from"]) > 0):
                dot = Digraph("%s Evolution Chain" % species_names[species], format="svg", node_attr={"shape": "box"}, graph_attr={"rankdir": "LR"})
                self.add_species_node(dot, species, highlight=True)
                self.build_evolution_graph(dot, species, evolution_map, set(), set())
                svg_content = dot.pipe().decode("utf-8")
                # Swap in the base64-encoded image data instead of the SVG's
                # image path. Using paths is super problematic because of the way
                # graphviz initially loads images and renders them inside the SVG.
                # It makes generating functional SVGs for both local and live-web
                # scenarios nearly impossible.
                img_paths = re.findall(r'"\w+\.png"', svg_content)
                for img_path in img_paths:
                    with open(img_path.strip('"'), "rb") as img_f:
                        encoded_img = base64.b64encode(img_f.read()).decode("ascii")
                        img_content = '"data:image/png;base64,%s"' % encoded_img
                        svg_content = svg_content.replace(img_path, img_content)

                svgs[species] = svg_content

        os.chdir(cur_dir)
        return svgs


    def build_evolution_graph(self, dot, initial_species, evolution_map, visited, edges):
        """
        Recursively builds the evolution graph starting at the
        given species.
        """
        if initial_species in visited or initial_species not in evolution_map:
            return

        visited.add(initial_species)
        for evo in evolution_map[initial_species]["from"]:
            species = evo["species"]
            edge_name = "%s:%s" % (species, initial_species)
            if edge_name not in edges:
                self.add_species_node(dot, species)
                self.add_species_edge(dot, species, initial_species, evo)
                edges.add(edge_name)
            self.build_evolution_graph(dot, species, evolution_map, visited, edges)

        for evo in evolution_map[initial_species]["to"]:
            species = evo["species"]
            edge_name = "%s:%s" % (initial_species, species)
            if edge_name not in edges:
                self.add_species_node(dot, species)
                self.add_species_edge(dot, initial_species, species, evo)
                edges.add(edge_name)
            self.build_evolution_graph(dot, species, evolution_map, visited, edges)


    def add_species_node(self, dot, species, highlight=False):
        national_num = self.core_data["species_to_national"][species]
        img_path = "%s_front.png" % national_num
        label = """<<table border="0">
            <tr><td>%s</td></tr>
            <tr><td><img scale="true" src="%s" /></td></tr>
        </table>>""" % (
            self.core_data["mon_species_names"][species],
            img_path
        )
        href = self.core_funcs["make_url"]("pokedex/%s.html" % self.core_data["species_to_national"][species])
        extra_args = {}
        if highlight:
            extra_args["style"] = "bold"
            extra_args["color"] = "red"

        dot.node(
            species,
            href=href,
            label=label,
            **extra_args
        )


    def add_species_edge(self, dot, from_species, to_species, evo):
        evo_description = self.project_settings["evolution_methods"].get_label(evo["method"], evo["param"], self.core_data["items"])
        dot.edge(from_species, to_species, label=" %s" % evo_description)


def create_encounters_map(wild_mons, id_to_species):
    """
    Creates a mapping of each species to the maps that it
    can be found in.
    """
    result = {}
    main_group = next(group for group in wild_mons["wild_encounter_groups"] if group["label"] == "gWildMonHeaders")
    for map_encounters in main_group["encounters"]:
        for field in main_group["fields"]:
            if field["type"] not in map_encounters:
                continue

            for mon in map_encounters[field["type"]]["mons"]:
                species = id_to_species[mon["species"]]
                if species not in result:
                    result[species] = set()

                result[species].add(map_encounters["map"])

    for species in result:
        result[species] = list(result[species])

    return result
