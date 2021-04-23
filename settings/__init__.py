from .evolution_methods import evolution_methods

def load_project_settings(config):
    """
    Loads the project settings. These are metadata that
    can't be gleaned from source code inspection due to the
    higher-level nature of the data.
    """
    return {
        "evolution_methods": evolution_methods,
    }
