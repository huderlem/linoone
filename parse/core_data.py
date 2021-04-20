#--------------------------------------------------------------------
# linoone: core_data.py
#
# Handles parsing and gathering core data from the project sources.
#--------------------------------------------------------------------
import glob
import json
import os
import re

from pycparser.c_ast import BinaryOp, Cast, Constant, FuncCall, ID, InitList, NamedInitializer
from parse.parse_code import parse_declaration_from_file, parse_ast_from_file, get_declaration_from_ast, parse_names


def parse_base_stats(config):
    """
    Parses and returns the project's mon base stats.
    """
    filepath = os.path.join(config["project_dir"], "src/pokemon.c")
    base_stats = parse_declaration_from_file(filepath, "gBaseStats", config["project_dir"])
    if base_stats == None:
        raise Exception("Failed to read mon base stats from %s" % filepath)

    result = {}
    for item in base_stats.init.exprs:
        species = item.name[0].value
        result[species] = {}
        for field in item.expr.exprs:
            typ = type(field)
            if typ != NamedInitializer:
                continue

            field_name = field.name[0].name
            expr = field.expr
            field_value = None
            expr_type = type(expr)
            if expr_type == Constant:
                field_value = expr.value
            elif expr_type == ID:
                field_value = expr.name
            elif expr_type == InitList:
                field_value = [item.value for item in expr.exprs]

            # TODO: how to handle FuncCall for genderRatio?
            result[species][field_name] = field_value

    return result


def parse_dex_entries(config):
    """
    Parses and returns the project's mon pokedex entries.
    It also includes the pokedex text blurb.
    """
    filepath = os.path.join(config["project_dir"], "src/pokedex.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    dex_entries = get_declaration_from_ast(ast, "gPokedexEntries")
    if dex_entries == None:
        raise Exception("Failed to read mon pokedex entries stats from %s" % filepath)

    result = {}
    for item in dex_entries.init.exprs:
        species = item.name[0].value
        result[species] = {}
        for field in item.expr.exprs:
            typ = type(field)
            if typ != NamedInitializer:
                continue

            field_name = field.name[0].name
            expr = field.expr
            field_value = None
            expr_type = type(expr)
            if expr_type == Constant:
                field_value = expr.value
            elif expr_type == ID:
                field_value = expr.name
            elif expr_type == FuncCall:
                if expr.name.name == "_":
                    field_value = expr.args.exprs[0].value.strip("\"")

            if field_name == "description":
                # Use the actual text for the pokedex description field, not the
                # reference symbol name.
                mon_text = get_declaration_from_ast(ast, field_value)
                field_value = mon_text.init.args.exprs[0].value.strip("\"")

            result[species][field_name] = field_value

    return result


def parse_levelup_learnsets(config):
    """
    Parses and returns the project's mon level-up move learnsets.
    """
    filepath = os.path.join(config["project_dir"], "src/pokemon.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    learnset_pointers = get_declaration_from_ast(ast, "gLevelUpLearnsets")
    if learnset_pointers == None:
        raise Exception("Failed to read mon learnsets from %s" % filepath)

    result = {}
    for item in learnset_pointers.init.exprs:
        species = item.name[0].value
        result[species] = []
        learnset = get_declaration_from_ast(ast, item.expr.name)
        for level_up_move in learnset.init.exprs:
            if type(level_up_move) == Constant:
                continue

            level = level_up_move.left.left.value
            move = level_up_move.right.value
            result[species].append({"level": level, "move": move})

        result[species] = sorted(result[species], key=lambda item: int(item["level"]))

    return result


def parse_tmhm_learnsets(config):
    """
    Parses and returns the project's mon TM/HM move learnsets.
    """
    filepath = os.path.join(config["project_dir"], "src/pokemon.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    tmhm_pointers = get_declaration_from_ast(ast, "gTMHMLearnsets")
    if tmhm_pointers == None:
        raise Exception("Failed to read mon tm/hm learnsets from %s" % filepath)

    result = {}
    for item in tmhm_pointers.init.exprs:
        species = item.name[0].value
        tmhm_learnset = get_tmhms_from_expr(item.expr.exprs[0].expr, [])
        result[species] = sorted(tmhm_learnset, key=int)

    return result


def get_tmhms_from_expr(expr, tmhm_learnset):
    """
    Recursively parses out the list of TMHMs from the expression.
    """
    if type(expr) != BinaryOp:
        return tmhm_learnset

    # This is the base case leaf node.
    if type(expr.left) == Cast:
        tmhm = expr.right.left.value
        tmhm_learnset.append(tmhm)
        return tmhm_learnset

    tmhm_learnset = get_tmhms_from_expr(expr.left, tmhm_learnset)
    tmhm = expr.right.right.left.value
    tmhm_learnset.append(tmhm)
    return tmhm_learnset


def parse_tmhm_mapping(config):
    """
    Parses and returns the project's item-to-move numbers mapping.
    Returns the reverse mapping, too.
    """
    filepath = os.path.join(config["project_dir"], "src/party_menu.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    tmhm_moves = get_declaration_from_ast(ast, "sTMHMMoves")
    if tmhm_moves == None:
        raise Exception("Failed to read mon tm/hm moves from %s" % filepath)

    item_to_move = {}
    move_to_item = {}
    for item in tmhm_moves.init.exprs:
        tmhm_item = item.name[0].left.value
        move = item.expr.value
        item_to_move[tmhm_item] = move
        move_to_item[move] = tmhm_item

    return item_to_move, move_to_item


def parse_egg_moves(config):
    """
    Parses and returns the project's egg moves.
    """
    filepath = os.path.join(config["project_dir"], "src/daycare.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    egg_moves = get_declaration_from_ast(ast, "gEggMoves")
    if egg_moves == None:
        raise Exception("Failed to read mon egg moves from %s" % filepath)

    result = {}
    cur_species = None
    for item in egg_moves.init.exprs:
        if type(item) == BinaryOp:
            cur_species = item.left.value
            result[cur_species] = []
        else:
            move = item.value
            if move != '0xFFFF':
                result[cur_species].append(move)

    for species in result:
        result[species] = sorted(result[species], key=int)

    return result


def parse_tutor_moves(config):
    """
    Parses and returns the project's move tutor moves.
    """
    filepath = os.path.join(config["project_dir"], "src/party_menu.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    tutor_move_defs = get_declaration_from_ast(ast, "gTutorMoves")
    if tutor_move_defs == None:
        raise Exception("Failed to read mon tutor move definitions from %s" % filepath)

    tutor_moves = get_declaration_from_ast(ast, "sTutorLearnsets")
    if tutor_moves == None:
        raise Exception("Failed to read mon tutor moves from %s" % filepath)

    tutor_move_map = {}
    for item in tutor_move_defs.init.exprs:
        tutor_move_id = item.name[0].value
        move = item.expr.value
        tutor_move_map[tutor_move_id] = move

    result = {}
    for item in tutor_moves.init.exprs:
        species = item.name[0].value
        tutor_moves = get_tutor_moves_from_expr(item.expr, tutor_move_map, [])
        result[species] = sorted(tutor_moves, key=int)

    return result


def get_tutor_moves_from_expr(expr, tutor_move_map, tutor_moves):
    """
    Recursively parses out the list of tutor moves from the expression.
    """
    if type(expr) != BinaryOp:
        return tutor_moves

    # This is the base case leaf node.
    if type(expr.left) == Constant:
        tutor_move_id = expr.right.value
        tutor_moves.append(tutor_move_map[tutor_move_id])
        return tutor_moves

    tutor_moves = get_tutor_moves_from_expr(expr.left, tutor_move_map, tutor_moves)
    tutor_move_id = expr.right.right.value
    tutor_moves.append(tutor_move_map[tutor_move_id])
    return tutor_moves


def parse_species_names(config):
    """
    Parses and returns the project's mon species names.
    """
    filepath = os.path.join(config["project_dir"], "src/data.c")
    return parse_names(filepath, "gSpeciesNames", config["project_dir"])


def parse_type_names(config):
    """
    Parses and returns the project's mon type names.
    """
    filepath = os.path.join(config["project_dir"], "src/battle_main.c")
    return parse_names(filepath, "gTypeNames", config["project_dir"])


def parse_ability_names(config):
    """
    Parses and returns the project's mon ability names.
    """
    filepath = os.path.join(config["project_dir"], "src/battle_main.c")
    return parse_names(filepath, "gAbilityNames", config["project_dir"])


def parse_move_names(config):
    """
    Parses and returns the project's move names.
    """
    filepath = os.path.join(config["project_dir"], "src/data.c")
    return parse_names(filepath, "gMoveNames", config["project_dir"])


def parse_items(config):
    """
    Parses and returns the project's items.
    """
    filepath = os.path.join(config["project_dir"], "src/item.c")
    items = parse_declaration_from_file(filepath, "gItems", config["project_dir"])
    if items == None:
        raise Exception("Failed to read mon base stats from %s" % filepath)

    result = {}
    for item in items.init.exprs:
        item_id = item.name[0].value
        result[item_id] = {}
        for field in item.expr.exprs:
            typ = type(field)
            if typ != NamedInitializer:
                continue

            field_name = field.name[0].name
            expr = field.expr
            field_value = None
            expr_type = type(expr)
            if expr_type == Constant:
                field_value = expr.value
            elif expr_type == ID:
                field_value = expr.name
            elif expr_type == FuncCall:
                if expr.name.name == "_":
                    field_value = expr.args.exprs[0].value.strip("\"")

            result[item_id][field_name] = field_value

    return result


def parse_ability_descriptions(config):
    """
    Parses and returns the project's ability descriptions.
    """
    filepath = os.path.join(config["project_dir"], "src/battle_main.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    ability_descriptions = get_declaration_from_ast(ast, "gAbilityDescriptionPointers")
    if ability_descriptions == None:
        raise Exception("Failed to read ability descriptions from %s" % filepath)

    result = {}
    for item in ability_descriptions.init.exprs:
        ability = item.name[0].value
        ability_description = get_declaration_from_ast(ast, item.expr.name)
        description = ability_description.init.args.exprs[0].value.strip("\"")
        result[ability] = description

    return result


def parse_move_descriptions(config):
    """
    Parses and returns the project's move descriptions.
    """
    filepath = os.path.join(config["project_dir"], "src/pokemon_summary_screen.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    move_descriptions = get_declaration_from_ast(ast, "gMoveDescriptionPointers")
    if move_descriptions == None:
        raise Exception("Failed to read move descriptions from %s" % filepath)

    result = {}
    for item in move_descriptions.init.exprs:
        move = item.name[0].left.value
        move_description = get_declaration_from_ast(ast, item.expr.name)
        description = move_description.init.args.exprs[0].value.strip("\"")
        result[move] = description

    return result


def parse_nature_names(config):
    """
    Parses and returns the project's nature names.
    """
    filepath = os.path.join(config["project_dir"], "src/pokemon_summary_screen.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    nature_names = get_declaration_from_ast(ast, "gNatureNamePointers")
    if nature_names == None:
        raise Exception("Failed to read nature names from %s" % filepath)

    result = {}
    for item in nature_names.init.exprs:
        nature = item.name[0].value
        nature_name = get_declaration_from_ast(ast, item.expr.name)
        name = nature_name.init.args.exprs[0].value.strip("\"")
        result[nature] = name

    return result


def parse_evolutions(config):
    """
    Parses and returns the project's mon evolution definitions.
    """
    filepath = os.path.join(config["project_dir"], "src/pokemon.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    evolutions = get_declaration_from_ast(ast, "gEvolutionTable")
    if evolutions == None:
        raise Exception("Failed to read mon evolutions from %s" % filepath)

    result = {}
    for item in evolutions.init.exprs:
        species = item.name[0].value
        result[species] = []
        for evolution in item.expr.exprs:
            method = evolution.exprs[0].value
            param = evolution.exprs[1].value
            dest_species = evolution.exprs[2].value
            result[species].append({"method": method, "param": param, "dest_species": dest_species})

    return result


def parse_species_mapping(config):
    """
    Parses and returns the project's species-to-national-dex numbers mapping.
    Returns the reverse mapping, too.
    """
    filepath = os.path.join(config["project_dir"], "src/pokemon.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    mappings = get_declaration_from_ast(ast, "gSpeciesToNationalPokedexNum")
    if mappings == None:
        raise Exception("Failed to read species-to-national-dex mapping from %s" % filepath)

    species_to_national = {}
    national_to_species = {}
    for item in mappings.init.exprs:
        if type(item.expr) == Constant:
            species = item.name[0].left.value
            national = item.expr.value
            species_to_national[species] = national
            national_to_species[national] = species

    return species_to_national, national_to_species


def parse_mon_gfx(config, pic_table_name, pic_table_file, pic_def_file):
    """
    Parses and returns the project's mon specified gfx data.
    """
    filepath = os.path.join(config["project_dir"], pic_table_file)
    ast = parse_ast_from_file(filepath, config["project_dir"])

    pics = get_declaration_from_ast(ast, pic_table_name)
    if pics == None:
        raise Exception("Failed to read mon pics from %s" % filepath)

    pics_filepath = os.path.join(config["project_dir"], pic_def_file)
    pics_ast = parse_ast_from_file(pics_filepath, config["project_dir"])

    result = {}
    for item in pics.init.exprs:
        if type(item.name[0]) == Constant:
            species = item.name[0].value
            pic_label = item.expr.exprs[0].name
            pic_decl = get_declaration_from_ast(pics_ast, pic_label)
            pic_filepath = pic_decl.init.args.exprs[0].value.strip("\"")
            pic_full_filepath = os.path.join(config["project_dir"], pic_filepath)
            result[species] = pic_full_filepath

    return result


def parse_mon_front_pics(config):
    """
    Parses and returns the project's mon specified pics.
    """
    return parse_mon_gfx(config, "gMonFrontPicTable", "src/data.c", "src/anim_mon_front_pics.c")


def parse_mon_back_pics(config):
    """
    Parses and returns the project's mon back pics.
    """
    return parse_mon_gfx(config, "gMonBackPicTable", "src/data.c", "src/graphics.c")


def parse_mon_shiny_palettes(config):
    """
    Parses and returns the project's mon shiny palettes.
    """
    return parse_mon_gfx(config, "gMonShinyPaletteTable", "src/data.c", "src/graphics.c")


def parse_mon_icon_pics(config):
    """
    Parses and returns the project's mon icon pics.
    """
    filepath = os.path.join(config["project_dir"], "src/pokemon_icon.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    icon_pics = get_declaration_from_ast(ast, "gMonIconTable")
    if icon_pics == None:
        raise Exception("Failed to read mon icons pics from %s" % filepath)

    gfx_filepath = os.path.join(config["project_dir"], "src/graphics.c")
    gfx_ast = parse_ast_from_file(gfx_filepath, config["project_dir"])

    result = {}
    for item in icon_pics.init.exprs:
        if type(item.name[0]) == Constant:
            species = item.name[0].value
            icon_label = item.expr.name
            icon_decl = get_declaration_from_ast(gfx_ast, icon_label)
            icon_filepath = icon_decl.init.args.exprs[0].value.strip("\"")
            icon_full_filepath = os.path.join(config["project_dir"], icon_filepath)
            result[species] = icon_full_filepath

    return result


def parse_moves(config):
    """
    Parses and returns the project's battle moves data.
    """
    filepath = os.path.join(config["project_dir"], "src/pokemon.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    battle_moves = get_declaration_from_ast(ast, "gBattleMoves")
    if battle_moves == None:
        raise Exception("Failed to read battle moves from %s" % filepath)

    result = {}
    for item in battle_moves.init.exprs:
        move = item.name[0].value
        result[move] = {}
        for field in item.expr.exprs:
            typ = type(field)
            if typ != NamedInitializer:
                continue

            field_name = field.name[0].name
            expr = field.expr
            field_value = None
            expr_type = type(expr)
            if expr_type == Constant:
                field_value = expr.value
            elif expr_type == ID:
                field_value = expr.name

            result[move][field_name] = field_value

    return result


def parse_maps(config):
    """
    Parses and returns the map definitions in the project. It locates the maps
    by globbing for map.json files in the maps directory.
    """
    maps = {}

    map_filepaths = []
    map_dir = os.path.join(config["project_dir"], "data/maps")
    for dirpath, dirs, files in os.walk(map_dir):
        for filename in files:
            if filename == "map.json":
                filepath = os.path.join(dirpath, filename)
                map_filepaths.append(filepath)

    for filepath in map_filepaths:
        with open(filepath) as f:
            map_data = json.load(f)
            maps[map_data["id"]] = map_data

    return maps


def parse_region_map_sections(config):
    """
    Parses and returns the project's region map entries.
    """
    filepath = os.path.join(config["project_dir"], "src/region_map.c")
    ast = parse_ast_from_file(filepath, config["project_dir"])

    region_map_entries = get_declaration_from_ast(ast, "gRegionMapEntries")
    if region_map_entries == None:
        raise Exception("Failed to read region map sections from %s" % filepath)

    mapsec_ids = parse_defines(config, "include/constants/region_map_sections.h", "MAPSEC_")
    result = {}
    for item in region_map_entries.init.exprs:
        mapsec = mapsec_ids[item.name[0].value]
        map_name_label = item.expr.exprs[4].name
        map_name_decl = get_declaration_from_ast(ast, map_name_label)
        map_name = map_name_decl.init.args.exprs[0].value.strip("\"")
        result[mapsec] = {
            'x': int(item.expr.exprs[0].value),
            'y': int(item.expr.exprs[1].value),
            'width': int(item.expr.exprs[2].value),
            'height': int(item.expr.exprs[3].value),
            'name': map_name,
        }

    return result


def parse_defines(config, filepath, prefix=None):
    """
    Parses the #define directives in a file. If a prefix
    is provided, then only the defines whose name starts
    with the prefix will be returned.
    """
    result = {}
    filepath = os.path.join(config["project_dir"], filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            match = re.match(r"#define\s+(\w+)\s+(.+)", line)
            if match:
                name = match.group(1)
                value = match.group(2)
                if prefix is None or name.startswith(prefix):
                    result[value] = name

    return result


def parse_species_defines(config):
    """
    Parses the Pokémon species defines to handle interop data originating
    from non-C files (like JSON).
    """
    species_to_id = parse_defines(config, "include/constants/species.h", "SPECIES_")
    id_to_species = {}
    for species in species_to_id:
        id_to_species[species_to_id[species]] = species

    return species_to_id, id_to_species


def parse_wild_mons(config):
    """
    Parses and returns the wild Pokémon definitions in the project.
    """
    wild_mons = {}

    filepath = os.path.join(config["project_dir"], "src/data/wild_encounters.json")
    with open(filepath) as f:
        wild_mons = json.load(f)

    return wild_mons
