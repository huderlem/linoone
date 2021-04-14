#--------------------------------------------------------------------
# linoone: mons.py
#
# Handles parsing and gathering mon data.
#--------------------------------------------------------------------
import os
from pycparser.c_ast import Constant, FuncCall, ID, InitList, NamedInitializer
from parse.parse_code import parse_declaration_from_file, parse_ast_from_file, get_declaration_from_ast, parse_names


def parse_base_stats(config):
    """
    Parses and returns the project's mon base stats.
    """
    filepath = os.path.join(config['project_dir'], "src/pokemon.c")
    base_stats = parse_declaration_from_file(filepath, "gBaseStats", config['project_dir'])
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
    filepath = os.path.join(config['project_dir'], "src/pokedex.c")
    ast = parse_ast_from_file(filepath, config['project_dir'])

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
    filepath = os.path.join(config['project_dir'], "src/pokemon.c")
    ast = parse_ast_from_file(filepath, config['project_dir'])

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


def parse_species_names(config):
    """
    Parses and returns the project's mon species names.
    """
    filepath = os.path.join(config['project_dir'], "src/data.c")
    return parse_names(filepath, "gSpeciesNames", config['project_dir'])


def parse_type_names(config):
    """
    Parses and returns the project's mon type names.
    """
    filepath = os.path.join(config['project_dir'], "src/battle_main.c")
    return parse_names(filepath, "gTypeNames", config['project_dir'])


def parse_ability_names(config):
    """
    Parses and returns the project's mon ability names.
    """
    filepath = os.path.join(config['project_dir'], "src/battle_main.c")
    return parse_names(filepath, "gAbilityNames", config['project_dir'])


def parse_move_names(config):
    """
    Parses and returns the project's move names.
    """
    filepath = os.path.join(config['project_dir'], "src/data.c")
    return parse_names(filepath, "gMoveNames", config['project_dir'])


def parse_ability_descriptions(config):
    """
    Parses and returns the project's ability descriptions.
    """
    filepath = os.path.join(config['project_dir'], "src/battle_main.c")
    ast = parse_ast_from_file(filepath, config['project_dir'])

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


def parse_nature_names(config):
    """
    Parses and returns the project's nature names.
    """
    filepath = os.path.join(config['project_dir'], "src/pokemon_summary_screen.c")
    ast = parse_ast_from_file(filepath, config['project_dir'])

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
    filepath = os.path.join(config['project_dir'], "src/pokemon.c")
    ast = parse_ast_from_file(filepath, config['project_dir'])

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
    filepath = os.path.join(config['project_dir'], "src/pokemon.c")
    ast = parse_ast_from_file(filepath, config['project_dir'])

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
    filepath = os.path.join(config['project_dir'], pic_table_file)
    ast = parse_ast_from_file(filepath, config['project_dir'])

    pics = get_declaration_from_ast(ast, pic_table_name)
    if pics == None:
        raise Exception("Failed to read mon pics from %s" % filepath)

    pics_filepath = os.path.join(config['project_dir'], pic_def_file)
    pics_ast = parse_ast_from_file(pics_filepath, config['project_dir'])

    result = {}
    for item in pics.init.exprs:
        if type(item.name[0]) == Constant:
            species = item.name[0].value
            pic_label = item.expr.exprs[0].name
            pic_decl = get_declaration_from_ast(pics_ast, pic_label)
            pic_filepath = pic_decl.init.args.exprs[0].value.strip("\"")
            pic_full_filepath = os.path.join(config['project_dir'], pic_filepath)
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
    filepath = os.path.join(config['project_dir'], "src/pokemon_icon.c")
    ast = parse_ast_from_file(filepath, config['project_dir'])

    icon_pics = get_declaration_from_ast(ast, "gMonIconTable")
    if icon_pics == None:
        raise Exception("Failed to read mon icons pics from %s" % filepath)

    gfx_filepath = os.path.join(config['project_dir'], "src/graphics.c")
    gfx_ast = parse_ast_from_file(gfx_filepath, config['project_dir'])

    result = {}
    for item in icon_pics.init.exprs:
        if type(item.name[0]) == Constant:
            species = item.name[0].value
            icon_label = item.expr.name
            icon_decl = get_declaration_from_ast(gfx_ast, icon_label)
            icon_filepath = icon_decl.init.args.exprs[0].value.strip("\"")
            icon_full_filepath = os.path.join(config['project_dir'], icon_filepath)
            result[species] = icon_full_filepath

    return result
