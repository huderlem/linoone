#--------------------------------------------------------------------
# linoone: parse_code.py
#
# Provides c-file parsing functionality using the pycparser library.
#--------------------------------------------------------------------
import os
import io
from subprocess import check_output

from pycparser.c_ast import Decl
from pycparser.c_parser import CParser


# Parse abstract syntax trees for files. The same C files are often
# required for parsing out project data. The AST will not change, so
# we can cache the resulting ASTs.
ast_cache = {}


def parse_ast_from_file(filepath, project_path):
    """
    Parses an abstract syntax tree from the given C file.
    """
    if filepath in ast_cache:
        return ast_cache[filepath]

    # TODO: There are some issues with the decomp code and pycparser.
    #       Had to make this modifications to decomp source code:
    #       1. In global.h, #define __attribute__(x)
    ast = parse_file(filepath, use_cpp=True, cpp_args=[
        r'-I%s' % os.path.join(project_path, "tools/agbcc/include"),
        r'-I%s' % os.path.join(project_path, "tools/agbcc"),
        r'-I%s' % os.path.join(project_path, "include"),
        r'-I%s' % os.path.join(project_path, "gflib")
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


def parse_declaration_from_file(filepath, declaration_name, project_path):
    """
    Parses a C file and finds the specified external declaration
    from the resulting abstract syntax tree. If it doesn't exist, it
    returns None.
    """
    ast = parse_ast_from_file(filepath, project_path)
    return get_declaration_from_ast(ast, declaration_name)


def parse_names(filepath, declaration_name, project_path):
    """
    Parses and returns an array of names.
    """
    ast = parse_ast_from_file(filepath, project_path)
    arr = get_declaration_from_ast(ast, declaration_name)
    if arr == None:
        raise Exception("Failed to read %s names from %s" % (declaration_name, filepath))

    result = {}
    for item in arr.init.exprs:
        key = item.name[0].value
        name = item.expr.args.exprs[0].value.strip("\"")
        result[key] = name

    return result


# The two functions below are nearly identical implementations
# to pycparser's. They are required to workaround lack of UTF-8
# support in pycparser's implementation.
# See https://github.com/eliben/pycparser/issues/415 for details.
def preprocess_file(filename, cpp_path='cpp', cpp_args=''):
    """ Preprocess a file using cpp.

        filename:
            Name of the file you want to preprocess.

        cpp_path:
        cpp_args:
            Refer to the documentation of parse_file for the meaning of these
            arguments.

        When successful, returns the preprocessed file's contents.
        Errors from cpp will be printed out.
    """
    path_list = [cpp_path]
    if isinstance(cpp_args, list):
        path_list += cpp_args
    elif cpp_args != '':
        path_list += [cpp_args]
    path_list += [filename]

    try:
        # Note the use of universal_newlines to treat all newlines
        # as \n for Python's purpose
        text = check_output(path_list, universal_newlines=True, encoding="utf-8")
    except OSError as e:
        raise RuntimeError("Unable to invoke 'cpp'.  " +
            'Make sure its path was passed correctly\n' +
            ('Original error: %s' % e))

    return text


def parse_file(filename, use_cpp=False, cpp_path='cpp', cpp_args='',
               parser=None):
    """ Parse a C file using pycparser.

        filename:
            Name of the file you want to parse.

        use_cpp:
            Set to True if you want to execute the C pre-processor
            on the file prior to parsing it.

        cpp_path:
            If use_cpp is True, this is the path to 'cpp' on your
            system. If no path is provided, it attempts to just
            execute 'cpp', so it must be in your PATH.

        cpp_args:
            If use_cpp is True, set this to the command line arguments strings
            to cpp. Be careful with quotes - it's best to pass a raw string
            (r'') here. For example:
            r'-I../utils/fake_libc_include'
            If several arguments are required, pass a list of strings.

        parser:
            Optional parser object to be used instead of the default CParser

        When successful, an AST is returned. ParseError can be
        thrown if the file doesn't parse successfully.

        Errors from cpp will be printed out.
    """
    if use_cpp:
        text = preprocess_file(filename, cpp_path, cpp_args)
    else:
        with io.open(filename) as f:
            text = f.read()

    if parser is None:
        parser = CParser()
    return parser.parse(text, filename)
