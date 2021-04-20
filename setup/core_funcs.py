#--------------------------------------------------------------------
# linoone: core_funcs.py
#
# Builds the core functions to be used by the templating pipeline.
#--------------------------------------------------------------------
import os
import urllib.parse

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