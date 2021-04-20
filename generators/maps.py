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
        get_encounter_info = create_encounter_func(
            self.core_data["wild_mons"],
            self.core_data["species_to_id"]
        )
        map_encounters = create_encounters_mapping(self.core_data["wild_mons"], get_encounter_info, self.core_data["id_to_species"])
        return {
            "map_encounters": map_encounters,
        }


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


def create_encounters_mapping(wild_mons, get_encounter_info, id_to_species):
    """
    Creates a dict for all maps with summaries of the wild
    mon data.
    """
    result = {}
    main_group = next(group for group in wild_mons["wild_encounter_groups"] if group["label"] == "gWildMonHeaders")
    for map_encounters in main_group["encounters"]:
        map_id = map_encounters["map"]
        map_summary = {}
        for field in main_group["fields"]:
            summary = {}
            if field["type"] not in map_encounters:
                continue

            unique_species = list(set([mon["species"] for mon in map_encounters[field["type"]]["mons"]]))
            if "groups" in field:
                for group in field["groups"]:
                    group_summary = {}
                    for species in unique_species:
                        encounter_info = get_encounter_info(map_id, id_to_species[species], field["type"], group)
                        if encounter_info:
                            group_summary[species] = encounter_info
                    summary[group] = group_summary
            else:
                for species in unique_species:
                    summary[species] = get_encounter_info(map_id, id_to_species[species], field["type"])

            map_summary[field["type"]] = summary

        result[map_id] = map_summary

    return result

def create_encounter_func(wild_mons, species_to_id):
    """
    Creates a function that returns some information about encountering a
    given species in a map for a type of encounter.
    The result of calling the function will be a dict containing:
        {"encounter_chance", "min_level", "max_level").
    Returns None if the species is not encounterable.
    """
    funcs = {}
    main_group = next(group for group in wild_mons["wild_encounter_groups"] if group["label"] == "gWildMonHeaders")
    for field in main_group["fields"]:
        if "groups" in field:
            # This behaves like the fishing rods, where each
            # rod type corresponds to a contiguous region of
            # the mons array.
            totals = {}
            for group in field["groups"]:
                total = 0
                for i in field["groups"][group]:
                    total += field["encounter_rates"][i]

                totals[group] = total

            funcs[field["type"]] = create_partitioned_encounter_summary_func(field, totals, main_group, species_to_id)
        else:
            total = sum(field["encounter_rates"])
            funcs[field["type"]] = create_encounter_summary_func(field, total, main_group, species_to_id)

    def encounter_chance_func(map_id, species, encounter_type, group=None):
        if encounter_type not in funcs:
            return None
        return funcs[encounter_type](map_id, species, group)

    return encounter_chance_func


def create_encounter_summary_func(field, total, main_group, species_to_id):
    def f(map_id, species, group):
        encounters = next(m for m in main_group["encounters"] if m["map"] == map_id)
        if encounters is None or field["type"] not in encounters:
            return None

        count = 0
        min_level = 99999
        max_level = -99999
        for i, mon in enumerate(encounters[field["type"]]["mons"]):
            if mon["species"] == species_to_id[species]:
                count += field["encounter_rates"][i]
                if mon["min_level"] < min_level:
                    min_level = mon["min_level"]
                if mon["max_level"] > max_level:
                    max_level = mon["max_level"]

        if count == 0:
            return None

        return {
            "encounter_chance": round(100 * count / total, 2),
            "min_level": min_level,
            "max_level": max_level,
        }

    return f


def create_partitioned_encounter_summary_func(field, totals, main_group, species_to_id):
    def f(map_id, species, group):
        if group not in totals or group not in field["groups"]:
            return None

        encounters = next(m for m in main_group["encounters"] if m["map"] == map_id)
        if encounters is None or field["type"] not in encounters:
            return None

        count = 0
        min_level = 99999
        max_level = -99999
        for i in field["groups"][group]:
            mon = encounters[field["type"]]["mons"][i]
            if mon["species"] == species_to_id[species]:
                count += field["encounter_rates"][i]
                if mon["min_level"] < min_level:
                    min_level = mon["min_level"]
                if mon["max_level"] > max_level:
                    max_level = mon["max_level"]

        if count == 0:
            return None

        return {
            "encounter_chance": round(100 * count / totals[group], 2),
            "min_level": min_level,
            "max_level": max_level,
        }

    return f
