#--------------------------------------------------------------------
# linoone: parse_code.py
#
# Provides c-file parsing functionality using the pycparser library.
#--------------------------------------------------------------------
from pycparser import parse_file
from pycparser.c_ast import Decl


# Parse abstract syntax trees for files. The same C files are often
# required for parsing out project data. The AST will not change, so
# we can cache the resulting ASTs.
ast_cache = {}


def parse_ast_from_file(filepath):
    """
    Parses an abstract syntax tree from the given C file.
    """
    if filepath in ast_cache:
        return ast_cache[filepath]

    # TODO: There are some issues with the decomp code and pycparser.
    #       Had to make these modifications to decomp source code:
    #       1. In global.h, #define __attribute__(x)
    #       2. In global.h, #define TEST_BUTTON(field, button) ((field) & (button))
    ast = parse_file(filepath, use_cpp=True, cpp_args=[
        r'-ID:/cygwin64/home/huder/pokeemerald/tools/agbcc/include',
        r'-ID:/cygwin64/home/huder/pokeemerald/tools/agbcc',
        r'-ID:/cygwin64/home/huder/pokeemerald/include',
        r'-ID:/cygwin64/home/huder/pokeemerald/gflib'
    ])
    ast_cache[filepath] = ast
    return ast


def get_declaration_from_ast(ast, declaration_name):
    """
    Finds and returns the specified external declaration from a C file's
    abstract syntax tree. If it doesn't exist, it returns None.
    """
    return next(
        (item for item in ast.ext if type(item) == Decl and
                                     item.name == declaration_name and
                                     'extern' not in item.storage), None)


def parse_declaration_from_file(filepath, declaration_name):
    """
    Parses a C file and finds the specified external declaration
    from the resulting abstract syntax tree. If it doesn't exist, it
    returns None.
    """
    ast = parse_ast_from_file(filepath)
    return get_declaration_from_ast(ast, declaration_name)


def parse_names(filepath, declaration_name):
    """
    Parses and returns an array of names.
    """
    ast = parse_ast_from_file(filepath)
    arr = get_declaration_from_ast(ast, declaration_name)
    if arr == None:
        raise Exception("Failed to read %s names from %s" % (declaration_name, filepath))

    result = {}
    for item in arr.init.exprs:
        key = item.name[0].value
        name = item.expr.args.exprs[0].value.strip("\"")
        result[key] = name

    return result
