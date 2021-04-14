#--------------------------------------------------------------------
# linoone: pokedex.py
#
# Base artifact generator. Facilitates pages and asset generation.
#--------------------------------------------------------------------
import os

from bs4 import BeautifulSoup as bs

class BaseGenerator:
    """
    Base class that all artifact generators inherit. Child class
    generators should override methods as needed.
    """
    def __init__(self, config, core_data, core_funcs):
        self.config = config
        self.core_data = core_data
        self.core_funcs = core_funcs
        self.custom_data = {}


    def run(self, env):
        """
        Runs the generator to completion.
        """
        generator_data = self.prepare_template_data()
        self.custom_data.update(generator_data)
        self.generate(env)


    def render_template(self, env, template_name, dest_filepath, extra_data={}):
        """
        Renders the final template to the destinatino filepath.
        """
        template = env.get_template(template_name)
        output = template.render(
            **self.config,
            **self.core_funcs,
            **self.core_data,
            **self.custom_data,
            **extra_data
        )
        soup = bs(output, "html.parser")
        prettyHTML = soup.prettify(formatter="html5")
        filepath = os.path.join(self.config["dist_dir"], dest_filepath)
        file_dir = os.path.dirname(os.path.realpath(filepath))
        os.makedirs(file_dir, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prettyHTML)


    def prepare_template_data(self):
        """
        Prepares any additional data the generator needs to render
        itself. Returns a dict of variables and/or functions that will
        be exposed to the template.
        """
        return {}


    def generate(self, env):
        """
        Generates the artifact(s) into the distribution directory.
        """
        pass
