#--------------------------------------------------------------------
# linoone: mon_summaries.py
#
# Page generator for the Pokémon summary pages.
#--------------------------------------------------------------------
from generators.base_generator import BaseGenerator


class MonSummariesGenerator(BaseGenerator):
    def prepare_template_data(self):
        """
        Prepares any additional data the page generator needs to
        render itself. Returns a dict of variables and/or functions
        that will be exposed to the template.
        """
        evolution_map = create_evolution_map(self.core_data["mon_evolutions"])
        encounters_map = create_encounters_map(self.core_data["wild_mons"], self.core_data["id_to_species"])
        return {
            "evolution_map": evolution_map,
            "encounters_map": encounters_map,
        }


    def generate(self, env):
        """
        Generates all of the Pokémon summary pages into the distribution directory.
        """
        for national_num in self.core_data["national_to_species"]:
            self.render_template(
                env,
                "mon_summary.html",
                "pokedex/%s.html" % national_num,
                extra_data={
                    'national_num': national_num,
                    'species': self.core_data["national_to_species"][national_num],
                }
            )


def create_evolution_map(mon_evolutions):
    """
    Create a convenient evolution mapping for each species' from and
    to evolutions.
    """
    evos_map = {}
    for species in mon_evolutions:
        if species not in evos_map:
            evos_map[species] = {"from": [], "to": []}

        evos = mon_evolutions[species]
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
